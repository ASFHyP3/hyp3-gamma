"""Create ArcGIS compatible xml metadata"""

import datetime
import glob
import logging
import os
import sys

from hyp3lib.execute import execute
from hyp3lib.file_subroutines import get_dem_tile_list
from hyp3lib.getParameter import getParameter
from hyp3lib.make_arc_thumb import pngtothumb
from hyp3lib.saa_func_lib import getCorners

import hyp3_rtc_gamma.etc


def get_hemisphere(fi):
    """Get the UTM N/S designation"""
    ullon, lrlon, lrlat, ullat = getCorners(fi)
    if lrlat + ullat >= 0:
        return "N"
    else:
        return "S"


def create_arc_xml(infile, outfile, input_type, gamma_flag, pwr_flag, filter_flag, looks, pol, cpol,
                   dem_type, spacing, hyp3_ver, gamma_ver, rtc_name):
    print("create_arc_xml: CWD is {}".format(os.getcwd()))
    zone = None
    try:
        proj_name = getParameter("area.dem.par".format(pol.upper()), "projection_name")
        if "UTM" in proj_name:
            zone = getParameter("area.dem.par".format(pol.upper()), "projection_zone")
    except Exception:
        pass
    logging.info("Zone is {}".format(zone))

    dem_tiles = get_dem_tile_list()

    # Create XML metadata files
    etc_dir = os.path.abspath(os.path.dirname(hyp3_rtc_gamma.etc.__file__))
    back = os.getcwd()
    os.chdir("PRODUCT")

    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    year = now.year

    basename = os.path.basename(infile)
    granulename = os.path.splitext(basename)[0]

    spacing = int(spacing)
    flooks = looks * 30
    hemi = get_hemisphere(rtc_name)

    if gamma_flag:
        power_type = "gamma"
    else:
        power_type = "sigma"
    if pwr_flag:
        format_type = "power"
    else:
        format_type = "amplitude"
    if filter_flag:
        filter_str = "has"
    else:
        filter_str = "has not"

    if input_type == "SLC":
        full_type = "Single-Look Complex"
    else:
        full_type = "Ground Range Detected"

    if "NED" in dem_type:
        if "13" in dem_type:
            resa = "1/3"
            resm = 10
        elif "1" in dem_type:
            resa = 1
            resm = 30
        else:
            resa = 2
            resm = 60
        pcs = "WGS 1984 UTM Zone {}{}".format(zone, hemi)
    elif "SRTMGL" in dem_type:
        if "1" in dem_type:
            resa = 1
            resm = 30
        else:
            resa = 3
            resm = 90
        pcs = "WGS 1984 UTM Zone {}{}".format(zone, hemi)
    elif "EU_DEM" in dem_type:
        resa = 1
        resm = 30
        pcs = "WGS 1984 UTM Zone {}{}".format(zone, hemi)
    elif "GIMP" in dem_type:
        resa = 1
        resm = 30
        pcs = "WGS 1984 NSIDC Sea Ice Polar Stereographic North"
    elif "REMA" in dem_type:
        resa = 1
        resm = 30
        pcs = "WGS 1984 Antarctic Polar Stereographic"
    else:
        logging.error("Unrecognized DEM type: {}".format(dem_type))
        sys.exit(1)

    for myfile in glob.glob("*.tif"):
        with open("{}.xml".format(myfile), "w") as g:
            f = None
            this_pol = None
            if cpol is None:
                cpol = "ZZ"
            if pol in myfile or cpol in myfile:
                f = open("{}/RTC_GAMMA_Template.xml".format(etc_dir), "r")

                encoded_jpg = pngtothumb("{}.png".format(outfile))
                if pol in myfile:
                    this_pol = pol
                else:
                    this_pol = cpol
            elif "ls_map" in myfile:
                f = open("{}/RTC_GAMMA_Template_ls.xml".format(etc_dir), "r")
                execute("pbmmake 100 75 | pnmtopng > white.png", uselogging=True)
                encoded_jpg = pngtothumb("white.png")
                os.remove("white.png")
            elif "inc_map" in myfile:
                f = open("{}/RTC_GAMMA_Template_inc.xml".format(etc_dir), "r")
                encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
            elif "dem" in myfile:
                if "NED" in dem_type:
                    f = open("{}/RTC_GAMMA_Template_dem_NED.xml".format(etc_dir), "r")
                elif "SRTM" in dem_type:
                    f = open("{}/RTC_GAMMA_Template_dem_SRTM.xml".format(etc_dir), "r")
                elif "EU_DEM" in dem_type:
                    f = open("{}/RTC_GAMMA_Template_dem_EUDEM.xml".format(etc_dir), "r")
                elif "GIMP" in dem_type:
                    f = open("{}/RTC_GAMMA_Template_dem_GIMP.xml".format(etc_dir), "r")
                elif "REMA" in dem_type:
                    f = open("{}/RTC_GAMMA_Template_dem_REMA.xml".format(etc_dir), "r")
                else:
                    logging.error("ERROR: Unrecognized dem type: {}".format(dem_type))
                encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
            else:
                encoded_jpg = None
            if f is not None:
                for line in f:
                    line = line.replace("[DATE]", date)
                    line = line.replace("[TIME]", "{}00".format(time))
                    line = line.replace("[DATETIME]", dt)
                    line = line.replace("[YEARPROCESSED]", "{}".format(year))
                    line = line.replace("[YEARACQUIRED]", infile[17:21])
                    line = line.replace("[TYPE]", input_type)
                    line = line.replace("[FULL_TYPE]", full_type)
                    line = line.replace("[THUMBNAIL_BINARY_STRING]", encoded_jpg)
                    if this_pol is not None:
                        line = line.replace("[POL]", this_pol)
                    line = line.replace("[POWERTYPE]", power_type)
                    line = line.replace("[GRAN_NAME]", granulename)
                    line = line.replace("[FORMAT]", format_type)
                    line = line.replace("[LOOKS]", "{}".format(looks))
                    line = line.replace("[FILT]", "{}".format(filter_str))
                    line = line.replace("[FLOOKS]", "{}".format(flooks))
                    line = line.replace("[SPACING]", "{}".format(spacing))
                    line = line.replace("[DEM]", "{}".format(dem_type))
                    line = line.replace("[RESA]", "{}".format(resa))
                    line = line.replace("[RESM]", "{}".format(resm))
                    line = line.replace("[HYP3_VER]", "{}".format(hyp3_ver))
                    line = line.replace("[GAMMA_VER]", "{}".format(gamma_ver))
                    line = line.replace("[TILES]", "{}".format(dem_tiles))
                    line = line.replace("[PCS]", "{}".format(pcs))
                    g.write("{}\n".format(line))
                f.close()

    for myfile in glob.glob("*.png"):

        if "rgb" in myfile:
            f = open("{}/RTC_GAMMA_Template_color_png.xml".format(etc_dir), "r")
            encoded_jpg = pngtothumb("{}_rgb.png".format(outfile))
        else:
            f = open("{}/RTC_GAMMA_Template_grayscale_png.xml".format(etc_dir), "r")
            encoded_jpg = pngtothumb("{}.png".format(outfile))

        if "large" in myfile:
            res = "medium"
        else:
            res = "low"

        g = open("{}.xml".format(myfile), "w")
        for line in f:
            line = line.replace("[DATE]", date)
            line = line.replace("[TIME]", "{}00".format(time))
            line = line.replace("[DATETIME]", dt)
            line = line.replace("[YEARPROCESSED]", "{}".format(year))
            line = line.replace("[YEARACQUIRED]", infile[17:21])
            line = line.replace("[TYPE]", input_type)
            line = line.replace("[FULL_TYPE]", full_type)
            line = line.replace("[THUMBNAIL_BINARY_STRING]", encoded_jpg)
            line = line.replace("[GRAN_NAME]", granulename)
            line = line.replace("[RES]", res)
            line = line.replace("[SPACING]", "{}".format(spacing))
            line = line.replace("[DEM]", "{}".format(dem_type))
            line = line.replace("[FORMAT]", format_type)
            line = line.replace("[HYP3_VER]", "{}".format(hyp3_ver))
            line = line.replace("[GAMMA_VER]", "{}".format(gamma_ver))
            line = line.replace("[DEM_TILES]", "{}".format(dem_tiles))
            line = line.replace("[PCS]", "{}".format(pcs))
            g.write("{}\n".format(line))
        f.close()
        g.close()

    f = open("{}/README_RTC_GAMMA.txt".format(etc_dir), "r")
    g = open("README.txt", "w")
    for line in f:
        line = line.replace("[DATE]", date)
        line = line.replace("[TIME]", "{}00".format(time))
        line = line.replace("[DATETIME]", dt)
        line = line.replace("[GRAN_NAME]", granulename)
        line = line.replace("[YEARPROCESSED]", "{}".format(year))
        line = line.replace("[YEARACQUIRED]", infile[17:21])
        line = line.replace("[POWERTYPE]", power_type)
        line = line.replace("[FORMAT]", format_type)
        line = line.replace("[LOOKS]", "{}".format(looks))
        line = line.replace("[FILT]", "{}".format(filter_str))
        line = line.replace("[FLOOKS]", "{}".format(flooks))
        line = line.replace("[SPACING]", "{}".format(spacing))
        line = line.replace("[DEM]", "{}".format(dem_type))
        line = line.replace("[RESA]", "{}".format(resa))
        line = line.replace("[RESM]", "{}".format(resm))
        line = line.replace("[HYP3_VER]", "{}".format(hyp3_ver))
        line = line.replace("[GAMMA_VER]", "{}".format(gamma_ver))
        line = line.replace("[DEM_TILES]", "{}".format(dem_tiles))
        line = line.replace("[PCS]", "{}".format(pcs))
        g.write("{}".format(line))
    f.close()
    g.close()

    os.chdir(back)
