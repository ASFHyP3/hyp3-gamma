"""Pre-process S1 SLC imagery into gamma format SLCs"""

from __future__ import print_function, absolute_import, division, unicode_literals

import logging
import argparse
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
import os
import glob
from hyp3lib.get_orb import downloadSentinelOrbitFile

#
# This subroutine assembles the par_S1_SLC gamma commands
#
def make_cmd(val,acqdate,path,pol=None):
    if pol is None:
        m = glob.glob("measurement/s1*-iw{VAL}*".format(VAL=val))[0]
        n = glob.glob("annotation/s1*-iw{VAL}*".format(VAL=val))[0]
        o = glob.glob("annotation/calibration/calibration-s1*-iw{VAL}*".format(VAL=val))[0]
        p = glob.glob("annotation/calibration/noise-s1*-iw{VAL}*".format(VAL=val))[0]
    else:
        m = glob.glob("measurement/s1*-iw{VAL}*{POL}*".format(VAL=val,POL=pol))[0]
        n = glob.glob("annotation/s1*-iw{VAL}*{POL}*".format(VAL=val,POL=pol))[0]
        o = glob.glob("annotation/calibration/calibration-s1*-iw{VAL}*{POL}*".format(VAL=val,POL=pol))[0]
        p = glob.glob("annotation/calibration/noise-s1*-iw{VAL}*{POL}*".format(VAL=val,POL=pol))[0]
    cmd = "par_S1_SLC {m} {n} {o} {p} {path}/{acq}_00{VAL}.slc.par {path}/{acq}_00{VAL}.slc {path}/{acq}_00{VAL}.tops_par".format(acq=acqdate,m=m,n=n,o=o,p=p,VAL=val,path=path) 
    return cmd


def par_s1_slc_single(myfile, pol=None):

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
             logging.error("ERROR: no {} polarization exists in a {} file".format(pol,mytype))
             exit(1)
    elif "SDH" in mytype:
         logging.info("Found multi-pol file")
         single_pol = 0
         if "vh" in pol or "vv" in pol:
             logging.error("ERROR: no {} polarization exists in a {} file".format(pol,mytype))
             exit(1)

    folder = myfile.replace(".SAFE","")
    datelong = myfile.split("_")[5]
    acqdate = (myfile.split("_")[5].split("T"))[0]
    path = os.path.join(wrk,acqdate)
    if not os.path.exists(path):
        os.mkdir(path)

    logging.info("Folder is {}".format(folder))
    logging.info("Long date is {}".format(datelong))
    logging.info("Acquisition date is {}".format(acqdate))

    os.chdir("{}.SAFE".format(folder))

    if (single_pol == 1):
        cmd = make_cmd(1,acqdate,path)
        execute(cmd,uselogging=True)
        cmd = make_cmd(2,acqdate,path)
        execute(cmd,uselogging=True)
        cmd = make_cmd(3,acqdate,path)
        execute(cmd,uselogging=True)
    else:
        cmd = make_cmd(1,acqdate,path,pol=pol)
        execute(cmd,uselogging=True)
        cmd = make_cmd(2,acqdate,path,pol=pol)
        execute(cmd,uselogging=True)
        cmd = make_cmd(3,acqdate,path,pol=pol)
        execute(cmd,uselogging=True)

    os.chdir(path)

    # Fetch precision state vectors
    try:
        logging.info("Getting precision orbit information")
        orb,tmp = downloadSentinelOrbitFile(myfile)
        logging.info("Applying precision orbit information")
        execute("S1_OPOD_vec {}_001.slc.par {}".format(acqdate,orb))
        execute("S1_OPOD_vec {}_002.slc.par {}".format(acqdate,orb))
        execute("S1_OPOD_vec {}_003.slc.par {}".format(acqdate,orb))
    except:
        logging.warning("Unable to fetch precision state vectors... continuing")

    slc = glob.glob("*_00*.slc")
    slc.sort()
    par = glob.glob("*_00*.slc.par")
    par.sort()
    top = glob.glob("*_00*.tops_par")
    top.sort()
    f = open(os.path.join(path,"SLC_TAB"),"w")
    for i in range(len(slc)):
        f.write("{} {} {}\n".format(slc[i],par[i],top[i]))
    f.close()

    #
    # Make a raster version of swath 3
    #
    width = getParameter("{}_003.slc.par".format(acqdate),"range_samples")
    execute("rasSLC {}_003.slc {} 1 0 50 10".format(acqdate,width))
    os.chdir(wrk)


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('infile', help='input SAFE file name')
    parser.add_argument('-p', '--pol', default='vv', help='name of polarization to process (default vv)')
    args = parser.parse_args()

    logFile = "par_s1_slc_single_log.txt"
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    par_s1_slc_single(args.infile, args.pol)


if __name__ == '__main__':
    main()

