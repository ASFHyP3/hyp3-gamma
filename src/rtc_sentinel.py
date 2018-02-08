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
from execute import execute 
    
def rtc_sentinel_gamma(outName,res=None,dem=None,matchFlag=None,deadFlag=None,gammaFlag=None,loFlag=None):

    string = "rtc_sentinel.pl "
    if dem is not None:
        string = string + "-e %s " % dem
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
    cmd = string + outName
    execute(cmd)


if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='rtc_sentinel',
    description='Creates an RTC image from a Sentinel 1 Scene using GAMMA software')
  parser.add_argument('output', help='base name of the output files')
  parser.add_argument("-o","--outputResolution",type=float,help="Desired output resolution")
  parser.add_argument("-e","--externalDEM",help="Specify a DEM file to use")
  parser.add_argument("-n",action="store_false",help="Do not perform matching")
  parser.add_argument("-d",action="store_true",help="if matching fails, use dead reckoning")
  parser.add_argument("-g",action="store_true",help="create gamma0 instead of sigma0");
  parser.add_argument("-l",action="store_true",help="create a lo-res output (30m)")
  args = parser.parse_args()

  rtc_sentinel_gamma(args.output,res=args.outputResolution,dem=args.externalDEM,matchFlag=args.n,
 			deadFlag=args.d,gammaFlag=args.g,loFlag=args.l)
			
