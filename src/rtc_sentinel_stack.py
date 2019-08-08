#!/usr/bin/python
import logging
import os, sys
import argparse
import shutil
import glob
import numpy as np

from getParameter import getParameter
from rtc_sentinel import rtc_sentinel_gamma

def rtc_granule(fi,prod_dir,res,look_fact,stack=None,dem=None,match=True):
    back = os.getcwd()
    mydir = os.path.basename(fi)
    mydir = mydir.replace(".SAFE","")
    mydir = mydir[17:32]
    if os.path.exists(mydir):
        logging.info("Old {} directory found; deleting".format(mydir))
        shutil.rmtree(mydir)
    logging.info("Creating directory {} for {}".format(mydir,fi))
    os.mkdir(mydir)
    os.chdir(mydir)
    os.symlink("../{}".format(fi),fi)

    rtc_sentinel_gamma(fi,matchFlag=match,deadFlag=True,gammaFlag=True,res=res,pwrFlag=True,looks=look_fact,
                       terms=1,noCrossPol=True,dem=dem,stack=stack)

    for tmp in glob.glob("PRODUCT/*_V*.tif"):
        shutil.copy(tmp,prod_dir)
    for tmp in glob.glob("PRODUCT/*_H*.tif"):
        shutil.copy(tmp,prod_dir)

    os.chdir(back)
    return(mydir)


def fix_diff_par(diff_par,rng_med,azi_med):
    f = open(diff_par,"r")
    outfile = diff_par.replace(".par","") + "_accum.par"
    g = open(outfile,"w")
    for line in f:
        if "range_offset_polynomial" in line:
            g.write("range_offset_polynomial: {} 0.0 0.0 0.0 0.0 0.0\n".format(rng_med))
        elif "azimuth_offset_polynomial" in line:
            g.write("azimuth_offset_polynomial: {} 0.0 0.0 0.0 0.0 0.0\n".format(azi_med))
        else:
            g.write("{}".format(line))
    f.close()
    g.close()
    return outfile

def get_poly(diff_par):
     polyra = getParameter(diff_par,"range_offset_polynomial",uselogging=True)
     polyaz = getParameter(diff_par,"azimuth_offset_polynomial",uselogging=True)
     ra_new = float(polyra.split()[0])
     az_new = float(polyaz.split()[0])
     return az_new,ra_new

def check_coreg(di):
    fi = "{}/coreg_check.log".format(di)
    f = open(fi,"r")
    for line in f:
        if "Granule passed" in line: 
            pf = True 
        elif "Granule failed" in line: 
            pf = False
    f.close()
    return pf

def rtc_sentinel_stack(infiles,res,tol):

    if res == 10.0:
        look_fact = 1
    else: 
        look_fact = int(res/10.0) * 2

    prod_dir = os.path.join(os.getcwd(),"RTC_PRODUCTS")
    if not os.path.exists(prod_dir):
        os.mkdir(prod_dir)

    # Run RTC on entire stack
    logging.info("Preparing initial RTC stack")
    f_list = []
    p_list = [] 
    for fi in infiles:
        logging.info("Running granule {}".format(fi))
        new_dir = rtc_granule(fi,prod_dir,res,look_fact,match=True)
        pf = check_coreg(new_dir)
        if pf == False:
            f_list.append(new_dir)
        else:
            p_list.append(new_dir)
        if "zip" in fi:
            safe = fi.replace(".zip",".SAFE")
            shutil.move("{}/{}".format(new_dir,safe),safe)

    logging.info("Pass List: {}".format(p_list))
    logging.info("Fail List: {}".format(f_list))

    # If we have a mixed stack, re-run the granules that passed with no matching
    if len(f_list) != 0 and len(p_list) !=0:
        logging.info("Found mixed stack; reprocessing passing files with no matching")
        for di in p_list:
            safe = glob.glob("*{}*.SAFE".format(di))[0]
            logging.info("Re-processing file {}".format(safe))
            new_dir = rtc_granule(safe,prod_dir,res,look_fact,match=False)
            if new_dir != di: 
                logging.error("ERROR!!!  You should never see this")
    
    # If all success, check for outliers and reprocess
    if len(f_list) == 0:
        logging.info("Found stack that passed coregistration; looking for outliers") 
        rng = np.zeros(len(p_list))
        azi = np.zeros(len(p_list))
        cnt = 0 
        for di in p_list:
            par = glob.glob("{}/geo_VV/image.diff_par".format(di))[0]
            azi[cnt],rng[cnt] = get_poly(par)
            logging.info("{} : {} : {}",di,rng[cnt],azi[cnt])
            cnt = cnt + 1
        med_rng = np.median(rng)
        med_azi = np.median(azi)
        logging.info("Offset medians: {},{} (rng/azi)".format(med_rng,med_azi))
        for di in p_list:
            par = glob.glob("{}/geo_VV/image.diff_par")[0]
            azi1,rng1 = get_poly(par)
            safe = glob.glob("*{}*.SAFE".format(di))[0]
            safe = os.path.basename(safe)
            if np.abs(rng1-med_rng)>tol:
                logging.info("Outlier found: {}; reprocessing with ({},{}) rng/azi offsets".format(di,med_rng,med_azi))

                # Replace the rng,azi polynomial with the median
                fix_diff_par(par,med_rng,med_azi)

                # Next is to re-run the granule using the modified diff_par file
                new_dir = rtc_granule(safe,prod_dir,res,look_fact,match=True,stack=par)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='rtc_sentinel_stack',description="RTC a stack of S1 images")
  parser.add_argument("infile",nargs="+",help="zip files or SAFE directories")
  parser.add_argument("-r","--res",type=float,default=30,help="Desired output pixel spacing for stack (default 30m)")
  parser.add_argument("-t","--tolerance",type=float,default=2.0,help="Tolerance for required re-run (default 2.0)")
  args = parser.parse_args()

  logFile = "{}_{}_log.txt".format("ingest_stack",os.getpid())
  logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
  logging.getLogger().addHandler(logging.StreamHandler())
  logging.info("Starting run")

  rtc_sentinel_stack(args.infile,args.res,args.tolerance)

