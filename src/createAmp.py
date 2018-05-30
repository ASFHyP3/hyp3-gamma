#!/usr/bin/env python

import saa_func_lib as saa
import numpy as np
import sys, os, re
import argparse

def createAmp(fi,nodata=None):
    (x,y,trans,proj,data) = saa.read_gdal_file(saa.open_gdal_file(fi))
    ampdata = np.sqrt(data)
    outfile = fi.replace('.tif','-amp.tif')
    print outfile
    saa.write_gdal_file_float(outfile,trans,proj,ampdata,nodata=nodata)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="creaetAmp.py",description="Convert Geotiff Power to Amplitude")
    parser.add_argument("infile",nargs="+",help="Input tif filename(s)")
    parser.add_argument("-n","--nodata",type=float,help="Set nodata value")
    args = parser.parse_args()

    infiles = args.infile
    for fi in infiles:
        createAmp(fi,args.nodata)

