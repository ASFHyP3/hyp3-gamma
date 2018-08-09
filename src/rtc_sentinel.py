#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
###############################################################################
# rtc_sentinel.py
#
# Project:  APD HYP3
# Purpose:  Create RTC files using rtc_sentinel.pl
#  
# Author:   Tom Logan
#
# Issues/Caveats:
#
###############################################################################
# Copyright (c) 2017, Alaska Satellite Facility
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
# 
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
###############################################################################
import argparse
import os, sys
import glob
import saa_func_lib as saa
import logging

from execute import execute 
from get_dem import get_dem
from utm2dem import utm2dem
from get_bb_from_shape import get_bb_from_shape

def perform_sanity_checks():
    print "Performing sanity checks on output PRODUCTs"
    tif_list = glob.glob("PRODUCT/*.tif")
    for myfile in tif_list:
        if "vv" in myfile or "hh" in myfile or "vh" in myfile or "hv" in myfile:
            # Check that the main polarization file is on a 30 meter posting
            x,y,trans,proj = saa.read_gdal_file_geo(saa.open_gdal_file(myfile))    
            print "    trans[1] = {}; trans[5] = {}".format(trans[1],trans[5]) 
            if abs(trans[5]) > 10 and abs(trans[1]) > 10:
                print "Checking corner coordinates...",
                ul1 = trans[3]
                lr1 = trans[3] + y*trans[5]
                ul2 = trans[0]
                lr2 = trans[0] + x*trans[1]
                if abs((ul1/30.0) - int(ul1/30)) != 0.5:
                    print "ERROR: Corner coordinates are amiss"
                    print "ERROR: ul1 coordinate not on a 30 meter posting"
                    print "ERROR: ul1 = {}".format(ul1)
                    exit(1)
                if abs((lr1/30.0) - int(lr1/30)) != 0.5:
                    print "ERROR: Corner coordinates are amiss"
                    print "ERROR: lr1 coordinate not on a 30 meter posting"
                    print "ERROR: lr1 = {}".format(lr1)
                    exit(1)
                if abs((ul2/30.0) - int(ul2/30)) != 0.5:
                    print "ERROR: Corner coordinates are amiss"
                    print "ERROR: ul2 coordinate not on a 30 meter posting"
                    print "ERROR: ul2 = {}".format(ul2)
                    exit(1)
                if abs((lr2/30.0) - int(lr2/30)) != 0.5:
                    print "ERROR: Corner coordinates are amiss"
                    print "ERROR: lr2 coordinate not on a 30 meter posting"
                    print "ERROR: lr2 = {}".format(lr2)
                    exit(1)
                print "...ok"




def rtc_sentinel_gamma(outName,res=None,dem=None,aoi=None,shape=None,matchFlag=None,
                       deadFlag=None,gammaFlag=None,loFlag=None,pwrFlag=None,
                       filtFlag=None,looks=None):

    string = "rtc_sentinel.pl "
    if dem is not None:
        string = string + "-e %s " % dem
    if shape is not None:
        minX,minY,maxX,maxY = get_bb_from_shape(shape)
        print minX,minY,maxX,maxY
        aoi = []
        aoi.append(minX)
        aoi.append(minY)
        aoi.append(maxX)
        aoi.append(maxY)
        print aoi
    if aoi is not None:
        tifdem = "tmp_{}_dem.tif".format(os.getpid())
        get_dem(aoi[0],aoi[1],aoi[2],aoi[3],tifdem,True,post=30)
        gammadem = "big.dem"  
        utm2dem(tifdem,gammadem,"big.dem.par")
        os.remove(tifdem)
        string = string + "-e {} ".format(gammadem)
    if res is not None:
        string = string + "-o %s " % res
    if not matchFlag:
        string = string + "-n "
    if deadFlag:
        string = string + "-d "
    if gammaFlag:
        string = string + "-g "
    if loFlag:
        string = string + "-l "
    if pwrFlag:
        string = string + "-p "
    if filtFlag:
        string = string + "-f "
    if looks is not None:
        string = string + "-k %s " % looks
    cmd = string + outName
    execute(cmd)

    perform_sanity_checks()


if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='rtc_sentinel',
    description='Creates an RTC image from a Sentinel 1 Scene using GAMMA software')
  parser.add_argument('output', help='base name of the output files')
  parser.add_argument("-o","--outputResolution",type=float,help="Desired output resolution")
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-e","--externalDEM",help="Specify a DEM file to use")
  group.add_argument("-a","--aoi",help="Specify AOI to use",type=float,nargs=4,metavar=('LON_MIN','LAT_MIN','LON_MAX','LAT_MAX'))
  group.add_argument("-s","--shape",help="Specify shape file to use")
  parser.add_argument("-n",action="store_false",help="Do not perform matching")
  parser.add_argument("-d",action="store_true",help="if matching fails, use dead reckoning")
  parser.add_argument("-g",action="store_true",help="create gamma0 instead of sigma0");
  parser.add_argument("-l",action="store_true",help="create a lo-res output (30m)")
  parser.add_argument("-p",action="store_true",help="create power images instead of amplitude")
  parser.add_argument("-f",action="store_true",help="run enhanced lee filter")
  parser.add_argument("-k","--looks",type=int,help="set the number of looks to take")
  args = parser.parse_args()

  rtc_sentinel_gamma(args.output,res=args.outputResolution,dem=args.externalDEM,
                     aoi=args.aoi,shape=args.shape,matchFlag=args.n,deadFlag=args.d,
                     gammaFlag=args.g,loFlag=args.l,pwrFlag=args.p,filtFlag=args.f,
                     looks=args.looks)
			
