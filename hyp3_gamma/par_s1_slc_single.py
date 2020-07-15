"""Pre-process S1 SLC imagery into gamma format SLCs"""

import glob
import logging
import os

from hyp3lib import ExecuteError, OrbitDownloadError
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from hyp3lib.get_orb import download_sentinel_orbit_file


#
# This subroutine assembles the par_S1_SLC gamma commands
#
def make_cmd(val, acqdate, path, pol=None):
    if pol is None:
        m = glob.glob("measurement/s1*-iw{VAL}*".format(VAL=val))[0]
        n = glob.glob("annotation/s1*-iw{VAL}*".format(VAL=val))[0]
        o = glob.glob("annotation/calibration/calibration-s1*-iw{VAL}*".format(VAL=val))[0]
        p = glob.glob("annotation/calibration/noise-s1*-iw{VAL}*".format(VAL=val))[0]
    else:
        m = glob.glob("measurement/s1*-iw{VAL}*{POL}*".format(VAL=val, POL=pol))[0]
        n = glob.glob("annotation/s1*-iw{VAL}*{POL}*".format(VAL=val, POL=pol))[0]
        o = glob.glob("annotation/calibration/calibration-s1*-iw{VAL}*{POL}*".format(VAL=val, POL=pol))[0]
        p = glob.glob("annotation/calibration/noise-s1*-iw{VAL}*{POL}*".format(VAL=val, POL=pol))[0]
    cmd = "par_S1_SLC {m} {n} {o} {p} {path}/{acq}_00{VAL}.slc.par {path}/{acq}_00{VAL}.slc {path}/{acq}_00{VAL}.tops_par".format(
        acq=acqdate, m=m, n=n, o=o, p=p, VAL=val, path=path)
    return cmd


def par_s1_slc_single(myfile, pol=None, orbit_file=None):
    wrk = os.getcwd()

    if pol is None:
        pol = 'vv'

    logging.info("Procesing directory {}".format(myfile))
    mytype = myfile[13:16]
    logging.info("Found image type {}".format(mytype))

    if "SSH" in mytype or "SSV" in mytype:
        logging.info("Found single pol file")
        single_pol = 1
    elif "SDV" in mytype:
        logging.info("Found multi-pol file")
        single_pol = 0
        if "hv" in pol or "hh" in pol:
            logging.error("ERROR: no {} polarization exists in a {} file".format(pol, mytype))
            exit(1)
    elif "SDH" in mytype:
        logging.info("Found multi-pol file")
        single_pol = 0
        if "vh" in pol or "vv" in pol:
            logging.error("ERROR: no {} polarization exists in a {} file".format(pol, mytype))
            exit(1)

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

    if (single_pol == 1):
        cmd = make_cmd(1, acqdate, path)
        execute(cmd, uselogging=True)
        cmd = make_cmd(2, acqdate, path)
        execute(cmd, uselogging=True)
        cmd = make_cmd(3, acqdate, path)
        execute(cmd, uselogging=True)
    else:
        cmd = make_cmd(1, acqdate, path, pol=pol)
        execute(cmd, uselogging=True)
        cmd = make_cmd(2, acqdate, path, pol=pol)
        execute(cmd, uselogging=True)
        cmd = make_cmd(3, acqdate, path, pol=pol)
        execute(cmd, uselogging=True)

    os.chdir(path)

    # Fetch precision state vectors
    try:
        if orbit_file is None:
            logging.info('Trying to get orbit file information from file {}'.format(myfile))
            orbit_file, _ = download_sentinel_orbit_file(myfile)
        logging.info("Applying precision orbit information")
        execute("S1_OPOD_vec {}_001.slc.par {}".format(acqdate, orbit_file))
        execute("S1_OPOD_vec {}_002.slc.par {}".format(acqdate, orbit_file))
        execute("S1_OPOD_vec {}_003.slc.par {}".format(acqdate, orbit_file))
    except OrbitDownloadError:
        logging.warning('Unable to fetch precision state vectors... continuing')
    except ExecuteError:
        logging.warning(f'Unable to create *.slc.par files... continuing')

    slc = glob.glob("*_00*.slc")
    slc.sort()
    par = glob.glob("*_00*.slc.par")
    par.sort()
    top = glob.glob("*_00*.tops_par")
    top.sort()
    f = open(os.path.join(path, "SLC_TAB"), "w")
    for i in range(len(slc)):
        f.write("{} {} {}\n".format(slc[i], par[i], top[i]))
    f.close()

    #
    # Make a raster version of swath 3
    #
    width = getParameter("{}_003.slc.par".format(acqdate), "range_samples")
    execute("rasSLC {}_003.slc {} 1 0 50 10".format(acqdate, width))
    os.chdir(wrk)
