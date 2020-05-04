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
        with open("{}.xml".format(myfile), "wb") as g:
            this_pol = None
            if cpol is None:
                cpol = "ZZ"

            if pol in myfile or cpol in myfile:
                template_suffix = ''
                encoded_jpg = pngtothumb("{}.png".format(outfile))
                if pol in myfile:
                    this_pol = pol
                else:
                    this_pol = cpol
            elif "ls_map" in myfile:
                template_suffix = '_ls'
                execute("pbmmake 100 75 | pnmtopng > white.png", uselogging=True)
                encoded_jpg = pngtothumb("white.png")
                os.remove("white.png")
            elif "inc_map" in myfile:
                template_suffix = '_inc'
                encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
            elif "dem" in myfile:
                if "NED" in dem_type:
                    template_suffix = '_dem_NED'
                elif "SRTM" in dem_type:
                    template_suffix = '_dem_SRTM'
                elif "EU_DEM" in dem_type:
                    template_suffix = '_dem_EUDEM'
                elif "GIMP" in dem_type:
                    template_suffix = '_dem_GIMP'
                elif "REMA" in dem_type:
                    template_suffix = '_dem_REMA'
                else:
                    logging.error("ERROR: Unrecognized dem type: {}".format(dem_type))
                encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
            else:
                template_suffix = None
                encoded_jpg = None

            if template_suffix is not None:
                with open("{}/RTC_GAMMA_Template{}.xml".format(etc_dir, template_suffix), "rb") as f:
                    for line in f:
                        line = line.replace(b"[DATE]", bytes(date, 'utf-8'))
                        line = line.replace(b"[TIME]", bytes("{}00".format(time), 'utf-8'))
                        line = line.replace(b"[DATETIME]", bytes(dt, 'utf-8'))
                        line = line.replace(b"[YEARPROCESSED]", bytes("{}".format(year), 'utf-8'))
                        line = line.replace(b"[YEARACQUIRED]", bytes(infile[17:21], 'utf-8'))
                        line = line.replace(b"[TYPE]", bytes(input_type, 'utf-8'))
                        line = line.replace(b"[FULL_TYPE]", bytes(full_type, 'utf-8'))
                        line = line.replace(b"[THUMBNAIL_BINARY_STRING]", encoded_jpg)
                        if this_pol is not None:
                            line = line.replace(b"[POL]", bytes(this_pol, 'utf-8'))
                        line = line.replace(b"[POWERTYPE]", bytes(power_type, 'utf-8'))
                        line = line.replace(b"[GRAN_NAME]", bytes(granulename, 'utf-8'))
                        line = line.replace(b"[FORMAT]", bytes(format_type, 'utf-8'))
                        line = line.replace(b"[LOOKS]", bytes("{}".format(looks), 'utf-8'))
                        line = line.replace(b"[FILT]", bytes("{}".format(filter_str), 'utf-8'))
                        line = line.replace(b"[FLOOKS]", bytes("{}".format(flooks), 'utf-8'))
                        line = line.replace(b"[SPACING]", bytes("{}".format(spacing), 'utf-8'))
                        line = line.replace(b"[DEM]", bytes("{}".format(dem_type), 'utf-8'))
                        line = line.replace(b"[RESA]", bytes("{}".format(resa), 'utf-8'))
                        line = line.replace(b"[RESM]", bytes("{}".format(resm), 'utf-8'))
                        line = line.replace(b"[HYP3_VER]", bytes("{}".format(hyp3_ver), 'utf-8'))
                        line = line.replace(b"[GAMMA_VER]", bytes("{}".format(gamma_ver), 'utf-8'))
                        line = line.replace(b"[TILES]", bytes("{}".format(dem_tiles), 'utf-8'))
                        line = line.replace(b"[PCS]", bytes("{}".format(pcs), 'utf-8'))
                        g.write(line + b'\n')

    for myfile in glob.glob("*.png"):
        with open("{}.xml".format(myfile), "wb") as g:
            if "rgb" in myfile:
                scale = 'color'
                encoded_jpg = pngtothumb("{}_rgb.png".format(outfile))
            else:
                scale = 'grayscale'
                encoded_jpg = pngtothumb("{}.png".format(outfile))

            if "large" in myfile:
                res = "medium"
            else:
                res = "low"

            with open("{}/RTC_GAMMA_Template_{}_png.xml".format(etc_dir, scale), "rb") as f:
                for line in f:
                    line = line.replace(b"[DATE]", bytes(date, 'utf-8'))
                    line = line.replace(b"[TIME]", bytes("{}00".format(time), 'utf-8'))
                    line = line.replace(b"[DATETIME]", bytes(dt, 'utf-8'))
                    line = line.replace(b"[YEARPROCESSED]", bytes("{}".format(year), 'utf-8'))
                    line = line.replace(b"[YEARACQUIRED]", bytes(infile[17:21], 'utf-8'))
                    line = line.replace(b"[TYPE]", bytes(input_type, 'utf-8'))
                    line = line.replace(b"[FULL_TYPE]", bytes(full_type, 'utf-8'))
                    line = line.replace(b"[THUMBNAIL_BINARY_STRING]", encoded_jpg)
                    line = line.replace(b"[GRAN_NAME]", bytes(granulename, 'utf-8'))
                    line = line.replace(b"[RES]", bytes(res, 'utf-8'))
                    line = line.replace(b"[SPACING]", bytes("{}".format(spacing), 'utf-8'))
                    line = line.replace(b"[DEM]", bytes("{}".format(dem_type), 'utf-8'))
                    line = line.replace(b"[FORMAT]", bytes(format_type, 'utf-8'))
                    line = line.replace(b"[HYP3_VER]", bytes("{}".format(hyp3_ver), 'utf-8'))
                    line = line.replace(b"[GAMMA_VER]", bytes("{}".format(gamma_ver), 'utf-8'))
                    line = line.replace(b"[DEM_TILES]", bytes("{}".format(dem_tiles), 'utf-8'))
                    line = line.replace(b"[PCS]", bytes("{}".format(pcs), 'utf-8'))
                    g.write(line + b"\n")

    with open("README.txt", "w") as g:
        with open("{}/README_RTC_GAMMA.txt".format(etc_dir), "r") as f:
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

    os.chdir(back)
