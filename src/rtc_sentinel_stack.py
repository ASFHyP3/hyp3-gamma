#!/usr/bin/python
import logging
import os, sys
import argparse
import shutil
import zipfile
import math
import osr
import glob
import datetime
import numpy as np
from osgeo import gdal
from lxml import etree

import saa_func_lib as saa
from byteSigmaScale import byteSigmaScale
from createAmp import createAmp
from getSubSwath import get_bounding_box_file
from execute import execute
from getParameter import getParameter
from makeAsfBrowse import makeAsfBrowse
from ingest_S1_granule import ingest_S1_granule
from rtc2color import rtc2color
from asf_geometry import geometry_geo2proj
from getBursts import getBursts
from make_arc_thumb import pngtothumb
from rtc_sentinel import rtc_sentinel_gamma

def create_dem_par_files(infiles):
    dpar_files = []
    for fi in infiles:
        basename = fi.replace(".SAFE","")
        dataType = "float"
        pixel_size = 30
        lat_max,lat_min,lon_max,lon_min = get_bounding_box_file(fi)
        post = 30
        create_dem_par(basename,dataType,pixel_size,lat_max,lat_min,lon_max,lon_min,post)
        dpar_files.append(basename+".par")

def create_dem_par(basename,dataType,pixel_size,lat_max,lat_min,lon_max,lon_min,post):
    demParIn = "{}_dem_par.in".format(basename)
    zone, false_north, y_min, y_max, x_min, x_max = geometry_geo2proj(lat_max,lat_min,lon_max,lon_min)
    logging.debug("Original Output Coordinates: {} {} {} {}".format(y_min, y_max, x_min, x_max))
    if post is not None:
        x_max = math.ceil(x_max/post)*post
        x_min = math.floor(x_min/post)*post
        y_max = math.ceil(y_max/post)*post
        y_min = math.floor(y_min/post)*post
        logging.debug("Snapped Output Coordinates: {} {} {} {}".format(y_min, y_max, x_min, x_max))

    f = open(demParIn,"w")
    f.write("UTM\n")
    f.write("WGS84\n")
    f.write("1\n")
    f.write("{}\n".format(zone))
    f.write("{}\n".format(false_north))
    f.write("{}\n".format(basename))
    if "float" in dataType:
        f.write("REAL*4\n")
    elif "int16" in dataType:
        f.write("INTEGER*2\n")
    f.write("0.0\n")
    f.write("1.0\n")

    xsize = np.floor(abs((x_max-x_min)/pixel_size))
    ysize = np.floor(abs((y_max-y_min)/pixel_size))

    f.write("{}\n".format(int(xsize)))
    f.write("{}\n".format(int(ysize)))
    f.write("{} {}\n".format(-1.0*pixel_size,pixel_size))
    f.write("{} {}\n".format(y_max,x_min))
    f.close()

    return demParIn

def ingest_raw_stack(infiles,res,look_fact):
  logging.info("Infile list: {}".format(infiles))
  mgrd_list = []
  for x in xrange(len(infiles)):
      infile = infiles[x]
      if not os.path.exists(infile):
          logging.error("ERROR: Input file {} does not exist".format(infile))
          exit(1)
      if "zip" in infile:
          logging.info("Unzipping file {}".format(infile))
          zip_ref = zipfile.ZipFile(infile, 'r')
          zip_ref.extractall(".")
          zip_ref.close()    
          infiles[x] = infile.replace(".zip",".SAFE")
          infile = infile.replace(".zip",".SAFE")

      if "SDV" in infile or "SSV" in infile:
          outfile = ingest_tiff(infile,"VV",look_fact)
          mgrd_list.append(outfile)
      else:
          outfile = ingest_tiff(infile,"HH",look_fact)
          mgrd_list.append(outfile)

  return(mgrd_list,infiles)

def ingest_tiff(infile,pol,look_fact):
    fi = glob.glob("{}/*/*{}*.tiff".format(infile,pol.lower()))[0]
    if not fi:
        logging.error("Unable to find input file {}/*/*{}*.tif".format(infile,pol.lower()))
        exit(1)
    outf = fi.split("/")[-1]
    outfile = outf.split(".")[0]
    outfile = outfile + ".mgrd"
    if os.path.isfile(outfile):
        logging.info("Output file {} already exists. Skipping.".format(outfile))
    else:
        logging.info("Creating output file {}".format(outfile))
        ingest_S1_granule(infile,"VV",look_fact,outfile)
        # remove EOF file for next iteration
        for eof in glob.glob("*.EOF"):
            os.remove(eof)
    return outfile
         
	
def create_diff_par_in():
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "config"))
    f = open("{}/diff_par.in".format(cfgdir),"r")
    outfile = "diff_par.in"
    g = open(outfile,"w")
    for line in f:
        g.write("{}".format(line))
    f.close()
    g.close()
    return(outfile)

def get_dates(file_list,sep="-"):
    date_and_file = []
    for fi in file_list:
        string = fi.split(sep)[4]
	date = string.split(sep)[0].upper()
	m = [fi,date]
	date_and_file.append(m)
    date_and_file.sort(key = lambda row: row[1])
    files = []
    dates = []
    for x in xrange(len(date_and_file)):
        files.append(date_and_file[x][0])
        dates.append(date_and_file[x][1])  
    return(files,dates)


def rtc_granule(fi,prod_dir,res,look_fact,stack=None,dem=None,match=True):
    back = os.getcwd()
    mydir = os.path.basename(fi)
    mydir = mydir.replace(".SAFE","")
    mydir = mydir[17:32]
    if os.path.exists(mydir):
        logging.info("Old {} directory found; deleting".format(mydir))
        shutil.rmtree(mydir)
    os.mkdir(mydir)
    os.chdir(mydir)
    os.symlink("../{}".format(fi),fi)

    rtc_sentinel_gamma(fi,matchFlag=match,deadFlag=True,gammaFlag=True,res=res,pwrFlag=True,looks=look_fact,
                       terms=1,noCrossPol=True,dem=dem,stack=stack)

#    for tmp in glob.glob("PRODUCT/*_V*.tif"):
#        shutil.copy(tmp,prod_dir)
#    for tmp in glob.glob("PRODUCT/*_H*.tif"):
#        shutil.copy(tmp,prod_dir)

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

    logging.info("Pass List: {}".format(p_list))
    logging.info("Fail List: {}".format(f_list))

    # If we have a mixed stack, re-run the granules that passed with no matching
    if len(f_list) != 0 and len(p_list) !=0:
        logging.info("Found mixed stack; reprocessing passing files with no matching")
        for di in p_list:
            safe = glob.glob("{}/*.SAFE".format(di))[0]
            logging.info("Re-processing file {}".format(os.path.basename(safe)))
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
            par = glob.glob("{}/geo_VV/image.diff_par".format(di))
            azi[cnt],rng[cnt] = get_poly(par)
            logging.info("{} : {} : {}",di,rng[cnt],azi[cnt])
            cnt = cnt + 1
        med_rng = np.median(rng)
        med_azi = np.median(azi)
        logging.info("Offset medians: {},{} (rng/azi)".format(med_rng,med_azi))
        for di in p_list:
            par = glob.glob("{}/geo_VV/image.diff_par")
            azi1,rng1 = get_poly(par)
            safe = glob.glob("{}/*.SAFE".format(di))[0]
            safe = os.path.basename(safe)
            if np.abs(rng1-med_rng)>tolerance:
                logging.info("Outlier found: {}; reprocessing with ({},{}) rng/azi offsets".format(di,med_rng,med_azi))

                # Replace the rng,azi polynomial with the median
                fix_diff_par(par,med_rng,med_azi)

                # Next is to re-run the granule using the modified diff_par file
                new_dir = rtc_granule(safe,prod_dir,res,look_fact,match=True,stack=par)
 		



if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='ingest_stack',description="ingest a stack of S1 GRD images")
  parser.add_argument("infile",nargs="+",help="zip files or SAFE directories")
  parser.add_argument("-r","--res",type=float,default=30,help="Desired output pixel spacing for stack (default 30m)")
  parser.add_argument("-t","--tolerance",type=float,default=2.0,help="Tolerance for required re-run (default 3.0)")
  args = parser.parse_args()

  logFile = "{}_{}_log.txt".format("ingest_stack",os.getpid())
  logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
  logging.getLogger().addHandler(logging.StreamHandler())
  logging.info("Starting run")

  rtc_sentinel_stack(args.infile,args.res,args.tolerance)

