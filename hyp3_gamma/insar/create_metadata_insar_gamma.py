import datetime
import logging
import os
import sys

from hyp3lib.system import gamma_version

import hyp3_insar_gamma.etc


def create_readme_file(refFile, secFile, outfile, pixelSize, demType, pol):
    looks = pixelSize / 20
    txtlooks = "{}x{}".format(looks * 5, looks)

    etcdir = os.path.abspath(os.path.dirname(hyp3_insar_gamma.etc.__file__))

    back = os.getcwd()
    os.chdir("PRODUCT")
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    year = now.year

    basename = os.path.basename(refFile)
    refname = os.path.splitext(basename)[0]
    basename = os.path.basename(secFile)
    secname = os.path.splitext(basename)[0]

    # FIXME: This doesn't exist anymore
    ver_file = "{}/version.txt".format(etcdir)
    hyp3_ver = None
    if os.path.exists(ver_file):
        with open(ver_file, "r") as f:
            for line in f:
                hyp3_ver = line.strip()
    else:
        logging.warning("No version.txt file found in {}".format(etcdir))

    gamma_ver = gamma_version()

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
    elif "SRTMGL" in demType:
        if "1" in demType:
            resa = 1
            resm = 30
        else:
            resa = 3
            resm = 90
    elif "EU_DEM" in demType:
        resa = 1
        resm = 30
    elif "GIMP" in demType:
        resa = 1
        resm = 30
    elif "REMA" in demType:
        resa = 1
        resm = 30
    else:
        logging.error("Unrecognized DEM type: {}".format(demType))
        sys.exit(1)

    with open("README.txt", "w") as g:
        with open("{}/README_InSAR_GAMMA.txt".format(etcdir), "r") as f:
            for line in f:
                line = line.replace("[DATE]", date)
                line = line.replace("[TIME]", "{}00".format(time))
                line = line.replace("[REF_NAME]", refname)
                line = line.replace("[SEC_NAME]", secname)
                line = line.replace("[YEARPROCESSED]", "{}".format(year))
                line = line.replace("[YEARACQUIRED]", refname[17:21])
                line = line.replace("[LOOKS]", "{}".format(txtlooks))
                line = line.replace("[SPACING]", "{}".format(pixelSize))
                line = line.replace("[DEM]", "{}".format(demType))
                line = line.replace("[RESA]", "{}".format(resa))
                line = line.replace("[RESM]", "{}".format(resm))
                line = line.replace("[HYP3_VER]", "{}".format(hyp3_ver))
                line = line.replace("[GAMMA_VER]", "{}".format(gamma_ver))
                g.write("{}".format(line))

    os.chdir(back)
