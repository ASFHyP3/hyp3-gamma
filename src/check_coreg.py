#!/usr/bin/python

import os, re
import argparse
import logging
import numpy as np
import glob
from getParameter import getParameter

def calc(s,l,r,a):
    rpt = r[0] + r[1]*s + r[2]*l + r[3]*s*l + r[4]*s*s + r[5]*l*l
    apt = a[0] + a[1]*s + a[2]*l + a[3]*s*l + a[4]*s*s + a[5]*l*l
    
    print rpt, apt
    return rpt, apt

def display(str,f,ERROR=False):
    
    if ERROR:
        logging.error("{}".format(str))
    else:
        logging.info("{}".format(str))
    f.write("{}\n".format(str))

def check_coreg(input,post,max_offset=50,max_error=2):

    f = open('coreg_check.log','w')

    display("SAR file: {}".format(input),f)
    display("Checking coregistration using {} meters".format(post),f)
    display("Setting maximum offset to be {}".format(max_offset),f)
    display("Setting maximum error to be {}".format(max_error),f)

    myfile = "mk_geo_radcal_2.log"
    if os.path.isdir("geo_HH"):
        mlog = "geo_HH/{}".format(myfile)
    elif os.path.isdir("geo_hh"):
        mlog = "geo_hh/{}".format(myfile)
    elif os.path.isdir("geo_VV"):
        mlog = "geo_VV/{}".format(myfile)
    elif os.path.isdir("geo_vv"):
        mlog = "geo_vv/{}".format(myfile)
    elif os.path.isdir("geo"):
        mlog = "geo/{}".format(myfile)
    else:
        display("ERROR: Can't find {}".format(myfile),f,ERROR=True)
        f.close()
	exit(-1)

    a = np.zeros(6)
    r = np.zeros(6)
    
    g = open(mlog,"r")
    for line in g:
        if 'final range offset poly. coeff.:' in line:
	    tmp = re.split(":",line)
	    vals = tmp[1].split()
	    if len(vals) == 1:
	        r[0] = float(vals[0])
		display("Range offset is {}".format(r),f)
	    elif len(vals) == 3:
	        r[0] = float(vals[0])
	        r[1] = float(vals[1])
	        r[2] = float(vals[2])
		display("Range polynomial is {}".format(r),f)
            elif len(vals) == 6:
	        r[0] = float(vals[0])
	        r[1] = float(vals[1])
	        r[2] = float(vals[2])
	        r[3] = float(vals[3])
	        r[4] = float(vals[4])
	        r[5] = float(vals[5])
		display("Range polynomial is {}".format(r),f)

	if 'final azimuth offset poly. coeff.:' in line:
	    tmp = re.split(":",line)
	    vals = tmp[1].split()
	    if len(vals) == 1:
	        a[0] = float(vals[0])
		display("Azimuth offset is {}".format(a),f)
	    elif len(vals) == 3:
	        a[0] = float(vals[0])
	        a[1] = float(vals[1])
	        a[2] = float(vals[2])
		display("Azimuth polynomial is {}".format(a),f)
            elif len(vals) == 6:
	        a[0] = float(vals[0])
	        a[1] = float(vals[1])
	        a[2] = float(vals[2])
	        a[3] = float(vals[3])
	        a[4] = float(vals[4])
	        a[5] = float(vals[5])
		display("Azimuth polynomial is {}".format(a),f)
	
        if 'final model fit std. dev. (samples) range:' in line:
	    tmp = re.split(":",line)
	    vals = tmp[1].split()
	    rng_error = float(vals[0])
	    val = tmp[2].strip()
	    azi_error = float(val)
	    display("Range std dev: {}  Azimuth std dev: {}".format(rng_error,azi_error),f)
	    error = np.sqrt(rng_error*rng_error+azi_error*azi_error)
	    display("error is {}".format(error),f)
	    if error > max_error:
	        display("error > max_error",f)
	        display("std dev is too high, using dead reckoning",f)
		display("Granule failed coregistration",f)
                f.close()
		exit(-1)
    g.close()
	
    mlog = glob.glob('geo_??/*.diff_par')[0]
    if mlog:
        platform = "NOT_LEGACY"
    else:
        mlog = glob.glob('geo/*.diff_par')[0]
	if mlog:
	    platform = "LEGACY"
	else:
	    log.error("Can't find diff_par file")
	    return(-1)
    
    if os.path.exists(mlog):
        ns = int(getParameter(mlog,"range_samp_1"))
	display("Number of samples is {}".format(ns),f)
	nl = int(getParameter(mlog,"az_samp_1"))
	display("Number of lines is {}".format(nl),f)
    else:
        log.error("Can't find diff par file {}".format(log))
	f.close()
        exit(-1)
 
    rpt,apt = calc(1,1,r,a)
    pt1 = np.sqrt(rpt*rpt+apt*apt)
    display("Point 1 offset is {}".format(pt1),f)
    
    rpt,apt = calc(ns,1,r,a)
    pt2 = np.sqrt(rpt*rpt+apt*apt)
    display("Point 2 offset is {}".format(pt2),f)
    
    rpt,apt = calc(1,nl,r,a)
    pt3 = np.sqrt(rpt*rpt+apt*apt)
    display("Point 3 offset is {}".format(pt3),f)
    
    rpt,apt = calc(ns,nl,r,a)
    pt4 = np.sqrt(rpt*rpt+apt*apt)
    display("Point 4 offset is {}".format(pt4),f)
    
    top = max(pt1,pt2,pt3,pt4)
    offset = top * post
    
    display("Found absolute offset of {} meters".format(offset),f)
    if offset < max_offset:
        display("...keeping offset",f)
	ret = 0
    else:
        display("offset too large, using dead reckoning",f)
	ret = -1

    if ret == 0:
        display("Granule passed coregistration",f)
	return(0)
    else:
        display("Granule failed coregistration",f)
        f.close()
        exit(-1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='check_coreg',
      description='Checks results of Gamma RTC coregistration process')
    parser.add_argument('input',help='Name of input SAR file')
    parser.add_argument('post',help='Posting of the SAR image',type=float)
    parser.add_argument('-o','--max_offset',help='Set the maximum allowable max_offset (meters)',type=float,default=50)
    parser.add_argument('-e','--max_error',help='Set the maximum allowable standard deviation of max_offset fit (pixels)',type=int,default=2)
    args = parser.parse_args()

    logFile = "check_coreg.log"
    logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    check_coreg(args.input,args.post,args.max_offset,args.max_error)
    
