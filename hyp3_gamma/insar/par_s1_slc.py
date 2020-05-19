"""Pre-process S1 SLC imagery into gamma format SLCs"""

import argparse
import glob
import logging
import os
import sys
import zipfile

from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from hyp3lib.get_orb import downloadSentinelOrbitFile


def make_cmd(val, acqdate, path, pol=None):
    """make the par_S1_SLC gamma commands"""
    if pol is None:
        m = glob.glob(f"measurement/s1*-iw{val}*")[0]
        n = glob.glob(f"annotation/s1*-iw{val}*")[0]
        o = glob.glob(f"annotation/calibration/calibration-s1*-iw{val}*")[0]
        p = glob.glob(f"annotation/calibration/noise-s1*-iw{val}*")[0]
    else:
        m = glob.glob(f"measurement/s1*-iw{val}*{pol}*")[0]
        n = glob.glob(f"annotation/s1*-iw{val}*{pol}*")[0]
        o = glob.glob(f"annotation/calibration/calibration-s1*-iw{val}*{pol}*")[0]
        p = glob.glob(f"annotation/calibration/noise-s1*-iw{val}*{pol}*")[0]

    cmd = f"par_S1_SLC {m} {n} {o} {p} {path}/{acqdate}_00{val}.slc.par" \
          f" {path}/{acqdate}_00{val}.slc {path}/{acqdate}_00{val}.tops_par"
    return cmd


def par_s1_slc(pol=None):
    wrk = os.getcwd()

    if pol is None:
        pol = 'vv'

    for myfile in os.listdir("."):
        if ".zip" in myfile:
            if not os.path.exists(myfile.replace(".zip", ".SAFE")):
                logging.info("Unzipping file {}".format(myfile))
                zip_ref = zipfile.ZipFile(myfile, 'r')
                zip_ref.extractall(".")
                zip_ref.close()

    for myfile in os.listdir("."):
        if ".SAFE" in myfile:
            logging.info("Procesing directory {}".format(myfile))
            mytype = myfile[13:16]
            logging.info("Found image type {}".format(mytype))

            single_pol = None
            if "SSH" in mytype or "SSV" in mytype:
                logging.info("Found single pol file")
                single_pol = 1
            elif "SDV" in mytype:
                logging.info("Found multi-pol file")
                single_pol = 0
                if "hv" in pol or "hh" in pol:
                    logging.error("ERROR: no {} polarization exists in a {} file".format(pol, mytype))
                    sys.exit(1)
            elif "SDH" in mytype:
                logging.info("Found multi-pol file")
                single_pol = 0
                if "vh" in pol or "vv" in pol:
                    logging.error("ERROR: no {} polarization exists in a {} file".format(pol, mytype))
                    sys.exit(1)

            folder = myfile.replace(".SAFE", "")
            datelong = myfile.split("_")[5]
            acqdate = (myfile.split("_")[5].split("T"))[0]
            path = os.path.join(wrk, acqdate)
            if not os.path.exists(path):
                os.mkdir(path)

            logging.info("Folder is {}".format(folder))
            logging.info("Long date is {}".format(datelong))
            logging.info("Acquisition date is {}".format(acqdate))

            os.chdir("{}.SAFE".format(folder))

            if single_pol == 1:
                execute(make_cmd(1, acqdate, path), uselogging=True)
                execute(make_cmd(2, acqdate, path), uselogging=True)
                execute(make_cmd(3, acqdate, path), uselogging=True)
            else:
                execute(make_cmd(1, acqdate, path, pol=pol), uselogging=True)
                execute(make_cmd(2, acqdate, path, pol=pol), uselogging=True)
                execute(make_cmd(3, acqdate, path, pol=pol), uselogging=True)

            os.chdir(path)

            logging.info("Getting precision orbit for file {}".format(myfile))
            try:
                _ = downloadSentinelOrbitFile(myfile)
                execute("S1_OPOD_vec {}_001.slc.par *.EOF".format(acqdate))
                execute("S1_OPOD_vec {}_002.slc.par *.EOF".format(acqdate))
                execute("S1_OPOD_vec {}_003.slc.par *.EOF".format(acqdate))
            except Exception as e:
                print(f"Error: {e}")

            slc = glob.glob("*_00*.slc")
            slc.sort()
            par = glob.glob("*_00*.slc.par")
            par.sort()
            top = glob.glob("*_00*.tops_par")
            top.sort()
            with open(os.path.join(path, "SLC_TAB"), "w") as f:
                for i in range(len(slc)):
                    f.write("{} {} {}\n".format(slc[i], par[i], top[i]))

            # Make a raster version of swath 3
            width = getParameter("{}_003.slc.par".format(acqdate), "range_samples")
            execute("rasSLC {}_003.slc {} 1 0 50 10".format(acqdate, width))
            os.chdir(wrk)


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='par_s1_slc.py',
        description=__doc__,
    )
    parser.add_argument('pol', nargs='?', default='vv', help='name of polarization to process (default vv)')
    args = parser.parse_args()

    logFile = "par_s1_slc_log.txt"
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    par_s1_slc(args.pol)


if __name__ == "__main__":
    main()
