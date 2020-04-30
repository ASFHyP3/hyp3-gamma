"""Create Radiometrically Terrain-Corrected (RTC) files using GAMMA software"""

import argparse
import datetime
import glob
import logging
import os
import shutil
import sys
import zipfile

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
from hyp3lib.utm2dem import utm2dem
from osgeo import gdal

import hyp3_rtc_gamma
from hyp3_rtc_gamma.asf_utils import write_asf_meta
from hyp3_rtc_gamma.check_coreg import check_coreg
from hyp3_rtc_gamma.create_metadata import create_arc_xml
from hyp3_rtc_gamma.smoothem import smooth_dem_tiles
from hyp3_rtc_gamma.xml2meta import sentinel2meta


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


def reproject_dir(demType, res, prod_dir=None):
    if "REMA" in demType:
        #        epsg = "EPSG:3031"
        epsg = 3031
    elif "GIMP" in demType:
        #       epsg = "EPSG:3413"
        epsg = 3413
    else:
        return

    tmpGeotiff = "tmp_reproj_dir_{}.tif".format(os.getpid())
    if prod_dir:
        home = os.getcwd()
        os.chdir(prod_dir)

    for inGeotiff in glob.glob("*.tif"):
        inRaster = gdal.Open(inGeotiff)
        outRaster = reproject2grid(inRaster, epsg, xRes=res)
        inRaster = None
        gdal.Translate(tmpGeotiff, outRaster)
        os.remove(inGeotiff)
        shutil.move(tmpGeotiff, inGeotiff)

    if prod_dir:
        os.chdir(home)


def report_kwargs(inName, outName, res, dem, roi, shape, matchFlag, deadFlag, gammaFlag, loFlag,
                  pwrFlag, filterFlag, looks, terms, par, noCrossPol, smooth, area):
    logging.info("Parameters for this run:")
    logging.info("    Input name                        : {}".format(inName))
    logging.info("    Output name                       : {}".format(outName))
    logging.info("    Output resolution                 : {}".format(res))
    logging.info("    DEM file                          : {}".format(dem))
    if roi is not None:
        logging.info("    Area of Interest                  : {}".format(roi))
    if shape is not None:
        logging.info("    Shape File                        : {}".format(shape))
    logging.info("    Match flag                        : {}".format(matchFlag))
    logging.info("    If no match, use Dead Reckoning   : {}".format(deadFlag))
    logging.info("    Gamma0 output                     : {}".format(gammaFlag))
    logging.info("    Low resolution flag               : {}".format(loFlag))
    logging.info("    Create power images               : {}".format(pwrFlag))
    logging.info("    Speckle Filtering                 : {}".format(filterFlag))
    logging.info("    Number of looks to take           : {}".format(looks))
    logging.info("    Number of terms in used in match  : {}".format(terms))
    if par is not None:
        logging.info("    Offset file                       : {}".format(par))
    logging.info("    Process crosspol                  : {}".format(not noCrossPol))
    logging.info("    Smooth DEM tiles                  : {}".format(smooth))
    logging.info("    Save Pixel Area                   : {}".format(area))


def process_pol(inFile, rtcName, auxName, pol, res, look_fact, matchFlag, deadFlag, gammaFlag,
                filterFlag, pwrFlag, browse_res, outName, dem, date, terms, par=None, area=False):
    logging.info("Processing the {} polarization".format(pol))

    mgrd = "{out}.{pol}.mgrd".format(out=outName, pol=pol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(inFile, pol, look_fact, mgrd)
    width = getParameter("{}.par".format(mgrd), "range_samples")

    # Apply filter if requested
    if filterFlag:
        el_looks = look_fact * 30
        cmd = "enh_lee {mgrd} temp.mgrd {wid} {el} 1 7 7".format(mgrd=mgrd, wid=width, el=el_looks)
        execute(cmd, uselogging=True)
        shutil.move("temp.mgrd", mgrd)

    options = "-p -j -n {} -q -c ".format(terms)
    if gammaFlag:
        options += "-g "

    logging.info("Running RTC process... initializing")
    geo_dir = "geo_{}".format(pol)
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par" \
          " {dir}/area.dem {dir}/area.dem_par {dir} image {res} 0" \
          " {opt}".format(mgrd=mgrd, dem=dem, dir=geo_dir, res=res, opt=options)
    execute(cmd, uselogging=True)

    if matchFlag and not par:
        fail = False
        logging.info("Running RTC process... coarse matching")
        cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par" \
              " {dir}/area.dem {dir}/area.dem_par {dir} image {res} 1" \
              " {opt}".format(mgrd=mgrd, dem=dem, dir=geo_dir, res=res, opt=options)
        try:
            execute(cmd, uselogging=True)
        except Exception:
            logging.warning("WARNING: Determination of the initial offset failed, skipping initial offset")

        logging.info("Running RTC process... fine matching")
        cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par" \
              " {dir}/area.dem {dir}/area.dem_par {dir} image {res} 2" \
              " {opt}".format(mgrd=mgrd, dem=dem, dir=geo_dir, res=res, opt=options)
        try:
            execute(cmd, uselogging=True)
        except Exception:
            if not deadFlag:
                logging.error("ERROR: Failed to match images")
                sys.exit(1)
            else:
                logging.warning("WARNING: Coregistration has failed; defaulting to dead reckoning")
                os.remove("{}/{}".format(geo_dir, "image.diff_par"))
                fail = True

        if not fail:
            try:
                check_coreg(outName, res, max_offset=75, max_error=2.0)
            except Exception:
                if not deadFlag:
                    logging.error("ERROR: Failed the coregistration check")
                    sys.exit(1)
                else:
                    logging.warning("WARNING: Coregistration check has failed; defaulting to dead reckoning")
                    os.remove("{}/{}".format(geo_dir, "image.diff_par"))

    logging.info("Running RTC process... finalizing")
    if par:
        shutil.copy(par, "{}/image.diff_par".format(geo_dir))
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par" \
          " {dir}/area.dem {dir}/area.dem_par {dir} image " \
          "{res} 3 {opt}".format(mgrd=mgrd, dem=dem, dir=geo_dir, res=res, opt=options)
    execute(cmd, uselogging=True)

    os.chdir(geo_dir)

    # Divide sigma0 by sin(theta) to get beta0
    cmd = "float_math image_0.inc_map - image_1.sin_theta {wid} 7 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    cmd = "float_math image_cal_map.mli image_1.sin_theta image_1.beta {wid} 3 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    cmd = "float_math image_1.beta image_0.sim image_1.flat {wid} 3 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    # Make Geotiff Files
    cmd = "data2geotiff area.dem_par image_0.ls_map 5 {}.ls_map.tif".format(outName)
    execute(cmd, uselogging=True)
    cmd = "data2geotiff area.dem_par image_0.inc_map 2 {}.inc_map.tif".format(outName)
    execute(cmd, uselogging=True)
    cmd = "data2geotiff area.dem_par image_1.flat 2 {}.flat.tif".format(outName)
    execute(cmd, uselogging=True)
    cmd = "data2geotiff area.dem_par area.dem 2 outdem.tif"
    execute(cmd, uselogging=True)
    gdal.Translate("{}.dem.tif".format(outName), "outdem.tif", outputType=gdal.GDT_Int16)

    if gammaFlag:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_gamma0'.format(pol)])
    else:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_sigma0'.format(pol)])
    shutil.move("tmp.tif", tif)
    createAmp(tif, nodata=0)

    # Make meta files and stats
    cmd = "asf_import -format geotiff {}.ls_map.tif ls_map".format(outName)
    execute(cmd, uselogging=True)
    cmd = "stats -overstat -overmeta ls_map"
    execute(cmd, uselogging=True)
    cmd = "asf_import -format geotiff {}.inc_map.tif inc_map".format(outName)
    execute(cmd, uselogging=True)
    cmd = "stats -overstat -overmeta -mask 0 inc_map"
    execute(cmd, uselogging=True)
    cmd = "asf_import -format geotiff image_cal_map.mli_amp.tif tc_{}".format(pol)
    execute(cmd, uselogging=True)
    cmd = "stats -nostat -overmeta -mask 0 tc_{}".format(pol)
    execute(cmd, uselogging=True)

    # Make browse resolution tif file
    if (res == browse_res):
        shutil.copy("image_cal_map.mli_amp.tif", "{}_{}_{}m.tif".format(outName, pol, browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(outName, pol, browse_res), "image_cal_map.mli_amp.tif",
                       xRes=browse_res, yRes=browse_res)

    # Move files into the product directory
    outDir = "../PRODUCT"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    tifName = rtcName
    if pwrFlag:
        shutil.move(tif, "{}/{}".format(outDir, tifName))
    else:
        copy_metadata(tif, "image_cal_map.mli_amp.tif")
        shutil.move("image_cal_map.mli_amp.tif", "{}/{}".format(outDir, tifName))

    shutil.move("{}.ls_map.tif".format(outName), "{}/{}_ls_map.tif".format(outDir, auxName))
    shutil.move("{}.inc_map.tif".format(outName), "{}/{}_inc_map.tif".format(outDir, auxName))
    shutil.move("{}.dem.tif".format(outName), "{}/{}_dem.tif".format(outDir, auxName))
    shutil.copy("image.diff_par", "{}/{}_diff.par".format(outDir, auxName))
    if area:
        shutil.move("{}.flat.tif".format(outName), "{}/{}_flat_{}.tif".format(outDir, auxName, pol))

    os.chdir("..")


def process_2nd_pol(inFile, rtcName, cpol, res, look_fact, gammaFlag, filterFlag, pwrFlag, browse_res,
                    outfile, dem, date, terms, par=None, area=False):
    if cpol == "VH":
        mpol = "VV"
    else:
        mpol = "HH"

    mgrd = "{out}.{pol}.mgrd".format(out=outfile, pol=cpol)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    ingest_S1_granule(inFile, cpol, look_fact, mgrd)
    width = getParameter("{}.par".format(mgrd), "range_samples")

    # Apply filtering if requested
    if filterFlag:
        el_looks = look_fact * 30
        cmd = "enh_lee {mgrd} temp.mgrd {wid} {el} 1 7 7".format(mgrd=mgrd, wid=width, el=el_looks)
        execute(cmd, uselogging=True)
        shutil.move("temp.mgrd", mgrd)

    options = "-p -j -n {} -q -c ".format(terms)
    if gammaFlag:
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
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par" \
          " {mdir}/area.dem {mdir}/area.dem_par {dir} image {res} 3" \
          " {opts}".format(mgrd=mgrd, dem=dem, mdir=mdir, dir=geo_dir, res=res, opts=options)
    execute(cmd, uselogging=True)

    os.chdir(geo_dir)

    # Divide sigma0 by sin(theta) to get beta0
    cmd = "float_math image_0.inc_map - image_1.sin_theta {wid} 7 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    cmd = "float_math image_cal_map.mli image_1.sin_theta image_1.beta {wid} 3 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    cmd = "float_math image_1.beta image_0.sim image_1.flat {wid} 3 - - 1 1 - 0".format(wid=width)
    execute(cmd)

    # Make geotiff file
    if gammaFlag:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_gamma0'.format(cpol)])
    else:
        gdal.Translate("tmp.tif", tif, metadataOptions=['Band1={}_sigma0'.format(cpol)])
    shutil.move("tmp.tif", tif)

    # Make browse resolution file
    createAmp(tif, nodata=0)
    if (res == browse_res):
        shutil.copy("image_cal_map.mli_amp.tif", "{}_{}_{}m.tif".format(outfile, cpol, browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(outfile, cpol, browse_res), "image_cal_map.mli_amp.tif", xRes=browse_res,
                       yRes=browse_res)

    # Create meta files and stats
    cmd = "asf_import -format geotiff image_cal_map.mli_amp.tif tc_{}".format(cpol)
    execute(cmd, uselogging=True)
    cmd = "stats -nostat -overmeta -mask 0 tc_{}".format(cpol)
    execute(cmd, uselogging=True)

    # Move files to product directory
    outDir = "../PRODUCT"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    cmd = "data2geotiff area.dem_par image_1.flat 2 {}.flat.tif".format(outfile)
    execute(cmd, uselogging=True)

    if pwrFlag:
        shutil.move(tif, "{}/{}".format(outDir, rtcName))
    else:
        copy_metadata(tif, "image_cal_map.mli_amp.tif")
        shutil.move("image_cal_map.mli_amp.tif", "{}/{}".format(outDir, rtcName))
    if area:
        shutil.move("{}.flat.tif".format(outfile), "{}/{}_flat_{}.tif".format(outDir, rtcName, cpol))

    os.chdir(home_dir)


def create_browse_images(outName, rtcName, res, pol, cpol, browse_res):
    ampfile = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=pol, name=outName, res=browse_res)
    if cpol:
        ampfile2 = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=cpol, name=outName, res=browse_res)
        threshold = -24
        outfile = "{}_rgb.tif".format(outName)
        rtc2color(ampfile, ampfile2, threshold, outfile, amp=True, cleanup=True)
        colorname = "PRODUCT/{}_rgb".format(rtcName)
        makeAsfBrowse(outfile, colorname)

    os.chdir("geo_{}".format(pol))
    outdir = "../PRODUCT"
    outfile = "{}/{}".format(outdir, rtcName)
    ampfile = "{name}_{pol}_{res}m.tif".format(pol=pol, name=outName, res=browse_res)
    sigmafile = ampfile.replace(".tif", "_sigma.tif")
    byteSigmaScale(ampfile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)

    os.chdir("../PRODUCT")

    infile = "{}_inc_map.tif".format(rtcName)
    outfile = "{}_inc_map".format(rtcName)
    sigmafile = infile.replace(".tif", "_sigma.tif")
    byteSigmaScale(infile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)
    os.remove(sigmafile)

    infile = "{}_ls_map.tif".format(rtcName)
    outfile = "{}_ls_map".format(rtcName)
    makeAsfBrowse(infile, outfile)

    infile = "{}_dem.tif".format(rtcName)
    outfile = "{}_dem".format(rtcName)
    sigmafile = infile.replace(".tif", "_sigma.tif")
    byteSigmaScale(infile, sigmafile)
    makeAsfBrowse(sigmafile, outfile)
    os.remove(sigmafile)

    raster_boundary2shape(rtcName + "_" + pol + ".tif", None, rtcName + "_shape.shp", use_closing=False,
                          pixel_shift=True, fill_holes=True)

    os.chdir("..")


def create_consolidated_log(basename, outName, loFlag, deadFlag, matchFlag, gammaFlag, roi,
                            shape, pwrFlag, filterFlag, pol, looks, logFile, smooth, terms,
                            noCrossPol, par):
    out = "PRODUCT"
    logname = "{}/{}.log".format(out, basename)
    logging.info("Creating log file: {}".format(logname))

    f = open(logname, "w")
    f.write("Consolidated log for: {}\n".format(outName))
    options = ""
    if loFlag:
        options += "-l "
    if not deadFlag:
        options += "--fail "
    if matchFlag:
        options += "-n "
    if not gammaFlag:
        options += "--sigma "
    if filterFlag:
        options += "-f "
    if not pwrFlag:
        options += "--amp "
    if smooth:
        options += "--smooth "
    options += "-k {}".format(looks)
    options += "-t {}".format(terms)
    if par:
        options += "--par {}".format(par)
    if noCrossPol:
        options += "--noCrossPol".format(noCrossPol)
    if roi:
        options += "-a {}".format(roi)
    if shape:
        options += "-s {}".format(shape)

    cmd = "rtc_sentinel.py " + options
    f.write("Command: {}\n".format(cmd))
    f.close()

    geo_dir = "geo_{}".format(pol)
    add_log(logFile, logname)
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


def create_iso_xml(outfile, outname, pol, cpol, inFile, output, demType, log):
    hdf5_name = "hdf5_list.txt"
    path = inFile
    etc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "etc"))
    shutil.copy("{}/sentinel_xml.xsl".format(etc_dir), "sentinel_xml.xsl")

    out = "PRODUCT"

    cmd = "xsltproc --stringparam path {path} --stringparam timestamp timestring" \
          " --stringparam file_size 1000 --stringparam server stuff" \
          " --output out.xml sentinel_xml.xsl {path}/manifest.safe".format(path=path)
    execute(cmd, uselogging=True)

    m = sentinel2meta("out.xml")
    write_asf_meta(m, "out.meta")

    # TODO: This could probably moved to a function in hyp3lib
    gamma_ver = os.getenv('GAMMA_VERSION')
    if gamma_ver is None:
        try:
            gamma_home = os.environ['GAMMA_HOME']
        except KeyError:
            logging.error(f'No GAMMA_HOME environment variable defined! GAMMA is not installed.')
            raise

        try:
            with open(f"{gamma_home}/ASF_Gamma_version.txt") as f:
                gamma_ver = f.readlines()[-1].strip()
        except IOError:
            logging.warning(
                f"No GAMMA_VERSION environment variable or ASF_Gamma_version.txt "
                f"file found in GAMMA_HOME:\n     {os.getenv('GAMMA_HOME')}\n"
                f"Attempting to parse GAMMA version from its install directory"
            )
            gamma_ver = os.path.basename(gamma_home).split('-')[-1]
    try:
        datetime.datetime.strptime(gamma_ver, '%Y%m%d')
    except ValueError:
        logging.warning(f'GAMMA version {gamma_ver} does not conform to the expected YYYYMMDD format')

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
    g.write("granule = {}\n".format(inFile.replace(".SAFE", "")))
    g.write("metadata = out.meta\n")

    geo_dir = "geo_{}".format(pol)
    dem_seg = "{}/area.dem".format(geo_dir)
    dem_seg_par = "{}/area.dem_par".format(geo_dir)

    g.write("oversampled dem file = {}\n".format(dem_seg))
    g.write("oversampled dem metadata = {}\n".format(dem_seg_par))
    g.write("original dem file = {}/{}_dem.tif\n".format(out, outname))
    g.write("layover shadow mask = {}/{}_ls_map.tif\n".format(out, outname))
    g.write("layover shadow stats = {}/ls_map.stat\n".format(geo_dir))
    g.write("incidence angle file = {}/{}_inc_map.tif\n".format(out, outname))
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
    g.write("mli.par file = {}.{}.mgrd.par\n".format(output, pol))
    g.write("gamma version = {}\n".format(gamma_ver))
    g.write("hyp3_rtc version = {}\n".format(hyp3_rtc_gamma.__version__))
    g.write("ipf version = {}\n".format(ipf_ver))
    g.write("dem source = {}\n".format(demType))
    g.write("browse image = {}/{}.png\n".format(out, outname))
    g.write("kml overlay = {}/{}.kmz\n".format(out, outname))

    g.close()

    cmd = "write_hdf5_xml {} {}.xml".format(hdf5_name, outname)
    execute(cmd, uselogging=True)

    logging.info("Generating {}.iso.xml with {}/rtc_iso.xsl\n".format(outname, etc_dir))

    cmd = "xsltproc {etc}/rtc_iso.xsl {out}.xml > {out}.iso.xml".format(etc=etc_dir, out=outname)
    execute(cmd, uselogging=True)

    shutil.copy("{}.iso.xml".format(outname), "{}".format(out))

    return gamma_ver


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


def rtc_sentinel_gamma(inFile,
                       outName=None,
                       res=None,
                       dem=None,
                       roi=None,
                       shape=None,
                       matchFlag=True,
                       deadFlag=None,
                       gammaFlag=None,
                       loFlag=None,
                       pwrFlag=None,
                       filterFlag=None,
                       looks=None,
                       terms=1,
                       par=None,
                       noCrossPol=False,
                       smooth=False,
                       area=False):
    logging.info("===================================================================")
    logging.info("                Sentinel RTC Program - Starting")
    logging.info("===================================================================")

    logging.info("Area flag is {}".format(area))

    if res is None:
        res = 10
    if loFlag:
        res = 30

    browse_res = 30
    if (res > browse_res):
        browse_res = res

    if looks is None:
        if res == 30:
            if "GRD" in inFile:
                looks = 6
            else:
                looks = 3
        else:
            looks = int(res / 10 + 0.5)
        logging.info("Setting looks to {}".format(looks))

    # get rid of ending "/"
    if inFile.endswith("/"):
        inFile = inFile[0:len(inFile) - 1]

    if not os.path.exists(inFile):
        logging.error("ERROR: Input file {} does not exist".format(inFile))
        sys.exit(1)
    if "zip" in inFile:
        zip_ref = zipfile.ZipFile(inFile, 'r')
        zip_ref.extractall(".")
        zip_ref.close()
        inFile = inFile.replace(".zip", ".SAFE")

    plat = inFile[2:3]
    mode = inFile[4:6]
    inputType = inFile[7:11]
    date = inFile[17:25]
    time = inFile[26:32]

    if 'SLC' in inputType:
        inputType = 'SLC'
    else:
        inputType = 'GRD'

    if gammaFlag:
        d = "g"
    else:
        d = "s"

    if pwrFlag:
        e = "p"
    else:
        e = "a"

    if filterFlag:
        f = "f"
    else:
        f = "n"

    if outName is None:
        baseName = "S1{}_{}_RT{}_{}T{}_G_{}{}{}".format(plat, mode, int(res), date, time, d, e, f)
        outName = baseName
    else:
        baseName = outName
    auxName = baseName

    report_kwargs(inFile, baseName, res, dem, roi, shape, matchFlag, deadFlag, gammaFlag, loFlag,
                  pwrFlag, filterFlag, looks, terms, par, noCrossPol, smooth, area)

    if dem is None:
        logging.info("Getting DEM file covering this SAR image")
        tifdem = "tmp_{}_dem.tif".format(os.getpid())
        if shape is not None:
            minX, minY, maxX, maxY = get_bb_from_shape(shape)
            logging.info(f'bounding box: {minX}, {minY}, {maxX}, {maxY}')
            roi = []
            roi.append(minX)
            roi.append(minY)
            roi.append(maxX)
            roi.append(maxY)
        if roi is not None:
            demType = get_dem(roi[0], roi[1], roi[2], roi[3], tifdem, post=30)
        else:
            demfile, demType = getDemFile(inFile, tifdem, post=30)

        if 'REMA' in demType and smooth:
            logging.info("Preparing to smooth DEM tiles")
            dem, parfile = smooth_dem_tiles("DEM", build=True)
        else:
            dem = "area.dem"
            parfile = "area.dem.par"
            if "GIMP" in demType or "REMA" in demType:
                ps2dem(tifdem, dem, parfile)
            else:
                utm2dem(tifdem, dem, parfile)
            os.remove(tifdem)
    elif ".tif" in dem:
        tiff_dem = dem
        dem = "area.dem"
        parfile = "area.dem.par"
        utm2dem(tiff_dem, dem, parfile)
        demType = "Unknown"
    elif os.path.isfile("{}.par".format(dem)):
        demType = "Unknown"
    else:
        logging.error("ERROR: Unrecognized DEM: {}".format(dem))
        sys.exit(1)

    vvlist = glob.glob("{}/*/*vv*.tiff".format(inFile))
    vhlist = glob.glob("{}/*/*vh*.tiff".format(inFile))
    hhlist = glob.glob("{}/*/*hh*.tiff".format(inFile))
    hvlist = glob.glob("{}/*/*hv*.tiff".format(inFile))

    cpol = None

    if vvlist:
        logging.info("Found VV polarization - processing")
        pol = "VV"
        rtcName = baseName + "_" + pol + ".tif"
        process_pol(inFile, rtcName, auxName, pol, res, looks, matchFlag, deadFlag, gammaFlag, filterFlag, pwrFlag,
                    browse_res, outName, dem, date, terms, par=par, area=area)

        if vhlist and not noCrossPol:
            cpol = "VH"
            rtcName = baseName + "_" + cpol + ".tif"
            logging.info("Found VH polarization - processing")
            process_2nd_pol(inFile, rtcName, cpol, res, looks, gammaFlag, filterFlag, pwrFlag, browse_res,
                            outName, dem, date, terms, par=par, area=area)

    if hhlist:
        logging.info("Found HH polarization - processing")
        pol = "HH"
        rtcName = baseName + "_" + pol + ".tif"
        process_pol(inFile, rtcName, auxName, pol, res, looks, matchFlag, deadFlag, gammaFlag, filterFlag, pwrFlag,
                    browse_res, outName, dem, date, terms, par=par, area=area)

        if hvlist and not noCrossPol:
            cpol = "HV"
            logging.info("Found HV polarization - processing")
            rtcName = baseName + "_" + cpol + ".tif"
            process_2nd_pol(inFile, rtcName, cpol, res, looks, gammaFlag, filterFlag, pwrFlag, browse_res,
                            outName, dem, date, terms, par=par, area=area)

    if hhlist is None and vvlist is None:
        logging.error("ERROR: Can not find VV or HH polarization in {}".inFile)
        sys.exit(1)

    fix_geotiff_locations()
    reproject_dir(demType, res, prod_dir="PRODUCT")
    reproject_dir(demType, res, prod_dir="geo_{}".format(pol))
    if cpol:
        reproject_dir(demType, res, prod_dir="geo_{}".format(cpol))
    create_browse_images(outName, auxName, res, pol, cpol, browse_res)
    logFile = logging.getLogger().handlers[0].baseFilename
    rtcName = baseName + "_" + pol + ".tif"
    gamma_ver = create_iso_xml(rtcName, auxName, pol, cpol, inFile, outName, demType, logFile)
    create_arc_xml(inFile, auxName, inputType, gammaFlag, pwrFlag, filterFlag, looks, pol, cpol,
                   demType, res, hyp3_rtc_gamma.__version__, gamma_ver, rtcName)
    cogify_dir(res=res)
    clean_prod_dir()
    perform_sanity_checks()
    logging.info("===================================================================")
    logging.info("               Sentinel RTC Program - Completed")
    logging.info("===================================================================")

    create_consolidated_log(auxName, outName, loFlag, deadFlag, matchFlag, gammaFlag, roi,
                            shape, pwrFlag, filterFlag, pol, looks, logFile, smooth, terms,
                            noCrossPol, par)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='rtc_sentinel',
                                     description='Creates an RTC image from a Sentinel 1 Scene using GAMMA software')
    parser.add_argument('input', help='Name of input file, either .zip or .SAFE')
    parser.add_argument("-o", "--outputResolution", type=float, help="Desired output resolution")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--externalDEM",
                       help="Specify a DEM file to use - must be in UTM projection")
    group.add_argument("-r", "--roi", help="Specify ROI to use", type=float, nargs=4,
                       metavar=('LON_MIN', 'LAT_MIN', 'LON_MAX', 'LAT_MAX'))
    group.add_argument("-s", "--shape", help="Specify shape file to use")
    parser.add_argument("-n", action="store_false", help="Do not perform matching")
    parser.add_argument("--fail", action="store_true", help="if matching fails, fail the program \
      default:use dead reckoning")
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
    parser.add_argument("--nocrosspol", help="Do not process the cross pol image", action="store_true")
    parser.add_argument("-a", "--area", help="Keep area map", action="store_true")
    args = parser.parse_args()

    logFile = "{}_{}_log.txt".format(args.input.rpartition('.')[0], os.getpid())
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    if args.fail:
        deadFlag = False
    else:
        deadFlag = True

    if not args.sigma:
        gammaFlag = True
    else:
        gammaFlag = False

    if args.amp:
        pwrFlag = False
    else:
        pwrFlag = True

    logging.info("Pixel area flag: {}".format(args.area))

    rtc_sentinel_gamma(args.input,
                       outName=args.output,
                       res=args.outputResolution,
                       dem=args.externalDEM,
                       roi=args.roi,
                       shape=args.shape,
                       matchFlag=args.n,
                       deadFlag=deadFlag,
                       gammaFlag=gammaFlag,
                       loFlag=args.l,
                       pwrFlag=pwrFlag,
                       filterFlag=args.f,
                       looks=args.looks,
                       terms=args.terms,
                       par=args.par,
                       noCrossPol=args.nocrosspol,
                       smooth=args.smooth,
                       area=args.area)
