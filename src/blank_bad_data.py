#!/usr/bin/python

import numpy as np
import saa_func_lib as saa
import glob
import os
import argparse
from getParameter import getParameter

def blank_bad_data(rawFile,x,y,left=10,right=10):

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

    data = data.byteswap()
    data.tofile(rawFile)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='blank_bad_data',description='Remove bad data values at the edge of an image')
    parser.add_argument('rawFile', help='name of input raw data file')
    parser.add_argument('parFile', help='name of input par file describing data')
    parser.add_argument('-l','--left',help='width of data to be blanked at left edge (def=10)',type=int,default=10)
    parser.add_argument('-r','--right',help='width of data to be blanked at right edge (def=10)',type=int,default=10)
    args = parser.parse_args()

    if not os.path.exists(args.rawFile):
        print('ERROR: Raw input file (%s) does not exist!' % args.rawFile)
        exit(1)

    if not os.path.exists(args.parFile):
        print('ERROR: PAR input file (%s) does not exist!' % args.parFile)
        exit(1)

    x = int(getParameter(args.parFile,"range_samp_1"))
    y = int(getParameter(args.parFile,"az_samp_1"))
    blank_bad_data(args.rawFile,x,y,left=args.left,right=args.right)


