"""re-process S1 SLC imagery into gamma format SLCs"""

from __future__ import print_function, absolute_import, division, unicode_literals

import logging
import argparse
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
import os
import shutil


def SLC_copy_S1_fullSW(path,slcname,tabin,burst_tab,mode=2,dem=None,dempath=None,raml=10,azml=2):
    
    logging.info("Using range looks {}".format(raml))
    logging.info("Using azimuth looks {}".format(azml))
    logging.info("Operating in mode {}".format(mode))
    logging.info("In directory {}".format(os.getcwd()))

    if not os.path.isfile(tabin):
        logging.error("ERROR: Can't find tab file {} in {}".format(tabin,os.getcwd()))
    f = open(tabin,"r")    
    g = open("TAB_swFULL","w")
    for line in f:
        s = line.split()
        for i in range(len(s)):
            g.write("{} ".format(os.path.join(path,s[i])))
        g.write("\n")
    f.close()
    g.close()

    wrk = os.getcwd()

    cmd = "SLC_copy_S1_TOPS {} {} {}".format(tabin,"TAB_swFULL",burst_tab)
    execute(cmd,uselogging=True)

    shutil.copy(tabin,path)
    os.chdir(path)

    cmd = "SLC_mosaic_S1_TOPS {TAB} {SLC}.slc {SLC}.slc.par {RL} {AL}".format(TAB = tabin,
      SLC=slcname,RL=raml,AL=azml)
    execute(cmd,uselogging=True)

    width = getParameter("{}.slc.par".format(slcname),"range_samples")    
    cmd = "rasSLC {}.slc {} 1 0 50 10".format(slcname,width)
    execute(cmd,uselogging=True)

    cmd = "multi_S1_TOPS {TAB} {SLC}.mli {SLC}.mli.par {RL} {AL}".format(TAB=tabin,SLC=slcname,RL=raml,AL=azml)
    execute(cmd,uselogging=True)

    mode = int(mode)
    if mode == 1:
    
        logging.info("currently in {}".format(os.getcwd()))
        logging.info("creating directory DEM")
    
        if not os.path.exists("DEM"):
            os.mkdir("DEM")
        os.chdir("DEM")
        mliwidth = getParameter("../{}.mli.par".format(slcname),"range_samples")
        mlinline = getParameter("../{}.mli.par".format(slcname),"azimuth_lines")
   
        cmd = "GC_map_mod ../{SLC}.mli.par  - {DP}/{DEM}.par {DP}/{DEM}.dem 2 2 demseg.par demseg ../{SLC}.mli  MAP2RDC inc pix ls_map 1 1".format(SLC=slcname,DEM=dem,DP=dempath)
        execute(cmd,uselogging=True)

        demwidth = getParameter("demseg.par","width")

        cmd = "geocode MAP2RDC demseg {} HGT_SAR_{}_{} {} {}".format(demwidth,raml,azml,mliwidth,mlinline)
        execute(cmd,uselogging=True)

        cmd = "gc_map ../{SLC}.mli.par - {DP}/{DEM}.par 1 demseg.par demseg map_to_rdc 2 2 pwr_sim_map - - inc_flat".format(SLC=slcname,DP=dempath,DEM=dem)
        execute(cmd,uselogging=True)

        os.chdir("..")

    shutil.copy(tabin,"SLC{}_tab".format(mode))
    os.chdir(wrk)


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('outDir',help="Absolute path to destination folder")
    parser.add_argument('slcID',help="SLC identifier (e.g. 20150429)")
    parser.add_argument('slcTab',help='SLC Tab file')
    parser.add_argument('burstTab',help='Burst tab for which bursts to copy')
    parser.add_argument('mode',help='1 = master image, 2 = slave image')
    parser.add_argument('-d','--dem',help='Name of DEM file',dest="dem")
    parser.add_argument('-p','--path',help='Path to DEM file',dest="path")
    parser.add_argument('-rl','--rangelooks',default='10',help='Number of range looks',dest="rl") 
    parser.add_argument('-al','--azimuthlooks',default='2',help='Number of range looks',dest="al") 
    args = parser.parse_args()

    if not os.path.exists(args.slcTab):
        logging.error("ERROR:  Can't find slc tab file {}".format(args.slcTab))

    if not os.path.exists(args.burstTab):
        logging.error("ERROR:  Can't find burst tab file {}".format(args.burstTab))

    logFile = "SLC_copy_S1_fullSW_log.txt"
    logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    SLC_copy_S1_fullSW(
        args.outDir, args.slcID, args.slcTab, args.burstTab, args.mode, args.dem,
        args.path, args.rl, args.al
    )


if __name__ == '__main__':
    main()
