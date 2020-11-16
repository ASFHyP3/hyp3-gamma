"""Create a Radiometrically Terrain-Corrected (RTC) image from a  Sentinel-1 scene sing GAMMA software"""

import argparse
import glob
import logging
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from math import isclose
from pathlib import Path
from secrets import token_hex
from tempfile import NamedTemporaryFile

from hyp3_metadata import create_metadata_file_set
from hyp3lib import ExecuteError, GranuleError, OrbitDownloadError
from hyp3lib import saa_func_lib as saa
from hyp3lib.area2point import fix_geotiff_locations
from hyp3lib.asf_geometry import reproject2grid
from hyp3lib.byteSigmaScale import byteSigmaScale
from hyp3lib.copy_metadata import copy_metadata
from hyp3lib.createAmp import createAmp
from hyp3lib.execute import execute
from hyp3lib.getDemFor import getDemFile
from hyp3lib.getParameter import getParameter
from hyp3lib.get_bb_from_shape import get_bb_from_shape
from hyp3lib.get_dem import get_dem
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.ingest_S1_granule import ingest_S1_granule
from hyp3lib.makeAsfBrowse import makeAsfBrowse
from hyp3lib.make_cogs import cogify_dir
from hyp3lib.ps2dem import ps2dem
from hyp3lib.raster_boundary2shape import raster_boundary2shape
from hyp3lib.rtc2color import rtc2color
from hyp3lib.system import gamma_version
from hyp3lib.utm2dem import utm2dem
from osgeo import gdal

import hyp3_rtc_gamma
from hyp3_rtc_gamma.check_coreg import CoregistrationError, check_coreg
from hyp3_rtc_gamma.smoothem import smooth_dem_tiles


def fetch_orbit_file(in_file):
    logging.info(f'Fetching orbit file for {in_file}')
    orbit_file = None
    try:
        orbit_file, _ = downloadSentinelOrbitFile(in_file)
    except OrbitDownloadError:
        logging.warning('Unable to fetch orbit file.  Continuing.')
    return orbit_file


def get_product_name(granule_name, orbit_file=None, resolution=30, gamma0=True, power=True,
                     filtered=False, matching=False):
    platform = granule_name[0:3]
    beam_mode = granule_name[4:6]
    polarization = granule_name[14:16]
    datetime = granule_name[17:32]
    res = int(resolution)

    if orbit_file is None:
        o = 'O'
    elif 'POEORB' in orbit_file:
        o = 'P'
    elif 'RESORB' in orbit_file:
        o = 'R'
    else:
        o = 'O'

    product_id = token_hex(2).upper()

    g = 'g' if gamma0 else 's'
    p = 'p' if power else 'a'
    f = 'f' if filtered else 'n'
    m = 'm' if matching else 'd'

    product_name = f'{platform}_{beam_mode}_{datetime}_{polarization}{o}_RTC{res}_G_{g}{p}u{f}e{m}_{product_id}'
    return product_name


def get_polarizations(in_file):
    mapping = {
        'SH': ('HH', None),
        'SV': ('VV', None),
        'DH': ('HH', 'HV'),
        'DV': ('VV', 'VH'),
    }
    key = in_file[14:16]
    polarizations = mapping.get(key)

    if not polarizations:
        raise GranuleError(f'Could not determine polarization(s) from {in_file}')

    return polarizations


def perform_sanity_checks(product_dir):
    logging.info(f"Performing sanity checks on output PRODUCTs in {product_dir}")
    tif_list = glob.glob(f"{product_dir}/*.tif")
    for myfile in tif_list:
        if "VV" in myfile or "HH" in myfile or "VH" in myfile or "HV" in myfile:
            # Check that the main polarization file is on a 30 meter posting
            x, y, trans, proj = saa.read_gdal_file_geo(saa.open_gdal_file(myfile))
            logging.debug("    trans[1] = {}; trans[5] = {}".format(trans[1], trans[5]))
            if abs(trans[5]) > 10 and abs(trans[1]) > 10:
                logging.debug("Checking corner coordinates...")
                ul1 = trans[3]
                lr1 = trans[3] + y * trans[5]
                ul2 = trans[0]
                lr2 = trans[0] + x * trans[1]
                if ul1 % 30 != 0:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: ul1 coordinate not on a 30 meter posting")
                    logging.error("ERROR: ul1 = {}".format(ul1))
                elif lr1 % 30 != 0:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: lr1 coordinate not on a 30 meter posting")
                    logging.error("ERROR: lr1 = {}".format(lr1))
                elif ul2 % 30 != 0:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: ul2 coordinate not on a 30 meter posting")
                    logging.error("ERROR: ul2 = {}".format(ul2))
                elif lr2 % 30 != 0:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: lr2 coordinate not on a 30 meter posting")
                    logging.error("ERROR: lr2 = {}".format(lr2))
                else:
                    logging.debug("...ok")


def reproject_dir(dem_type, res, prod_dir=None):
    if "REMA" in dem_type:
        epsg = 3031
    elif "GIMP" in dem_type:
        epsg = 3413
    else:
        return

    tmp_geotiff = "tmp_reproj_dir_{}.tif".format(os.getpid())
    home = os.getcwd()
    if prod_dir:
        os.chdir(prod_dir)

    for inGeotiff in glob.glob("*.tif"):
        in_raster = gdal.Open(inGeotiff)
        out_raster = reproject2grid(in_raster, epsg, xRes=res)
        in_raster = None  # Because GDAL is weird!
        gdal.Translate(tmp_geotiff, out_raster)
        os.remove(inGeotiff)
        shutil.move(tmp_geotiff, inGeotiff)

    if prod_dir:
        os.chdir(home)


def report_kwargs(in_name, out_name, res, dem, roi, shape, match_flag, dead_flag, gamma_flag,
                  pwr_flag, filter_flag, looks, terms, par, no_cross_pol, smooth, include_scattering_area, orbit_file):
    logging.info("Parameters for this run:")
    logging.info("    Input name                        : {}".format(in_name))
    logging.info("    Output name                       : {}".format(out_name))
    logging.info("    Output resolution                 : {}".format(res))
    logging.info("    DEM file                          : {}".format(dem))
    if roi is not None:
        logging.info("    Area of Interest                  : {}".format(roi))
    if shape is not None:
        logging.info("    Shape File                        : {}".format(shape))
    logging.info("    Match flag                        : {}".format(match_flag))
    logging.info("    If no match, use Dead Reckoning   : {}".format(dead_flag))
    logging.info("    Gamma0 output                     : {}".format(gamma_flag))
    logging.info("    Create power images               : {}".format(pwr_flag))
    logging.info("    Speckle Filtering                 : {}".format(filter_flag))
    logging.info("    Number of looks to take           : {}".format(looks))
    logging.info("    Number of terms in used in match  : {}".format(terms))
    if par is not None:
        logging.info("    Offset file                       : {}".format(par))
    logging.info("    Process crosspol                  : {}".format(not no_cross_pol))
    logging.info("    Smooth DEM tiles                  : {}".format(smooth))
    logging.info("    Include Scattering Area           : {}".format(include_scattering_area))
    logging.info("    Orbit File                        : {}".format(orbit_file))


def process_pol(in_file, rtc_name, out_name, pol, res, look_fact, match_flag, dead_flag, gamma_flag,
                filter_flag, pwr_flag, browse_res, dem, terms, par=None, orbit_file=None):
    logging.info(f'Processing the {pol} polarization')

    mgrd = "{out}.{pol}.mgrd".format(out=out_name, pol=pol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(in_file, pol, look_fact, mgrd, orbit_file=orbit_file)
    width = getParameter("{}.par".format(mgrd), "range_samples")

    # Apply filter if requested
    if filter_flag:
        el_looks = look_fact * 30
        execute(f"enh_lee {mgrd} temp.mgrd {width} {el_looks} 1 7 7", uselogging=True)
        shutil.move("temp.mgrd", mgrd)

    options = "-p -n {} -q -c ".format(terms)
    if gamma_flag:
        options += "-g "

    logging.info("Running RTC process... initializing")
    geo_dir = "geo_{}".format(pol)
    execute(f"mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {geo_dir}/area.dem"
            f" {geo_dir}/area.dem_par {geo_dir} image {res} 0 {options}", uselogging=True)

    if match_flag and not par:
        fail = False
        logging.info("Running RTC process... coarse matching")
        try:
            execute(f"mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {geo_dir}/area.dem"
                    f" {geo_dir}/area.dem_par {geo_dir} image {res} 1 {options}", uselogging=True)
        except ExecuteError:
            logging.warning("WARNING: Determination of the initial offset failed, skipping initial offset")

        logging.info("Running RTC process... fine matching")
        try:
            execute(f"mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {geo_dir}/area.dem"
                    f" {geo_dir}/area.dem_par {geo_dir} image {res} 2 {options}", uselogging=True)
        except ExecuteError:
            if not dead_flag:
                logging.error("ERROR: Failed to match images")
                sys.exit(1)
            else:
                logging.warning("WARNING: Coregistration has failed; defaulting to dead reckoning")
                os.remove("{}/{}".format(geo_dir, "image.diff_par"))
                fail = True

        if not fail:
            try:
                check_coreg(out_name, res, max_offset=75, max_error=2.0)
            except CoregistrationError:
                if not dead_flag:
                    logging.error("ERROR: Failed the coregistration check")
                    sys.exit(1)
                else:
                    logging.warning("WARNING: Coregistration check has failed; defaulting to dead reckoning")
                    os.remove("{}/{}".format(geo_dir, "image.diff_par"))

    logging.info("Running RTC process... finalizing")
    if par:
        shutil.copy(par, "{}/image.diff_par".format(geo_dir))
    execute(f"mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {geo_dir}/area.dem"
            f" {geo_dir}/area.dem_par {geo_dir} image {res} 3 {options}", uselogging=True)

    os.chdir(geo_dir)

    # Make Geotiff Files
    execute(f"data2geotiff area.dem_par image_0.ls_map 5 {out_name}.ls_map.tif", uselogging=True)
    execute(f"data2geotiff area.dem_par image_0.inc_map 2 {out_name}.inc_map.tif", uselogging=True)
    execute("data2geotiff area.dem_par area.dem 2 outdem.tif", uselogging=True)

    gdal.Translate("{}.dem.tif".format(out_name), "outdem.tif", outputType=gdal.GDT_Int16)

    if gamma_flag:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_gamma0'.format(pol)])
    else:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_sigma0'.format(pol)])
    shutil.move("tmp.tif", tif)
    createAmp(tif, nodata=0)

    # Make browse resolution tif file
    if res == browse_res:
        shutil.copy("image_cal_map.mli_amp.tif", "{}_{}_{}m.tif".format(out_name, pol, browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(out_name, pol, browse_res), "image_cal_map.mli_amp.tif",
                       xRes=browse_res, yRes=browse_res)

    # Move files into the product directory
    out_dir = "../PRODUCT"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if pwr_flag:
        shutil.move(tif, "{}/{}".format(out_dir, rtc_name))
    else:
        copy_metadata(tif, "image_cal_map.mli_amp.tif")
        shutil.move("image_cal_map.mli_amp.tif", "{}/{}".format(out_dir, rtc_name))

    shutil.move("{}.ls_map.tif".format(out_name), "{}/{}_ls_map.tif".format(out_dir, out_name))
    shutil.move("{}.inc_map.tif".format(out_name), "{}/{}_inc_map.tif".format(out_dir, out_name))
    shutil.move("{}.dem.tif".format(out_name), "{}/{}_dem.tif".format(out_dir, out_name))

    os.chdir("..")


def process_2nd_pol(in_file, rtc_name, cpol, res, look_fact, gamma_flag, filter_flag, pwr_flag, browse_res,
                    outfile, dem, terms, par=None, orbit_file=None):
    logging.info(f'Processing the {cpol} polarization')
    if cpol == "VH":
        mpol = "VV"
    else:
        mpol = "HH"

    mgrd = "{out}.{pol}.mgrd".format(out=outfile, pol=cpol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(in_file, cpol, look_fact, mgrd, orbit_file=orbit_file)
    width = getParameter("{}.par".format(mgrd), "range_samples")

    # Apply filtering if requested
    if filter_flag:
        el_looks = look_fact * 30
        execute(f"enh_lee {mgrd} temp.mgrd {width} {el_looks} 1 7 7", uselogging=True)
        shutil.move("temp.mgrd", mgrd)

    options = "-p -n {} -q -c ".format(terms)
    if gamma_flag:
        options += "-g "

    home_dir = os.getcwd()
    geo_dir = "geo_{}".format(cpol)
    mdir = "geo_{}".format(mpol)
    if not os.path.isdir(geo_dir):
        os.mkdir(geo_dir)

    shutil.copy("geo_{}/image.diff_par".format(mpol), "{}".format(geo_dir))
    os.symlink("../geo_{}/image_0.map_to_rdc".format(mpol), "{}/image_0.map_to_rdc".format(geo_dir))
    os.symlink("../geo_{}/image_0.ls_map".format(mpol), "{}/image_0.ls_map".format(geo_dir))
    os.symlink("../geo_{}/image_0.inc_map".format(mpol), "{}/image_0.inc_map".format(geo_dir))
    os.symlink("../geo_{}/image_0.sim".format(mpol), "{}/image_0.sim".format(geo_dir))
    os.symlink("../geo_{}/area.dem_par".format(mpol), "{}/area.dem_par".format(geo_dir))

    if par:
        shutil.copy(par, "{}/image.diff_par".format(geo_dir))

    execute(f"mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {mdir}/area.dem"
            f" {mdir}/area.dem_par {geo_dir} image {res} 3 {options}", uselogging=True)

    os.chdir(geo_dir)

    # Make geotiff file
    if gamma_flag:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_gamma0'.format(cpol)])
    else:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_sigma0'.format(cpol)])
    shutil.move("tmp.tif", tif)

    # Make browse resolution file
    createAmp(tif, nodata=0)
    if res == browse_res:
        shutil.copy("image_cal_map.mli_amp.tif", "{}_{}_{}m.tif".format(outfile, cpol, browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(outfile, cpol, browse_res), "image_cal_map.mli_amp.tif", xRes=browse_res,
                       yRes=browse_res)

    # Move files to product directory
    out_dir = "../PRODUCT"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if pwr_flag:
        shutil.move(tif, "{}/{}".format(out_dir, rtc_name))
    else:
        copy_metadata(tif, "image_cal_map.mli_amp.tif")
        shutil.move("image_cal_map.mli_amp.tif", "{}/{}".format(out_dir, rtc_name))

    os.chdir(home_dir)


def create_area_geotiff(data_in, lookup_table, mli_par, dem_par, output_name):
    logging.info(f'Creating scattering area geotiff: {output_name}')
    width_in = getParameter(mli_par, 'range_samples')
    width_out = getParameter(dem_par, 'width')
    nlines_out = getParameter(dem_par, 'nlines')

    with NamedTemporaryFile() as temp_file:
        execute(f'geocode_back {data_in} {width_in} {lookup_table} {temp_file.name} {width_out} {nlines_out} 2',
                uselogging=True)
        execute(f'data2geotiff {dem_par} {temp_file.name} 2 {output_name}', uselogging=True)


def create_browse_images(out_name, pol, cpol, browse_res):
    out_dir = 'PRODUCT'
    pol_amp_tif = f'geo_{pol}/{out_name}_{pol}_{browse_res}m.tif'

    if cpol:
        cpol_amp_tif = f'geo_{cpol}/{out_name}_{cpol}_{browse_res}m.tif'
        threshold = -24
        outfile = f'{out_dir}/{out_name}_rgb'
        with NamedTemporaryFile() as rgb_tif:
            rtc2color(pol_amp_tif, cpol_amp_tif, threshold, rgb_tif.name, amp=True, cleanup=True)
            makeAsfBrowse(rgb_tif.name, outfile)

    outfile = f'{out_dir}/{out_name}'
    with NamedTemporaryFile() as rescaled_tif:
        byteSigmaScale(pol_amp_tif, rescaled_tif.name)
        makeAsfBrowse(rescaled_tif.name, outfile)

    for file_type in ['inc_map', 'dem', 'area']:
        tif = f'{out_dir}/{out_name}_{file_type}.tif'
        if os.path.exists(tif):
            outfile = f'{out_dir}/{out_name}_{file_type}'
            with NamedTemporaryFile() as rescaled_tif:
                byteSigmaScale(tif, rescaled_tif.name)
                makeAsfBrowse(rescaled_tif.name, outfile)

    pol_tif = f'{out_dir}/{out_name}_{pol}.tif'
    shapefile = f'{out_dir}/{out_name}_shape.shp'
    raster_boundary2shape(pol_tif, None, shapefile, use_closing=False, pixel_shift=True, fill_holes=True)


def create_consolidated_log(logname, out_name, dead_flag, match_flag, gamma_flag, roi,
                            shape, pwr_flag, filter_flag, pol, looks, log_file, smooth, terms,
                            no_cross_pol, par):
    logging.info("Creating log file: {}".format(logname))

    f = open(logname, "w")
    f.write("Consolidated log for: {}\n".format(out_name))
    options = ""
    if not dead_flag:
        options += "--fail "
    if match_flag:
        options += "-n "
    if not gamma_flag:
        options += "--sigma "
    if filter_flag:
        options += "-f "
    if not pwr_flag:
        options += "--amp "
    if smooth:
        options += "--smooth "
    options += "-k {}".format(looks)
    options += "-t {}".format(terms)
    if par:
        options += "--par {}".format(par)
    if no_cross_pol:
        options += "--nocrosspol"
    if roi:
        options += "-a {}".format(roi)
    if shape:
        options += "-s {}".format(shape)

    cmd = "rtc_sentinel.py " + options
    f.write("Command: {}\n".format(cmd))
    f.close()

    geo_dir = "geo_{}".format(pol)
    add_log(log_file, logname)
    add_log("{}/mk_geo_radcal_0.log".format(geo_dir), logname)
    add_log("{}/mk_geo_radcal_1.log".format(geo_dir), logname)
    add_log("{}/mk_geo_radcal_2.log".format(geo_dir), logname)
    add_log("{}/mk_geo_radcal_3.log".format(geo_dir), logname)
    add_log("coreg_check.log", logname)


def add_log(log, full_log):
    g = open(full_log, "a")
    g.write("==============================================\n")
    g.write("Log: {}\n".format(log))
    g.write("==============================================\n")

    if not os.path.isfile(log):
        g.write("(not found)\n")
        g.close()
        return ()

    f = open(log, "r")
    for line in f:
        g.write("{}".format(line))
    f.close()

    g.write("\n")
    g.close()


def clean_prod_dir(product_dir):
    for pattern in ['*inc_map*png*', '*inc_map*kmz', '*dem*png*', '*dem*kmz', '*area*png*', '*area*kmz']:
        for myfile in glob.glob(f'{product_dir}/{pattern}'):
            os.remove(myfile)


def configure_log_file():
    log_file = f'rtc_sentinel_{os.getpid()}.log'
    log_file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    log_file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(log_file_handler)
    return log_file


def rtc_sentinel_gamma(in_file,
                       out_name=None,
                       res=30.0,
                       dem=None,
                       roi=None,
                       shape=None,
                       match_flag=False,
                       dead_flag=True,
                       gamma_flag=True,
                       pwr_flag=True,
                       filter_flag=False,
                       looks=None,
                       terms=1,
                       par=None,
                       no_cross_pol=False,
                       smooth=False,
                       include_scattering_area=False):

    log_file = configure_log_file()

    logging.info("===================================================================")
    logging.info("                Sentinel RTC Program - Starting")
    logging.info("===================================================================")

    browse_res = 30
    if res > browse_res:
        browse_res = res

    if looks is None:
        if isclose(res, 30.0):
            if "GRD" in in_file:
                looks = 6
            else:
                looks = 3
        else:
            looks = int(res / 10 + 0.5)

    in_file = in_file.rstrip('/')
    if not os.path.exists(in_file):
        logging.error("ERROR: Input file {} does not exist".format(in_file))
        sys.exit(1)
    if in_file.endswith('.zip'):
        logging.info(f'Unzipping {in_file}')
        with zipfile.ZipFile(in_file, 'r') as z:
            z.extractall()
        in_file = in_file.replace('.zip', '.SAFE')

    orbit_file = fetch_orbit_file(in_file)

    if out_name is None:
        out_name = get_product_name(in_file, orbit_file, res, gamma_flag, pwr_flag, filter_flag, match_flag)

    report_kwargs(in_file, out_name, res, dem, roi, shape, match_flag, dead_flag, gamma_flag,
                  pwr_flag, filter_flag, looks, terms, par, no_cross_pol, smooth, include_scattering_area, orbit_file)

    orbit_file = os.path.abspath(orbit_file)  # ingest_S1_granule requires absolute path

    if dem is None:
        logging.info("Getting DEM file covering this SAR image")
        tifdem = "tmp_{}_dem.tif".format(os.getpid())
        if shape is not None:
            min_x, min_y, max_x, max_y = get_bb_from_shape(shape)
            logging.info(f'bounding box: {min_x}, {min_y}, {max_x}, {max_y}')
            roi = [min_x, min_y, max_x, max_y]
        if roi is not None:
            dem_type = get_dem(roi[0], roi[1], roi[2], roi[3], tifdem, post=30)
        else:
            demfile, dem_type = getDemFile(in_file, tifdem, post=30)

        if 'REMA' in dem_type and smooth:
            logging.info("Preparing to smooth DEM tiles")
            dem, parfile = smooth_dem_tiles("DEM", build=True)
        else:
            dem = "area.dem"
            parfile = "area.dem.par"
            if "GIMP" in dem_type or "REMA" in dem_type:
                ps2dem(tifdem, dem, parfile)
            else:
                utm2dem(tifdem, dem, parfile)
            os.remove(tifdem)
    elif ".tif" in dem:
        tiff_dem = dem
        dem = "area.dem"
        parfile = "area.dem.par"
        utm2dem(tiff_dem, dem, parfile)
        dem_type = "Unknown"
    elif os.path.isfile("{}.par".format(dem)):
        dem_type = "Unknown"
    else:
        logging.error("ERROR: Unrecognized DEM: {}".format(dem))
        sys.exit(1)

    pol, cpol = get_polarizations(in_file)
    if no_cross_pol:
        cpol = None

    rtc_name = f'{out_name}_{pol}.tif'
    process_pol(in_file, rtc_name, out_name, pol, res, looks,
                match_flag, dead_flag, gamma_flag, filter_flag, pwr_flag,
                browse_res, dem, terms, par=par, orbit_file=orbit_file)

    if include_scattering_area:
        create_area_geotiff(f'geo_{pol}/image_1.pix', f'geo_{pol}/image_1.map_to_rdc', f'{out_name}.{pol}.mgrd.par',
                            f'geo_{pol}/{dem}_par', f'PRODUCT/{out_name}_area.tif')

    if cpol:
        rtc_name = f'{out_name}_{cpol}.tif'
        process_2nd_pol(in_file, rtc_name, cpol, res, looks,
                        gamma_flag, filter_flag, pwr_flag, browse_res,
                        out_name, dem, terms, par=par, orbit_file=orbit_file)

    fix_geotiff_locations()
    reproject_dir(dem_type, res, prod_dir="PRODUCT")
    reproject_dir(dem_type, res, prod_dir="geo_{}".format(pol))
    if cpol:
        reproject_dir(dem_type, res, prod_dir="geo_{}".format(cpol))
    create_browse_images(out_name, pol, cpol, browse_res)

    logging.info(f'Renaming PRODUCT directory to {out_name}')
    os.rename('PRODUCT', out_name)

    cogify_dir(directory=out_name)
    create_metadata_file_set(
        product_dir=Path(out_name),
        granule_name=in_file.replace('.SAFE', ''),
        dem_name=dem_type,
        processing_date=datetime.now(timezone.utc),
        looks=looks,
        plugin_name=hyp3_rtc_gamma.__name__,
        plugin_version=hyp3_rtc_gamma.__version__,
        processor_name='GAMMA',
        processor_version=gamma_version(),
    )
    clean_prod_dir(out_name)
    perform_sanity_checks(out_name)

    logging.info("===================================================================")
    logging.info("               Sentinel RTC Program - Completed")
    logging.info("===================================================================")

    create_consolidated_log(f'{out_name}/{out_name}.log', out_name, dead_flag, match_flag, gamma_flag, roi,
                            shape, pwr_flag, filter_flag, pol, looks, log_file, smooth, terms,
                            no_cross_pol, par)
    return out_name


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='rtc_sentinel.py',
        description=__doc__,
    )
    parser.add_argument('input', help='Name of input file, either .zip or .SAFE')
    parser.add_argument("-o", "--outputResolution", type=float, default=30.0, help="Desired output resolution")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--externalDEM", help="Specify a DEM file to use - must be in UTM projection")
    group.add_argument("-r", "--roi", type=float, nargs=4, metavar=('LON_MIN', 'LAT_MIN', 'LON_MAX', 'LAT_MAX'),
                       help="Specify ROI to use")
    group.add_argument("-s", "--shape", help="Specify shape file to use")

    parser.add_argument("-n", action="store_false", help="Do not perform matching")
    parser.add_argument("--fail", action="store_true",
                        help="if matching fails, fail the program. Default: use dead reckoning")
    parser.add_argument("--sigma", action="store_true", help="create sigma0 instead of gamma0")
    parser.add_argument("--amp", action="store_true", help="create amplitude images instead of power")
    parser.add_argument("--smooth", action="store_true", help="smooth DEM file before terrain correction")
    parser.add_argument("-f", action="store_true", help="run enhanced lee filter")
    parser.add_argument("-k", "--looks", type=int,
                        help="set the number of looks to take (def:3 for SLC/6 for GRD)")
    parser.add_argument("-t", "--terms", type=int, default=1,
                        help="set the number of terms in matching polynomial (default is 1)")
    parser.add_argument('--output', help='base name of the output files')
    parser.add_argument("--par", help="Stack processing - use specified offset file and don't match")
    parser.add_argument("--nocrosspol", action="store_true", help="Do not process the cross pol image")
    parser.add_argument("-a", "--include-scattering-area", action="store_true",
                        help="Include a geotiff of scattering area in the output package")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    # FIXME: This function's inputs should be 1:1 (name and value!) with CLI args!
    rtc_sentinel_gamma(args.input,
                       out_name=args.output,
                       res=args.outputResolution,
                       dem=args.externalDEM,
                       roi=args.roi,
                       shape=args.shape,
                       match_flag=args.n,
                       dead_flag=not args.fail,
                       gamma_flag=not args.sigma,
                       pwr_flag=not args.amp,
                       filter_flag=args.f,
                       looks=args.looks,
                       terms=args.terms,
                       par=args.par,
                       no_cross_pol=args.nocrosspol,
                       smooth=args.smooth,
                       include_scattering_area=args.include_scattering_area)


if __name__ == "__main__":
    main()
