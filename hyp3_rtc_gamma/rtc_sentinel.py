"""Create a Radiometrically Terrain-Corrected (RTC) image from a  Sentinel-1 scene sing GAMMA software"""

import argparse
import glob
import logging
import os
import shutil
import sys
import zipfile

from hyp3lib import ExecuteError
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
from hyp3_rtc_gamma.create_metadata import create_arc_xml
from hyp3_rtc_gamma.metadata_utils import write_asf_meta
from hyp3_rtc_gamma.smoothem import smooth_dem_tiles
from hyp3_rtc_gamma.xml2meta import sentinel2meta


def get_product_name(granule_name, resolution=30, gamma0=True, power=True, filtered=False):
    platform = granule_name[0:3]
    beam_mode = granule_name[4:6]
    datetime = granule_name[17:32]
    g = 'g' if gamma0 else 's'
    p = 'p' if power else 'a'
    f = 'f' if filtered else 'n'

    product_name = f'{platform}_{beam_mode}_RT{resolution}_{datetime}_G_{g}{p}{f}'
    return product_name


def perform_sanity_checks():
    logging.info("Performing sanity checks on output PRODUCTs")
    tif_list = glob.glob("PRODUCT/*.tif")
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


def report_kwargs(in_name, out_name, res, dem, roi, shape, match_flag, dead_flag, gamma_flag, lo_flag,
                  pwr_flag, filter_flag, looks, terms, par, no_cross_pol, smooth, area):
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
    logging.info("    Low resolution flag               : {}".format(lo_flag))
    logging.info("    Create power images               : {}".format(pwr_flag))
    logging.info("    Speckle Filtering                 : {}".format(filter_flag))
    logging.info("    Number of looks to take           : {}".format(looks))
    logging.info("    Number of terms in used in match  : {}".format(terms))
    if par is not None:
        logging.info("    Offset file                       : {}".format(par))
    logging.info("    Process crosspol                  : {}".format(not no_cross_pol))
    logging.info("    Smooth DEM tiles                  : {}".format(smooth))
    logging.info("    Save Pixel Area                   : {}".format(area))


def process_pol(in_file, rtc_name, out_name, pol, res, look_fact, match_flag, dead_flag, gamma_flag,
                filter_flag, pwr_flag, browse_res, dem, terms, par=None, area=False):
    logging.info("Processing the {} polarization".format(pol))

    mgrd = "{out}.{pol}.mgrd".format(out=out_name, pol=pol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(in_file, pol, look_fact, mgrd)
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

    # Divide sigma0 by sin(theta) to get beta0
    execute(f"float_math image_0.inc_map - image_1.sin_theta {width} 7 - - 1 1 - 0")

    execute(f"float_math image_cal_map.mli image_1.sin_theta image_1.beta {width} 3 - - 1 1 - 0")

    execute(f"float_math image_1.beta image_0.sim image_1.flat {width} 3 - - 1 1 - 0")

    # Make Geotiff Files
    execute(f"data2geotiff area.dem_par image_0.ls_map 5 {out_name}.ls_map.tif", uselogging=True)
    execute(f"data2geotiff area.dem_par image_0.inc_map 2 {out_name}.inc_map.tif", uselogging=True)
    execute(f"data2geotiff area.dem_par image_1.flat 2 {out_name}.flat.tif", uselogging=True)
    execute("data2geotiff area.dem_par area.dem 2 outdem.tif", uselogging=True)

    gdal.Translate("{}.dem.tif".format(out_name), "outdem.tif", outputType=gdal.GDT_Int16)

    if gamma_flag:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_gamma0'.format(pol)])
    else:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_sigma0'.format(pol)])
    shutil.move("tmp.tif", tif)
    createAmp(tif, nodata=0)

    # Make meta files and stats
    execute(f"asf_import -format geotiff {out_name}.ls_map.tif ls_map", uselogging=True)
    execute("stats -overstat -overmeta ls_map", uselogging=True)
    execute(f"asf_import -format geotiff {out_name}.inc_map.tif inc_map", uselogging=True)
    execute("stats -overstat -overmeta -mask 0 inc_map", uselogging=True)
    execute(f"asf_import -format geotiff image_cal_map.mli_amp.tif tc_{pol}", uselogging=True)
    execute(f"stats -nostat -overmeta -mask 0 tc_{pol}", uselogging=True)

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
    shutil.copy("image.diff_par", "{}/{}_diff.par".format(out_dir, out_name))
    if area:
        shutil.move("{}.flat.tif".format(out_name), "{}/{}_flat_{}.tif".format(out_dir, out_name, pol))

    os.chdir("..")


def process_2nd_pol(in_file, rtc_name, cpol, res, look_fact, gamma_flag, filter_flag, pwr_flag, browse_res,
                    outfile, dem, terms, par=None, area=False):
    if cpol == "VH":
        mpol = "VV"
    else:
        mpol = "HH"

    mgrd = "{out}.{pol}.mgrd".format(out=outfile, pol=cpol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(in_file, cpol, look_fact, mgrd)
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

    # Divide sigma0 by sin(theta) to get beta0
    execute(f"float_math image_0.inc_map - image_1.sin_theta {width} 7 - - 1 1 - 0")

    execute(f"float_math image_cal_map.mli image_1.sin_theta image_1.beta {width} 3 - - 1 1 - 0")

    execute(f"float_math image_1.beta image_0.sim image_1.flat {width} 3 - - 1 1 - 0")

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

    # Create meta files and stats
    execute(f"asf_import -format geotiff image_cal_map.mli_amp.tif tc_{cpol}", uselogging=True)
    execute(f"stats -nostat -overmeta -mask 0 tc_{cpol}", uselogging=True)

    # Move files to product directory
    out_dir = "../PRODUCT"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    execute(f"data2geotiff area.dem_par image_1.flat 2 {outfile}.flat.tif", uselogging=True)

    if pwr_flag:
        shutil.move(tif, "{}/{}".format(out_dir, rtc_name))
    else:
        copy_metadata(tif, "image_cal_map.mli_amp.tif")
        shutil.move("image_cal_map.mli_amp.tif", "{}/{}".format(out_dir, rtc_name))
    if area:
        shutil.move("{}.flat.tif".format(outfile), "{}/{}_flat_{}.tif".format(out_dir, rtc_name, cpol))

    os.chdir(home_dir)


def create_browse_images(out_name, pol, cpol, browse_res):
    ampfile = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=pol, name=out_name, res=browse_res)
    if cpol:
        ampfile2 = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=cpol, name=out_name, res=browse_res)
        threshold = -24
        outfile = "{}_rgb.tif".format(out_name)
        rtc2color(ampfile, ampfile2, threshold, outfile, amp=True, cleanup=True)
        colorname = "PRODUCT/{}_rgb".format(out_name)
        makeAsfBrowse(outfile, colorname)

    os.chdir("geo_{}".format(pol))
    outdir = "../PRODUCT"
    outfile = "{}/{}".format(outdir, out_name)
    ampfile = "{name}_{pol}_{res}m.tif".format(pol=pol, name=out_name, res=browse_res)
    sigmafile = ampfile.replace(".tif", "_sigma.tif")
    byteSigmaScale(ampfile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)

    os.chdir("../PRODUCT")

    infile = "{}_inc_map.tif".format(out_name)
    outfile = "{}_inc_map".format(out_name)
    sigmafile = infile.replace(".tif", "_sigma.tif")
    byteSigmaScale(infile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)
    os.remove(sigmafile)

    infile = "{}_ls_map.tif".format(out_name)
    outfile = "{}_ls_map".format(out_name)
    makeAsfBrowse(infile, outfile)

    infile = "{}_dem.tif".format(out_name)
    outfile = "{}_dem".format(out_name)
    sigmafile = infile.replace(".tif", "_sigma.tif")
    byteSigmaScale(infile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)
    os.remove(sigmafile)

    raster_boundary2shape(out_name + "_" + pol + ".tif", None, out_name + "_shape.shp", use_closing=False,
                          pixel_shift=True, fill_holes=True)

    os.chdir("..")


def create_consolidated_log(out_name, lo_flag, dead_flag, match_flag, gamma_flag, roi,
                            shape, pwr_flag, filter_flag, pol, looks, log_file, smooth, terms,
                            no_cross_pol, par):
    out = "PRODUCT"
    logname = "{}/{}.log".format(out, out_name)
    logging.info("Creating log file: {}".format(logname))

    f = open(logname, "w")
    f.write("Consolidated log for: {}\n".format(out_name))
    options = ""
    if lo_flag:
        options += "-l "
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


def create_iso_xml(outfile, out_name, pol, cpol, in_file, dem_type, log, gamma_ver):
    hdf5_name = "hdf5_list.txt"
    path = in_file
    etc_dir = os.path.abspath(os.path.dirname(hyp3_rtc_gamma.etc.__file__))
    shutil.copy("{}/sentinel_xml.xsl".format(etc_dir), "sentinel_xml.xsl")

    out = "PRODUCT"

    execute(f"xsltproc --stringparam path {path} --stringparam timestamp timestring"
            f" --stringparam file_size 1000 --stringparam server stuff"
            f" --output out.xml sentinel_xml.xsl {path}/manifest.safe", uselogging=True)

    m = sentinel2meta("out.xml")
    write_asf_meta(m, "out.meta")

    ver_file = "{}/manifest.safe".format(path)
    ipf_ver = None
    if os.path.exists(ver_file):
        f = open(ver_file, "r")
        for line in f:
            if "IPF" in line:
                t = line.split('"')
                ipf_ver = t[3].strip()
    else:
        logging.warning("No manifest.safe file found in {}".format(path))

    g = open(hdf5_name, "w")
    g.write("[GAMMA RTC]\n")
    g.write("granule = {}\n".format(in_file.replace(".SAFE", "")))
    g.write("metadata = out.meta\n")

    geo_dir = "geo_{}".format(pol)
    dem_seg = "{}/area.dem".format(geo_dir)
    dem_seg_par = "{}/area.dem_par".format(geo_dir)

    g.write("oversampled dem file = {}\n".format(dem_seg))
    g.write("oversampled dem metadata = {}\n".format(dem_seg_par))
    g.write("original dem file = {}/{}_dem.tif\n".format(out, out_name))
    g.write("layover shadow mask = {}/{}_ls_map.tif\n".format(out, out_name))
    g.write("layover shadow stats = {}/ls_map.stat\n".format(geo_dir))
    g.write("incidence angle file = {}/{}_inc_map.tif\n".format(out, out_name))
    g.write("incidence angle metadata = {}/inc_map.meta\n".format(geo_dir))

    g.write("input {} file = {}\n".format(pol, outfile))
    g.write("terrain corrected {pol} metadata = {dir}/tc_{pol}.meta\n".format(pol=pol, dir=geo_dir))
    g.write("terrain corrected {} file = {}/{}\n".format(pol, out, outfile))

    if cpol:
        outfile2 = outfile.replace(pol, cpol)
        g.write("input {} file = {}\n".format(pol, outfile))
        geo_dir2 = geo_dir.replace(pol, cpol)
        g.write("terrain corrected {pol} metadata = {dir}/tc_{pol}.meta\n".format(pol=cpol, dir=geo_dir2))
        g.write("terrain corrected {} file = {}/{}\n".format(cpol, out, outfile2))

    g.write("initial processing log = {}\n".format(log))
    g.write("terrain correction log = {}\n".format(log))
    g.write("main log = {}\n".format(log))
    g.write("mk_geo_radcal_0 log = {}/mk_geo_radcal_0.log\n".format(geo_dir))
    g.write("mk_geo_radcal_1 log = {}/mk_geo_radcal_1.log\n".format(geo_dir))
    g.write("mk_geo_radcal_2 log = {}/mk_geo_radcal_2.log\n".format(geo_dir))
    g.write("mk_geo_radcal_3 log = {}/mk_geo_radcal_3.log\n".format(geo_dir))
    g.write("coreg_check log = coreg_check.log\n")
    g.write("mli.par file = {}.{}.mgrd.par\n".format(out_name, pol))
    g.write("gamma version = {}\n".format(gamma_ver))
    g.write("hyp3_rtc version = {}\n".format(hyp3_rtc_gamma.__version__))
    g.write("ipf version = {}\n".format(ipf_ver))
    g.write("dem source = {}\n".format(dem_type))
    g.write("browse image = {}/{}.png\n".format(out, out_name))
    g.write("kml overlay = {}/{}.kmz\n".format(out, out_name))

    g.close()

    execute(f"write_hdf5_xml {hdf5_name} {out_name}.xml", uselogging=True)

    logging.info("Generating {}.iso.xml with {}/rtc_iso.xsl\n".format(out_name, etc_dir))

    execute(f"xsltproc {etc_dir}/rtc_iso.xsl {out_name}.xml > {out_name}.iso.xml", uselogging=True)

    shutil.copy("{}.iso.xml".format(out_name), "{}".format(out))


def clean_prod_dir():
    os.chdir("PRODUCT")
    for myfile in glob.glob("*ls_map*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*ls_map*kmz"):
        os.remove(myfile)
    for myfile in glob.glob("*inc_map*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*inc_map*kmz"):
        os.remove(myfile)
    for myfile in glob.glob("*dem*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*dem*kmz"):
        os.remove(myfile)
    os.chdir("..")


def rtc_sentinel_gamma(in_file,
                       out_name=None,
                       res=None,
                       dem=None,
                       roi=None,
                       shape=None,
                       match_flag=False,
                       dead_flag=True,
                       gamma_flag=True,
                       lo_flag=True,
                       pwr_flag=True,
                       filter_flag=False,
                       looks=None,
                       terms=1,
                       par=None,
                       no_cross_pol=False,
                       smooth=False,
                       area=False):

    log_file = "{}_{}_log.txt".format(in_file.rpartition('.')[0], os.getpid())
    logging.basicConfig(filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    logging.info("===================================================================")
    logging.info("                Sentinel RTC Program - Starting")
    logging.info("===================================================================")

    logging.info("Area flag is {}".format(area))

    if res is None:
        res = 10
    if lo_flag:
        res = 30

    browse_res = 30
    if res > browse_res:
        browse_res = res

    if looks is None:
        if res == 30:
            if "GRD" in in_file:
                looks = 6
            else:
                looks = 3
        else:
            looks = int(res / 10 + 0.5)
        logging.info("Setting looks to {}".format(looks))

    # get rid of ending "/"
    if in_file.endswith("/"):
        in_file = in_file[0:len(in_file) - 1]

    if not os.path.exists(in_file):
        logging.error("ERROR: Input file {} does not exist".format(in_file))
        sys.exit(1)
    if "zip" in in_file:
        zip_ref = zipfile.ZipFile(in_file, 'r')
        zip_ref.extractall(".")
        zip_ref.close()
        in_file = in_file.replace(".zip", ".SAFE")

    input_type = in_file[7:11]
    if 'SLC' in input_type:
        input_type = 'SLC'
    else:
        input_type = 'GRD'

    if out_name is None:
        out_name = get_product_name(in_file, res, gamma_flag, pwr_flag, filter_flag)

    report_kwargs(in_file, out_name, res, dem, roi, shape, match_flag, dead_flag, gamma_flag, lo_flag,
                  pwr_flag, filter_flag, looks, terms, par, no_cross_pol, smooth, area)

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

    vvlist = glob.glob("{}/*/*vv*.tiff".format(in_file))
    vhlist = glob.glob("{}/*/*vh*.tiff".format(in_file))
    hhlist = glob.glob("{}/*/*hh*.tiff".format(in_file))
    hvlist = glob.glob("{}/*/*hv*.tiff".format(in_file))

    cpol = None
    pol = None
    if vvlist:
        logging.info("Found VV polarization - processing")
        pol = "VV"
        rtc_name = out_name + "_" + pol + ".tif"
        process_pol(in_file, rtc_name, out_name, pol, res, looks,
                    match_flag, dead_flag, gamma_flag, filter_flag, pwr_flag,
                    browse_res, dem, terms, par=par, area=area)

        if vhlist and not no_cross_pol:
            cpol = "VH"
            rtc_name = out_name + "_" + cpol + ".tif"
            logging.info("Found VH polarization - processing")
            process_2nd_pol(in_file, rtc_name, cpol, res, looks,
                            gamma_flag, filter_flag, pwr_flag, browse_res,
                            out_name, dem, terms, par=par, area=area)

    if hhlist:
        logging.info("Found HH polarization - processing")
        pol = "HH"
        rtc_name = out_name + "_" + pol + ".tif"
        process_pol(in_file, rtc_name, out_name, pol, res, looks,
                    match_flag, dead_flag, gamma_flag, filter_flag, pwr_flag,
                    browse_res, dem, terms, par=par, area=area)

        if hvlist and not no_cross_pol:
            cpol = "HV"
            logging.info("Found HV polarization - processing")
            rtc_name = out_name + "_" + cpol + ".tif"
            process_2nd_pol(in_file, rtc_name, cpol, res, looks,
                            gamma_flag, filter_flag, pwr_flag, browse_res,
                            out_name, dem, terms, par=par, area=area)

    if hhlist is None and vvlist is None:
        logging.error(f"ERROR: Can not find VV or HH polarization in {in_file}")
        sys.exit(1)

    fix_geotiff_locations()
    reproject_dir(dem_type, res, prod_dir="PRODUCT")
    reproject_dir(dem_type, res, prod_dir="geo_{}".format(pol))
    if cpol:
        reproject_dir(dem_type, res, prod_dir="geo_{}".format(cpol))
    create_browse_images(out_name, pol, cpol, browse_res)
    log_file = logging.getLogger().handlers[0].baseFilename
    rtc_name = out_name + "_" + pol + ".tif"
    gamma_ver = gamma_version()
    create_iso_xml(rtc_name, out_name, pol, cpol, in_file, dem_type, log_file, gamma_ver)
    create_arc_xml(in_file, out_name, input_type, gamma_flag, pwr_flag, filter_flag, looks, pol, cpol,
                   dem_type, res, hyp3_rtc_gamma.__version__, gamma_ver, rtc_name)
    cogify_dir(res=res)
    clean_prod_dir()
    perform_sanity_checks()
    logging.info("===================================================================")
    logging.info("               Sentinel RTC Program - Completed")
    logging.info("===================================================================")

    create_consolidated_log(out_name, lo_flag, dead_flag, match_flag, gamma_flag, roi,
                            shape, pwr_flag, filter_flag, pol, looks, log_file, smooth, terms,
                            no_cross_pol, par)
    return 'PRODUCT'


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='rtc_sentinel.py',
        description=__doc__,
    )
    parser.add_argument('input', help='Name of input file, either .zip or .SAFE')
    parser.add_argument("-o", "--outputResolution", type=float, help="Desired output resolution")

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
    parser.add_argument("-l", action="store_true", help="create a lo-res output (30m)")
    parser.add_argument("-f", action="store_true", help="run enhanced lee filter")
    parser.add_argument("-k", "--looks", type=int,
                        help="set the number of looks to take (def:3 for SLC/6 for GRD)")
    parser.add_argument("-t", "--terms", type=int, default=1,
                        help="set the number of terms in matching polynomial (default is 1)")
    parser.add_argument('--output', help='base name of the output files')
    parser.add_argument("--par", help="Stack processing - use specified offset file and don't match")
    parser.add_argument("--nocrosspol", action="store_true", help="Do not process the cross pol image")
    parser.add_argument("-a", "--area", action="store_true", help="Keep area map")
    args = parser.parse_args()

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
                       lo_flag=args.l,
                       pwr_flag=not args.amp,
                       filter_flag=args.f,
                       looks=args.looks,
                       terms=args.terms,
                       par=args.par,
                       no_cross_pol=args.nocrosspol,
                       smooth=args.smooth,
                       area=args.area)


if __name__ == "__main__":
    main()
