#!/usr/bin/python

import logging
import os
import datetime
from getParameter import getParameter
from make_arc_thumb import pngtothumb

def create_readme_file(refFile,secFile,outfile,pixelSize,demType,pol):

    looks = pixelSize / 20
    txtlooks = "{}x{}".format(looks*5,looks)

    etcdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "etc"))

    proj_name = getParameter("big.par".format(pol.upper()),"projection_name")
    if "UTM" in proj_name:
        zone = getParameter("big.par".format(pol.upper()),"projection_zone")
    else:
        zone = None

    back = os.getcwd()
    os.chdir("PRODUCT")
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    year = now.year

    pngfile = "{}_unw_phase.png".format(outfile)
    encoded_jpg = pngtothumb(pngfile)

    basename = os.path.basename(refFile)
    refname = os.path.splitext(basename)[0]
    basename = os.path.basename(secFile)
    secname = os.path.splitext(basename)[0]

    ver_file = "{}/version.txt".format(etcdir)
    hyp3_ver = None
    if os.path.exists(ver_file):
        f = open(ver_file,"r")
        for line in f:
            hyp3_ver = line.strip()
    else:
        logging.warning("No version.txt file found in {}".format(etcdir))

    ver_file = "{}/ASF_Gamma_version.txt".format(os.environ['GAMMA_HOME'])
    gamma_ver = None
    if os.path.exists(ver_file):
        f = open(ver_file,"r")
        for line in f:
            gamma_ver = line.strip()
    else:
        logging.warning("No ASF_Gamma_version.txt file found in {}".format(os.environ['GAMMA_HOME']))

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
        pcs = "WGS 1984 UTM zone {}".format(zone)
    elif "SRTMGL" in demType:
        if "1" in demType:
            resa = 1
            resm = 30
        else:
            resa = 3
            resm = 90
        pcs = "WGS 1984 UTM zone {}".format(zone)
    elif "EU_DEM" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 Antarctic Polar Stereographic"
    elif "GIMP" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 NSIDC Polar Stereographic North"
    elif "REMA" in demType:
        resa = 1
        resm = 30
        pcs = "WGS 1984 Antarctic Polar Stereographic"
    else:
        logging.error("Unrecognized DEM type: {}".format(demType))
        exit(1)

    f = open("{}/README_InSAR_GAMMA.txt".format(etcdir),"r")
    g = open("README.txt","w")

    for line in f:
        line = line.replace("[DATE]",date)
        line = line.replace("[TIME]","{}00".format(time))
        line = line.replace("[REF_NAME]",refname)
        line = line.replace("[SEC_NAME]",secname)
        line = line.replace("[YEARPROCESSED]","{}".format(year))
        line = line.replace("[YEARACQUIRED]",refname[17:21])
        line = line.replace("[LOOKS]","{}".format(txtlooks))
        line = line.replace("[SPACING]","{}".format(pixelSize))
        line = line.replace("[DEM]","{}".format(demType))
        line = line.replace("[RESA]","{}".format(resa))
        line = line.replace("[RESM]","{}".format(resm))
        line = line.replace("[HYP3_VER]","{}".format(hyp3_ver))
        line = line.replace("[GAMMA_VER]","{}".format(gamma_ver))
        g.write("{}".format(line))
    f.close()
    g.close()

    os.chdir(back)


