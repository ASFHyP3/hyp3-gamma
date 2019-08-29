#!/usr/bin/python

import numpy as np
import saa_func_lib as saa
import glob
import os
import argparse
from getParameter import getParameter

def blank_bad_data(rawFile,x,y,left=15,right=15,cut=27):

    # Read in the data
    data = np.fromfile(rawFile,dtype=np.float32)
    data = np.reshape(data,(y,x))
    data = data.byteswap()

    # For each line in the file
    for i in xrange(y):
        # Black out the start of the line 
        for j in xrange(x):
            if data[i,j] != 0:
                data[i,:j+left] = 0
                break
        # Black out the end of the line 
        for j in xrange(x-1,0,-1):
            if data[i,j] != 0:
                data[i,j-right:] = 0
                break            

    # Any non-zero pixel is set to 1
    mask = np.zeros((y,x))
    mask[data>0.0] = 1
    
    # Sum up the rows of data
    sums = np.sum(mask,1)
    
    # Any line that has > x/2 pixels will not be blanked
    sums[sums>x/2]= 0
    
    # Any line that has < x/2 pixels is subject to blanking
    sums[sums>0] = 1
    
    # Scan the top of the file, blanking any lines that have
    # less than x/2 pixels and are within cut pixels of the edge
    for i in xrange(0,cut):
        if sums[i] == 1:
	    data[i,:] = 0
    
    # Scan the bottom of the file, blanking any lines that have
    # less than x/2 pixels and are within cut pixels of the edge
    for i in xrange(y-cut,y):
        if sums[i] == 1:
	    data[i,:] = 0

    # Write out the data	    
    data = data.byteswap()
    data.tofile(rawFile)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='blank_bad_data',description='Remove bad data values at the edge of an image')
    parser.add_argument('rawFile', help='name of input raw data file')
    parser.add_argument('parFile', help='name of input par file describing data')
    parser.add_argument('-l','--left',help='width of data to be blanked at left edge (def=15)',type=int,default=15)
    parser.add_argument('-r','--right',help='width of data to be blanked at right edge (def=15)',type=int,default=15)
    parser.add_argument('-c','--cut',help='width of data to be blanked at top/bottom edges (def=27)',type=int,default=27)

    args = parser.parse_args()

    if not os.path.exists(args.rawFile):
        print('ERROR: Raw input file (%s) does not exist!' % args.rawFile)
        exit(1)

    if not os.path.exists(args.parFile):
        print('ERROR: PAR input file (%s) does not exist!' % args.parFile)
        exit(1)

    x = int(getParameter(args.parFile,"range_samp_2"))
    y = int(getParameter(args.parFile,"az_samp_2"))

    blank_bad_data(args.rawFile,x,y,left=args.left,right=args.right,cut=args.cut)
    



