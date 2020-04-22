"""Create ArcGIS compatible xml metadata"""

import datetime
import glob
import logging
import os

from hyp3lib.execute import execute
from hyp3lib.file_subroutines import get_dem_tile_list
from hyp3lib.getParameter import getParameter
from hyp3lib.make_arc_thumb import pngtothumb
from hyp3lib.saa_func_lib import getCorners


# Get the UTM N/S designation
def get_hemisphere(fi):
    ullon,lrlon,lrlat,ullat = getCorners(fi)
    if lrlat + ullat >= 0:
        return("N")
    else:
        return("S")


def create_arc_xml(infile,outfile,inputType,gammaFlag,pwrFlag,filterFlag,looks,pol,cpol,
                   demType,spacing,hyp3_ver,gamma_ver,rtcName):

    print("create_arc_xml: CWD is {}".format(os.getcwd()))
    try:
        proj_name = getParameter("area.dem.par".format(pol.upper()),"projection_name")
        if "UTM" in proj_name:
            zone = getParameter("area.dem.par".format(pol.upper()),"projection_zone")
    except:
        zone = None
    logging.info("Zone is {}".format(zone))
   
    demTiles = get_dem_tile_list()    

    # Create XML metadata files
    etc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "etc"))
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
    flooks = looks*30
    hemi = get_hemisphere(rtcName)

    if gammaFlag:
        power_type = "gamma"
    else:
        power_type = "sigma"
    if pwrFlag:
        format_type = "power"
    else:
        format_type = "amplitude"
    if filterFlag:
        filterStr = "has"
    else:
        filterStr = "has not"

    if inputType == "SLC":
        full_type = "Single-Look Complex"
    else:
        full_type = "Ground Range Detected"

    if "NED" in demType:
        if "13" in demType:
            resa = "1/3"
            resm = 10
        elif "1" in demType:
            resa = 1
            resm = 30
        else:
            resa = 2
            resm = 60
        pcs = "WGS 1984 UTM Zone {}{}".format(zone,hemi)
    elif "SRTMGL" in demType:
        if "1" in demType:
            resa = 1
            resm = 30
        else:
            resa = 3
            resm = 90
        pcs = "WGS 1984 UTM Zone {}{}".format(zone,hemi)
    elif "EU_DEM" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 UTM Zone {}{}".format(zone,hemi)
    elif "GIMP" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 NSIDC Sea Ice Polar Stereographic North"
    elif "REMA" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 Antarctic Polar Stereographic"
    else:
        logging.error("Unrecognized DEM type: {}".format(demType))
        exit(1)

    for myfile in glob.glob("*.tif"):
        f = None
        this_pol = None
        if cpol is None:
            cpol = "ZZ"
        if pol in myfile or cpol in myfile:
            f = open("{}/RTC_GAMMA_Template.xml".format(etc_dir),"r")
            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(outfile))
            if pol in myfile:
                this_pol = pol
            else:
                this_pol = cpol
        elif "ls_map" in myfile:
            f = open("{}/RTC_GAMMA_Template_ls.xml".format(etc_dir),"r")
            g = open("{}.xml".format(myfile),"w")
            cmd = "pbmmake 100 75 | pnmtopng > white.png"
            execute(cmd,uselogging=True)
            encoded_jpg = pngtothumb("white.png")
            os.remove("white.png")
        elif "inc_map" in myfile:
            f = open("{}/RTC_GAMMA_Template_inc.xml".format(etc_dir),"r")
            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
        elif "dem" in myfile:
            if "NED" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_NED.xml".format(etc_dir),"r")
            elif "SRTM" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_SRTM.xml".format(etc_dir),"r")
            elif "EU_DEM" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_EUDEM.xml".format(etc_dir),"r")
            elif "GIMP" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_GIMP.xml".format(etc_dir),"r")
            elif "REMA" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_REMA.xml".format(etc_dir),"r")
            else:
                logging.error("ERROR: Unrecognized dem type: {}".format(demType)) 
            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
        if f is not None:
            for line in f:
                line = line.replace("[DATE]",date)
                line = line.replace("[TIME]","{}00".format(time))
                line = line.replace("[DATETIME]",dt)
                line = line.replace("[YEARPROCESSED]","{}".format(year))
                line = line.replace("[YEARACQUIRED]",infile[17:21])
                line = line.replace("[TYPE]",inputType)
                line = line.replace("[FULL_TYPE]",full_type)
                line = line.replace("[THUMBNAIL_BINARY_STRING]",encoded_jpg)
                if this_pol is not None:
                    line = line.replace("[POL]",this_pol)
                line = line.replace("[POWERTYPE]",power_type)
                line = line.replace("[GRAN_NAME]",granulename)
                line = line.replace("[FORMAT]",format_type)
                line = line.replace("[LOOKS]","{}".format(looks))
                line = line.replace("[FILT]","{}".format(filterStr))
                line = line.replace("[FLOOKS]","{}".format(flooks))
                line = line.replace("[SPACING]","{}".format(spacing))
                line = line.replace("[DEM]","{}".format(demType))
                line = line.replace("[RESA]","{}".format(resa))
                line = line.replace("[RESM]","{}".format(resm))
                line = line.replace("[HYP3_VER]","{}".format(hyp3_ver))
                line = line.replace("[GAMMA_VER]","{}".format(gamma_ver))
                line = line.replace("[TILES]","{}".format(demTiles))
                line = line.replace("[PCS]","{}".format(pcs))
                g.write("{}\n".format(line))
            f.close()
            g.close()


    for myfile in glob.glob("*.png"):

        if "rgb" in myfile:
            f = open("{}/RTC_GAMMA_Template_color_png.xml".format(etc_dir),"r")
            encoded_jpg = pngtothumb("{}_rgb.png".format(outfile))
        else:
            f = open("{}/RTC_GAMMA_Template_grayscale_png.xml".format(etc_dir),"r")
            encoded_jpg = pngtothumb("{}.png".format(outfile))

        if "large" in myfile:
            res = "medium"
        else:
            res = "low"

        g = open("{}.xml".format(myfile),"w")
        for line in f:
            line = line.replace("[DATE]",date)
            line = line.replace("[TIME]","{}00".format(time))
            line = line.replace("[DATETIME]",dt)
            line = line.replace("[YEARPROCESSED]","{}".format(year))
            line = line.replace("[YEARACQUIRED]",infile[17:21])
            line = line.replace("[TYPE]",inputType)
            line = line.replace("[FULL_TYPE]",full_type)
            line = line.replace("[THUMBNAIL_BINARY_STRING]",encoded_jpg)
            line = line.replace("[GRAN_NAME]",granulename)
            line = line.replace("[RES]",res)
            line = line.replace("[SPACING]","{}".format(spacing))
            line = line.replace("[DEM]","{}".format(demType))
            line = line.replace("[FORMAT]",format_type)
            line = line.replace("[HYP3_VER]","{}".format(hyp3_ver))
            line = line.replace("[GAMMA_VER]","{}".format(gamma_ver))
            line = line.replace("[DEM_TILES]","{}".format(demTiles))
            line = line.replace("[PCS]","{}".format(pcs))
            g.write("{}\n".format(line))
        f.close()
        g.close()

    f = open("{}/README_RTC_GAMMA.txt".format(etc_dir),"r")
    g = open("README.txt","w")
    for line in f:
        line = line.replace("[DATE]",date)
        line = line.replace("[TIME]","{}00".format(time))
        line = line.replace("[DATETIME]",dt)
        line = line.replace("[GRAN_NAME]",granulename)
        line = line.replace("[YEARPROCESSED]","{}".format(year))
        line = line.replace("[YEARACQUIRED]",infile[17:21])
        line = line.replace("[POWERTYPE]",power_type)
        line = line.replace("[FORMAT]",format_type)
        line = line.replace("[LOOKS]","{}".format(looks))
        line = line.replace("[FILT]","{}".format(filterStr))
        line = line.replace("[FLOOKS]","{}".format(flooks))
        line = line.replace("[SPACING]","{}".format(spacing))
        line = line.replace("[DEM]","{}".format(demType))
        line = line.replace("[RESA]","{}".format(resa))
        line = line.replace("[RESM]","{}".format(resm))
        line = line.replace("[HYP3_VER]","{}".format(hyp3_ver))
        line = line.replace("[GAMMA_VER]","{}".format(gamma_ver))
        line = line.replace("[DEM_TILES]","{}".format(demTiles))
        line = line.replace("[PCS]","{}".format(pcs))
        g.write("{}".format(line))
    f.close()
    g.close()

    os.chdir(back)


