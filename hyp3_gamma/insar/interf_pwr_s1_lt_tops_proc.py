#!/usr/bin/python

import argparse
import logging
import os
import shutil
from execute import execute
from getParameter import getParameter

# 
# Create a new rslc tab
#
def create_slc2r_tab(SLC2tab,SLC2Rtab):
    if os.path.isfile(SLC2Rtab):
        os.remove(SLC2Rtab)
    f = open(SLC2tab,"rb")
    g = open(SLC2Rtab,"wb")
    with open(SLC2tab) as f:
        content = f.readlines()
        for item in content:
            item = item.rstrip()
            out = item.replace("slc","rslc")
            out = out.replace("tops","rtops")
            g.write("{}\n".format(out))
    g.close()
 
def coregister_data(cnt,SLC2tab,SLC2Rtab,spar,mpar,mmli,smli,ifgname,master,slave,lt,rlooks,alooks,iter):

    if (cnt < iter+1):
        offi = ifgname + ".off_{}".format(cnt)
    else:
        offi = ifgname + ".off.it.corrected.temp"

    if (cnt == 0):
        offit = "-"
    elif (cnt < iter+1):
        offit = ifgname + ".off.it"
    else:
        offit = ifgname + ".off.it.corrected"
    
    SLC1tab = "SLC1_tab"
    srslc = slave + ".rslc"
    srpar = slave + ".rslc.par" 

    cmd = "SLC_interp_lt_S1_TOPS {TAB2} {SPAR} {TAB1} {MPAR} {LT} {MMLI} {SMLI} {OFFIT} {TAB2R} {SRSLC} {SRPAR}".format(TAB1=SLC1tab,TAB2=SLC2tab,TAB2R=SLC2Rtab,SPAR=spar,MPAR=mpar,LT=lt,MMLI=mmli,SMLI=smli,SRSLC=srslc,SRPAR=srpar,OFFIT=offit)
    execute(cmd,uselogging=True)

    cmd = "create_offset {MPAR} {SPAR} {OFFI} 1 {RL} {AL} 0".format(MPAR=mpar,SPAR=spar,IFG=ifgname,RL=rlooks,AL=alooks,OFFI=offi)
    execute(cmd,uselogging=True)

    if (cnt < iter+1):
        cmd = "offset_pwr {M}.slc {S}.rslc {MPAR} {SRPAR} {OFFI} offs snr 256 64 offsets 1 64 256 0.2".format(M=master,S=slave,MPAR=mpar,SRPAR=srpar,IFG=ifgname,OFFI=offi)
    else:
        cmd = "offset_pwr {M}.slc {S}.rslc {MPAR} {SRPAR} {OFFI} offs snr 512 256 - 1 16 64 0.2".format(M=master,S=slave,MPAR=mpar,SRPAR=srpar,IFG=ifgname,OFFI=offi)
    execute(cmd,uselogging=True)

    cmd = "offset_fit offs snr {OFFI} - - 0.2 1".format(IFG=ifgname,OFFI=offi)
    log = open("offsetfit{}.log".format(cnt),"w")
    execute(cmd,uselogging=True,logfile=log)
    log.close()

    if (cnt < iter+1):
        cmd = "SLC_diff_intf {M}.slc {S}.rslc {MPAR} {SRPAR} {OFFI} {IFG}.sim_unw {IFG}.diff0.it{I} {RL} {AL} 0 0".format(M=master,S=slave,MPAR=mpar,SRPAR=srpar,IFG=ifgname,RL=rlooks,AL=alooks,OFFI=offi,I=cnt)
    else:
        cmd = "SLC_diff_intf {M}.slc {S}.rslc {MPAR} {SRPAR} {OFFI} {IFG}.sim_unw {IFG}.diff0.man {RL} {AL} 0 0".format(M=master,S=slave,MPAR=mpar,SRPAR=srpar,IFG=ifgname,RL=rlooks,AL=alooks,OFFI=offi)
    execute(cmd,uselogging=True)

    width = getParameter(offi,"interferogram_width")
    if (cnt < iter+1):
        cmd = "rasmph_pwr {IFG}.diff0.it{I} {M}.mli {W} 1 1 0 3 3".format(IFG=ifgname,M=master,W=width,I=cnt)
    else:
        cmd = "rasmph_pwr {IFG}.diff0.man {M}.mli {W} 1 1 0 3 3".format(IFG=ifgname,M=master,W=width,I=cnt)
    execute(cmd,uselogging=True)
    
    if (cnt == 0):
        offit = ifgname + ".off.it"
        shutil.copy(offi,offit)
    elif (cnt<iter+1):
        cmd = "offset_add {OFFIT} {OFFI} {OFFI}.temp".format(OFFIT=offit,OFFI=offi)
        execute(cmd,uselogging=True)
        shutil.copy("{}.temp".format(offi),offit)
    else:
        cmd = "offset_add {OFFIT} {OFFI} {OFFIT}.out".format(OFFIT=offit,OFFI=offi)
        execute(cmd,uselogging=True)

  
def interf_pwr_s1_lt_tops_proc(master,slave,dem,rlooks=10,alooks=2,iter=5,step=0):

    # Setup various file names that we'll need    
    ifgname = "{}_{}".format(master,slave)
    SLC2tab = "SLC2_tab"
    SLC2Rtab = "SLC2R_tab"
    lt = "{}.lt".format(master)
    mpar = master + ".slc.par"
    spar = slave + ".slc.par"
    mmli = master + ".mli.par"
    smli = slave + ".mli.par"
    off = ifgname + ".off_temp" 

    # Make a fresh slc2r tab
    create_slc2r_tab(SLC2tab,SLC2Rtab)

    if step == 0:
        if not os.path.isfile(dem):
            logging.info("Currently in directory {}".format(os.getcwd()))
            logging.error("ERROR: Input DEM file {} can't be found!".format(dem))
            exit(1)
        logging.info("Input DEM file {} found".format(dem))
        logging.info("Preparing initial look up table and sim_unw file")
        cmd = "create_offset {MPAR} {SPAR} {OFF} 1 {RL} {AL} 0".format(MPAR=mpar,SPAR=spar,OFF=off,RL=rlooks,AL=alooks)
        execute(cmd,uselogging=True)
        cmd = "rdc_trans {MMLI} {DEM} {SMLI} {LT}".format(MMLI=mmli,DEM=dem,SMLI=smli,M=master,LT=lt)
        execute(cmd,uselogging=True)
        cmd = "phase_sim_orb {MPAR} {SPAR} {OFF} {DEM} {IFG}.sim_unw {MPAR} -".format(MPAR=mpar,SPAR=spar,OFF=off,DEM=dem,IFG=ifgname,M=master)
        execute(cmd,uselogging=True)
    elif step == 1:
        logging.info("Starting initial coregistration with look up table")
        coregister_data(0,SLC2tab,SLC2Rtab,spar,mpar,mmli,smli,ifgname,master,slave,lt,rlooks,alooks,iter)
    elif step == 2:
        logging.info("Starting iterative coregistration with look up table")
        for n in range (1,iter+1):
            coregister_data(n,SLC2tab,SLC2Rtab,spar,mpar,mmli,smli,ifgname,master,slave,lt,rlooks,alooks,iter)
    elif step == 3:
        logging.info("Starting single interation coregistration with look up table")
        coregister_data(iter+1,SLC2tab,SLC2Rtab,spar,mpar,mmli,smli,ifgname,master,slave,lt,rlooks,alooks,iter)
    else:
        logging.error("ERROR: Unrecognized step {}; must be from 0 - 2".format(step))
        exit(1)     

if __name__ == '__main__':
    
  parser = argparse.ArgumentParser(prog='INTERF_PWR_S1_LT_TOPS_Proc.py',
    description='Sentinel-1 SLC data and DEM coregistration process')
  parser.add_argument("master",help='Master scene identifier')
  parser.add_argument("slave",help='Slave scene identifier')
  parser.add_argument("dem",help='Dem file in SAR coordinates (e.g. ./DEM/HGT_SAR_10_2)')
  parser.add_argument("-r","--rlooks",default=10,help="Number of range looks (def=10)",type=int)
  parser.add_argument("-a","--alooks",default=2,help="Number of azimuth looks (def=2)",type=int)
  parser.add_argument("-i","--iter",help='Number of coregistration iterations (def=5)',default=5,type=int)
  parser.add_argument("-s","--step",type=int,help='Procesing step: 0) Prepare LUT and SIM_UNW; 1) Initial co-registration with DEM; 2) iteration coregistration',default=0)
  args = parser.parse_args()

  logFile = "interf_pwr_s1_tops_proc_log.txt"
  logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
  logging.getLogger().addHandler(logging.StreamHandler())
  logging.info("Starting run")

  interf_pwr_s1_lt_tops_proc(args.master,args.slave,args.dem,rlooks=args.rlooks,alooks=args.alooks,iter=args.iter,step=args.step)
    

