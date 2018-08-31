#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
###############################################################################
# rtc_sentinel.py
#
# Project:  APD HYP3
# Purpose:  Create RTC files using GAMMA software
#  
# Author:   Tom Logan
#
# Issues/Caveats:
#
###############################################################################
# Copyright (c) 2018, Alaska Satellite Facility
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
import logging
import zipfile
import shutil
import numpy as np
from osgeo import gdal
import datetime

import saa_func_lib as saa
from execute import execute 
from get_dem import get_dem
from utm2dem import utm2dem
from get_bb_from_shape import get_bb_from_shape
from getDemFor import getDemFile
from createAmp import createAmp
from byteSigmaScale import byteSigmaScale
from makeAsfBrowse import makeAsfBrowse
from check_coreg import check_coreg
from rtc2color import rtc2color
from xml2meta import sentinel2meta
from asf_utils import write_asf_meta
from copy_metadata import copy_metadata
from par_s1_slc_single import par_s1_slc_single
from SLC_copy_S1_fullSW import SLC_copy_S1_fullSW
from getBursts import getBursts
from make_arc_thumb import pngtothumb

def perform_sanity_checks():
    logging.info("Performing sanity checks on output PRODUCTs")
    tif_list = glob.glob("PRODUCT/*.tif")
    for myfile in tif_list:
        if "vv" in myfile or "hh" in myfile or "vh" in myfile or "hv" in myfile:
            # Check that the main polarization file is on a 30 meter posting
            x,y,trans,proj = saa.read_gdal_file_geo(saa.open_gdal_file(myfile))    
            logging.debug("    trans[1] = {}; trans[5] = {}".format(trans[1],trans[5]))
            if abs(trans[5]) > 10 and abs(trans[1]) > 10:
                logging.debug("Checking corner coordinates...")
                ul1 = trans[3]
                lr1 = trans[3] + y*trans[5]
                ul2 = trans[0]
                lr2 = trans[0] + x*trans[1]
                if abs((ul1/30.0) - int(ul1/30)) != 0.5:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: ul1 coordinate not on a 30 meter posting")
                    logging.error("ERROR: ul1 = {}".format(ul1))
                    exit(1)
                if abs((lr1/30.0) - int(lr1/30)) != 0.5:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: lr1 coordinate not on a 30 meter posting")
                    logging.error("ERROR: lr1 = {}".format(lr1))
                    exit(1)
                if abs((ul2/30.0) - int(ul2/30)) != 0.5:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: ul2 coordinate not on a 30 meter posting")
                    logging.error("ERROR: ul2 = {}".format(ul2))
                    exit(1)
                if abs((lr2/30.0) - int(lr2/30)) != 0.5:
                    logging.error("ERROR: Corner coordinates are amiss")
                    logging.error("ERROR: lr2 coordinate not on a 30 meter posting")
                    logging.error("ERROR: lr2 = {}".format(lr2))
                    exit(1)
                logging.debug("...ok")


def report_kwargs(inName,outName,res,dem,aoi,shape,matchFlag,deadFlag,gammaFlag,loFlag,
                  pwrFlag,filterFlag,looks):
    
    logging.info("Parameters for this run:")
    logging.info("    Input name                        : {}".format(inName))
    logging.info("    Output name                       : {}".format(outName))
    logging.info("    Output resolution                 : {}".format(res))
    logging.info("    DEM file                          : {}".format(dem))
    if aoi is not None:
        logging.info("    Area of Interest                  : {}".format(aoi)) 
    if shape is not None:
        logging.info("    Shape File                        : {}".format(shape)) 
    logging.info("    Match flag                        : {}".format(matchFlag))
    logging.info("    If no match, use Dead Reckoning   : {}".format(deadFlag))
    logging.info("    Gamma0 output                     : {}".format(gammaFlag))
    logging.info("    Low resolution flag               : {}".format(loFlag))
    logging.info("    Create power images               : {}".format(pwrFlag))
    logging.info("    Speckle Filtering                 : {}".format(filterFlag))
    logging.info("    Number of looks to take           : {}".format(looks))
    
def process_pol(inFile,rtcName,auxName,pol,res,look_fact,matchFlag,deadFlag,gammaFlag,
                filterFlag,pwrFlag,browse_res,outName,dem,inputType,data):

    logging.info("Processing the {} polarization".format(pol))

    grd = "{out}.{pol}.grd".format(out=outName,pol=pol)
    mgrd = "{out}.{pol}.mgrd".format(out=outName,pol=pol)
    utm = "{out}.{pol}.utm".format(out=outName,pol=pol)
    dem = "area.dem"
    small_map = "{out}_small_map".format(out=outName)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    if "GRD" in inputType:
        cmd = "par_S1_GRD {inf}/*/*{pol}*.tiff {inf}/*/*{pol}*.xml {inf}/*/*/calibration-*{pol}*.xml \
              {inf}/*/*/noise-*{pol}*.xml {grd}.par {grd}".format(inf=inFile,pol=pol,grd=grd)
        execute(cmd,uselogging=True)
	
        # Update the state vectors
        try:
            for eoffile in glob.glob("*.EOF"):
                logging.debug("Applying precision orbit information")
                cmd = "S1_OPOD_vec {grd}.par {eof}".format(grd=grd,eof=eoffile)
                execute(cmd,uselogging=True)
        except:
            logging.warning("Unable to get precision state vectors... continuing...")

        # Multi-look the image
        if look_fact > 1.0:
            cmd = "multi_look_MLI {grd} {grd}.par {mgrd} {mgrd}.par {lks} {lks}".format(grd=grd,mgrd=mgrd,lks=look_fact)
            execute(cmd,uselogging=True)
        else:
	    shutil.copy(grd,mgrd)
            shutil.copy("{}.par".format(grd),"{}.par".format(mgrd))

    else:
        #  Ingest SLC data files into gamma format
        par_s1_slc_single(inFile,pol)
        date = inFile[17:25]
	make_tab_flag = True
        burst_tab = getBursts(inFile,make_tab_flag)
        shutil.copy(burst_tab,date)

        # Mosaic the swaths together and copy SLCs over        
        back = os.getcwd()
        os.chdir(date) 
        path = "../"
        rlooks = look_fact*5
        alooks = look_fact 
        SLC_copy_S1_fullSW(path,date,"SLC_TAB",burst_tab,mode=2,raml=rlooks,azml=alooks)
        os.chdir(back)
 
        # Rename files
        name = "{}.mli".format(date)
        shutil.move(name,mgrd)
        name = "{}.mli.par".format(date)
        shutil.move(name,"{}.par".format(mgrd))

    if filterFlag:
        width = getParmeter("{}.par".format(mgrd),"range_samples")
	el_looks = look_fact * look_fact * 5
	cmd = "enh_lee {mgrd} temp.mgrd {wid} {el} 1 7 7".format(mgrd=mgrd,wid=width,el=el_looks)
	execute(cmd,uselogging=True)
	shutil.move("temp.mgrd",mgrd)

    options = "-p -j -n 6 -q -c "
    if gammaFlag:
        options = options + "-g "
    
    logging.info("Running RTC process... initializing")
    dir = "geo_{}".format(pol)
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {dir}/area.dem {dir}/area.dem_par {dir} image {res} 0 {opt}".format(mgrd=mgrd,dem=dem,dir=dir,res=res,opt=options)
    execute(cmd,uselogging=True)
    
    if matchFlag:
        fail = False
        logging.info("Running RTC process... coarse matching")
	cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {dir}/area.dem {dir}/area.dem_par {dir} image {res} 1 {opt}".format(mgrd=mgrd,dem=dem,dir=dir,res=res,opt=options)
        try:
	    execute(cmd,uselogging=True)
	except:
	    logging.warning("WARNING: Determination of the initial offset failed, skipping initial offset")
	
        logging.info("Running RTC process... fine matching")
	cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {dir}/area.dem {dir}/area.dem_par {dir} image {res} 2 {opt}".format(mgrd=mgrd,dem=dem,dir=dir,res=res,opt=options)
        try:
	    execute(cmd,uselogging=True)
	except:
	    if not deadFlag:
	        logging.error("ERROR: Failed to match images")
		exit(1)
            else:
	        logging.warning("WARNING: Coregistration has failed; defaulting to dead reckoning")
		os.remove("{}/{}".format(dir,"image.diff_par"))
		fail = True
	
	if not fail:
	    try:
	        check_coreg(outName,res,max_offset=50,max_error=2)
            except:
		if not deadFlag:
	            logging.error("ERROR: Failed to coregistration check")
		    exit(1)
                else:
	            logging.warning("WARNING: Coregistration check has failed; defaulting to dead reckoning")
		    os.remove("{}/{}".format(dir,"image.diff_par"))

    logging.info("Running RTC process... finalizing")
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {dir}/area.dem {dir}/area.dem_par {dir} image {res} 3 {opt}".format(mgrd=mgrd,dem=dem,dir=dir,res=res,opt=options)    		
    execute(cmd,uselogging=True)

    back = os.getcwd()
    os.chdir(dir)

    # Make Geotiff Files
    cmd = "data2geotiff area.dem_par image_0.ls_map 5 {}.ls_map.tif".format(outName)
    execute(cmd,uselogging=True)
    cmd = "data2geotiff area.dem_par image_0.inc_map 2 {}.inc_map.tif".format(outName)
    execute(cmd,uselogging=True)
    cmd = "data2geotiff area.dem_par area.dem 2 outdem.tif"
    execute(cmd,uselogging=True)
    gdal.Translate("{}.dem.tif".format(outName),"outdem.tif",outputType=gdal.GDT_Int16)

    if gammaFlag:
        gdal.Translate("tmp.tif",tif,metadataOptions = ['Band1={}_gamma0'.format(pol)])
    else:
        gdal.Translate("tmp.tif",tif,metadataOptions = ['Band1={}_sigma0'.format(pol)])
    shutil.move("tmp.tif",tif)
    createAmp(tif,nodata=0)
  
    # Make meta files and stats 
    cmd = "asf_import -format geotiff {}.ls_map.tif ls_map".format(outName)
    execute(cmd,uselogging=True)
    cmd = "stats -overstat -overmeta ls_map"
    execute(cmd,uselogging=True)
    cmd = "asf_import -format geotiff {}.inc_map.tif inc_map".format(outName) 
    execute(cmd,uselogging=True)
    cmd = "stats -overstat -overmeta -mask 0 inc_map"
    execute(cmd,uselogging=True)
    cmd = "asf_import -format geotiff image_cal_map.mli_amp.tif tc_{}".format(pol)
    execute(cmd,uselogging=True)
    cmd = "stats -nostat -overmeta -mask 0 tc_{}".format(pol)
    execute(cmd,uselogging=True)
     
    # Make browse resolution tif file 
    if (res > browse_res):
        browse_res = res
        shutil.copy("image_cal_map.mli_amp.tif","{}_{}_{}m.tif".format(outName,pol,browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(outName,pol,browse_res),"image_cal_map.mli_amp.tif",xRes=browse_res,yRes=browse_res)

    # Move files into the product directory 
    outDir = "../PRODUCT"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    tifName = rtcName
    if pwrFlag:
        shutil.move(tif,"{}/{}".format(outDir,tifName))
    else:
        copy_metadata(tif,"image_cal_map.mli_amp.tif")
	shutil.move("image_cal_map.mli_amp.tif","{}/{}".format(outDir,tifName))
	
    shutil.move("{}.ls_map.tif".format(outName),"{}/{}-ls_map.tif".format(outDir,auxName))
    shutil.move("{}.inc_map.tif".format(outName),"{}/{}-inc_map.tif".format(outDir,auxName))
    shutil.move("{}.dem.tif".format(outName),"{}/{}-dem.tif".format(outDir,auxName))
    
    os.chdir("..")
    
		  
def process_2nd_pol(inFile,rtcName,cpol,res,look_fact,gammaFlag,filterFlag,pwrFlag,browse_res,
	                    outfile,dem,inputType,date):

    if cpol == "vh":
        mpol = "vv"
    else:
        mpol = "hh"

    grd = "{out}.{pol}.grd".format(out=outfile,pol=cpol)
    mgrd = "{out}.{pol}.mgrd".format(out=outfile,pol=cpol)
    utm = "{out}.{pol}.utm".format(out=outfile,pol=cpol)
    dem = "area.dem"
    small_map = "{out}_small_map".format(out=outfile)
    tif = "image_cal_map.mli.tif"

    # Ingest the granule into gamma format
    if "GRD" in inputType:
        cmd = "par_S1_GRD {inf}/*/*{pol}*.tiff {inf}/*/*{pol}*.xml {inf}/*/*/calibration-*{pol}*.xml \
              {inf}/*/*/noise-*{pol}*.xml {grd}.par {grd}".format(inf=inFile,pol=cpol,grd=grd)
        execute(cmd,uselogging=True)
	
        # Update the state vectors
        try:
            for eoffile in glob.glob("*.EOF"):
                logging.debug("Applying precision orbit information")
                cmd = "S1_OPOD_vec {grd}.par {eof}".format(grd=grd,eof=eoffile)
                execute(cmd,uselogging=True)
        except:
            logging.warning("Unable to get precision state vectors... continuing...")

        # Multi-look the image
        if look_fact > 1.0:
            cmd = "multi_look_MLI {grd} {grd}.par {mgrd} {mgrd}.par {lks} {lks}".format(grd=grd,mgrd=mgrd,lks=look_fact)
            execute(cmd,uselogging=True)
        else:
	    shutil.copy(grd,mgrd)
            shutil.copy("{}.par".format(grd),"{}.par".format(mgrd))

    else:
        #  Ingest SLC data files into gamma format
        par_s1_slc_single(inFile,cpol)
        date = inFile[17:25]
	make_tab_flag = False
        burst_tab = getBursts(inFile,make_tab_flag)
        shutil.copy(burst_tab,date)

        # Mosaic the swaths together and copy SLCs over        
        back = os.getcwd()
        os.chdir(date) 
        path = "../"
        rlooks = look_fact*5
        alooks = look_fact 
        SLC_copy_S1_fullSW(path,date,"SLC_TAB",burst_tab,mode=2,raml=rlooks,azml=alooks)
        os.chdir(back)
 
        # Rename files
        name = "{}.mli".format(date)
        shutil.move(name,mgrd)
        name = "{}.mli.par".format(date)
        shutil.move(name,"{}.par".format(mgrd))
 
    if filterFlag:
        width = getParmeter("{}.par".format(mgrd),"range_samples")
	el_looks = look_fact * look_fact * 5
	cmd = "enh_lee {mgrd} temp.mgrd {wid} {el} 1 7 7".format(mgrd=mgrd,wid=width,el=el_looks)
	execute(cmd,uselogging=True)
	shutil.move("temp.mgrd",mgrd)

    options = "-p -j -n 6 -q -c "
    if gammaFlag:
        options = options + "-g "
    
    dir = "geo_{}".format(cpol)
    mdir = "geo_{}".format(mpol)
    if not os.path.isdir(dir):
        os.mkdir(dir)

    shutil.copy("geo_{}/image.diff_par".format(mpol),"{}".format(dir))
    os.symlink("../geo_{}/image_0.map_to_rdc".format(mpol),"{}/image_0.map_to_rdc".format(dir))
    os.symlink("../geo_{}/image_0.ls_map".format(mpol),"{}/image_0.ls_map".format(dir))
    os.symlink("../geo_{}/image_0.inc_map".format(mpol),"{}/image_0.inc_map".format(dir))
    os.symlink("../geo_{}/image_0.sim".format(mpol),"{}/image_0.sim".format(dir))
    os.symlink("../geo_{}/image_0.pix_map".format(mpol),"{}/image_0.pix_map".format(dir))
    
    cmd = "mk_geo_radcal {mgrd} {mgrd}.par {dem} {dem}.par {mdir}/area.dem {mdir}/area.dem_par {dir} image {res} 3 {opt}".format(mgrd=mgrd,dem=dem,mdir=mdir,dir=dir,res=res,opt=options)
    execute(cmd,uselogging=True)
    os.chdir(dir)
    
    # Make geotif file
    if gammaFlag:
        gdal.Translate("tmp.tif",tif,metadataOptions = ['Band1={}_gamma0'.format(cpol)])
    else:
        gdal.Translate("tmp.tif",tif,metadataOptions = ['Band1={}_sigma0'.format(cpol)])
    shutil.move("tmp.tif",tif)
    
    # Make browse resolution file
    createAmp(tif,nodata=0)
    if (res > browse_res):
        browse_res = res
        shutil.copy("image_cal_map.mli_amp.tif","{}_{}_{}m.tif".format(outfile,cpol,browse_res))
    else:
        gdal.Translate("{}_{}_{}m.tif".format(outfile,cpol,browse_res),"image_cal_map.mli_amp.tif",xRes=browse_res,yRes=browse_res)

    # Create meta files and stats
    cmd = "asf_import -format geotiff image_cal_map.mli_amp.tif tc_{}".format(cpol)
    execute(cmd,uselogging=True)
    cmd = "stats -nostat -overmeta -mask 0 tc_{}".format(cpol)
    execute(cmd,uselogging=True)

    # Move files to product directory
    outDir = "../PRODUCT"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    if pwrFlag:
        shutil.move(tif,"{}/{}".format(outDir,rtcName))
    else:
        copy_metadata(tif,"image_cal_map.mli_amp.tif")
	shutil.move("image_cal_map.mli_amp.tif","{}/{}".format(outDir,rtcName))
        
    os.chdir("..")
    
def create_browse_images(outName,rtcName,res,pol,cpol,browse_res):

    ampfile = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=pol,name=outName,res=browse_res)
    if cpol:
	ampfile2 = "geo_{pol}/{name}_{pol}_{res}m.tif".format(pol=cpol,name=outName,res=browse_res)
	threshold = -24
	outfile = "{}_rgb.tif".format(outName)
        rtc2color(ampfile,ampfile2, threshold, outfile, amp=True, cleanup=True)
        colorname = "PRODUCT/{}_rgb".format(rtcName)
        makeAsfBrowse(outfile,colorname)
     
    os.chdir("geo_{}".format(pol))
    outdir = "../PRODUCT"
    outfile = "{}/{}".format(outdir,rtcName)
    ampfile = "{name}_{pol}_{res}m.tif".format(pol=pol,name=outName,res=browse_res)
    sigmafile = ampfile.replace(".tif","_sigma.tif")
    byteSigmaScale(ampfile,sigmafile)
    makeAsfBrowse(sigmafile,outfile)
  
    os.chdir("../PRODUCT")

    infile = "{}-ls_map.tif".format(rtcName)
    outfile = "{}-ls_map".format(rtcName)
    makeAsfBrowse(infile,outfile) 

    infile = "{}-inc_map.tif".format(rtcName)
    outfile = "{}-inc_map".format(rtcName)
    makeAsfBrowse(infile,outfile) 

    infile = "{}-dem.tif".format(rtcName)
    outfile = "{}-dem".format(rtcName)
    makeAsfBrowse(infile,outfile) 

    os.chdir("..")


def create_arc_xml(infile,outfile,inputType,gammaFlag,pwrFlag,filterFlag,looks,pol,cpol,demType):
    # Create XML metadata files
    etc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "etc"))
    back = os.getcwd()
    os.chdir("PRODUCT")
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    year = now.year
    basename = os.path.basename(infile)
    granulename = os.path.splitext(basename)[0]
    flooks = looks*looks*5
    if gammaFlag:
        power_type = "gamma"
    else:
        power_type = "sigma"
    if pwrFlag:
        format_type = "power"
    else:
        format_type = "amplitude"
    if filterFlag:
        filterStr = "has"
    else:
        filterStr = "has not"

    for myfile in glob.glob("*.tif"):
        f = None
        this_pol = None
        resa = None
        resm = None
        if pol in myfile or cpol in myfile:
            f = open("{}/RTC_GAMMA_Template.xml".format(etc_dir),"r")
            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(outfile))
            if pol in myfile:
                this_pol = pol
            else:
                this_pol = cpol
        elif "ls_map" in myfile:
            f = open("{}/RTC_GAMMA_Template_ls.xml".format(etc_dir),"r")
            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
        elif "inc_map" in myfile:
            encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
        elif "dem" in myfile:
            if "NED" in demType:
                f = open("{}/RTC_GAMMA_Template_dem_NED.xml".format(etc_dir),"r")
                if "13" in demType:
                    resa = 0.333333333333
                    resm = 10
                elif "1" in demType:
                    resa = 1.0
                    resm = 30
                else:
                    resa = 2.0
                    resm = 60
            else:
                f = open("{}/RTC_GAMMA_Template_dem_SRTM.xml".format(etc_dir),"r")
                if "1" in demType:
                    resa = 1.0
                    resm = 30
                else:
                    resa = 3.0
                    resm = 90

            g = open("{}.xml".format(myfile),"w")
            encoded_jpg = pngtothumb("{}.png".format(os.path.splitext(myfile)[0]))
        if f is not None: 
            for line in f:
                line = line.replace("[DATE]",date)
                line = line.replace("[TIME]","{}00".format(time))
                line = line.replace("[DATETIME]",dt)
                line = line.replace("[YEARPROCESSED]","{}".format(year))
                line = line.replace("[YEARACQUIRED]",infile[17:21])
                line = line.replace("[TYPE]",inputType)
                line = line.replace("[THUMBNAIL_BINARY_STRING]",encoded_jpg)
                if this_pol is not None:
                    line = line.replace("[POL]",this_pol)
                line = line.replace("[POWERTYPE]",power_type)
                line = line.replace("[GRAN_NAME]",granulename)
                line = line.replace("[FORMAT]",format_type)
                line = line.replace("[LOOKS]","{}".format(looks))
                line = line.replace("[FILT]","{}".format(filterStr))
                line = line.replace("[FLOOKS]","{}".format(flooks))
                line = line.replace("[DEM]","{}".format(demType))
                if resa is not None:
                    line = line.replace("[RESA]","{}".format(resa))
                if resm is not None:
                    line = line.replace("[RESM]","{}".format(resm))
                g.write("{}\n".format(line))
            f.close()
            g.close()

    for myfile in glob.glob("*.png"):

        if "rgb" in myfile:
            f = open("{}/RTC_GAMMA_Template_color_png.xml".format(etc_dir),"r")
            encoded_jpg = pngtothumb("{}_rgb.png".format(outfile))
        else:
            f = open("{}/RTC_GAMMA_Template_grayscale_png.xml".format(etc_dir),"r")
            encoded_jpg = pngtothumb("{}.png".format(outfile))

        if "large" in myfile:
            res = "medium"
        else:
            res = "low"

        g = open("{}.xml".format(myfile),"w")
        for line in f:
            line = line.replace("[DATE]",date)
            line = line.replace("[TIME]","{}00".format(time))
            line = line.replace("[DATETIME]",dt)
            line = line.replace("[YEARPROCESSED]","{}".format(year))
            line = line.replace("[YEARACQUIRED]",infile[17:21])
            line = line.replace("[TYPE]",inputType)
            line = line.replace("[THUMBNAIL_BINARY_STRING]",encoded_jpg)
            line = line.replace("[GRAN_NAME]",granulename)
            line = line.replace("[RES]",res)
            line = line.replace("[FORMAT]",format_type)
            g.write("{}\n".format(line))
        f.close()
        g.close()

    os.chdir(back)


def create_consolidated_log(basename,outName,loFlag,deadFlag,matchFlag,gammaFlag,aoi,
                            shape,pwrFlag,filterFlag,pol,looks,logFile):

    out = "PRODUCT"
    logname = "{}/{}.log".format(out,basename)
    logging.info("Creating log file: {}".format(logname))
 
    f = open(logname,"w")
    f.write("Consolidated log for: {}\n".format(outName))
    options = ""
    if loFlag:
        options = options + "-l "
    if deadFlag:
        options = options + "-d "
    if matchFlag:
        options = options + "-n "
    if gammaFlag:
        options = options + "-g "
    if filterFlag:
        options = options + "-f "
    if pwrFlag:
        options = options + "-p "
    options = options + "-k {}".format(looks)
    if aoi:
        options = options + "-a {}".format(aoi)
    if shape:
        options = options + "-s {}".format(shape)

    cmd = "rtc_sentinel.py " + options
    f.write("Command: {}\n".format(cmd))
    f.close()    

    dir = "geo_{}".format(pol)
    add_log(logFile,logname)
    add_log("{}/mk_geo_radcal_0.log".format(dir),logname)
    add_log("{}/mk_geo_radcal_1.log".format(dir),logname)
    add_log("{}/mk_geo_radcal_2.log".format(dir),logname)
    add_log("{}/mk_geo_radcal_3.log".format(dir),logname)
    add_log("coreg_check.log",logname)


def add_log(log,full_log):
    g = open(full_log,"a")
    g.write("==============================================\n")
    g.write("Log: {}\n".format(log))
    g.write("==============================================\n")

    if not os.path.isfile(log):
        g.write("(not found)\n")
        g.close()
        return()

    f = open(log,"r")
    for line in f:
        g.write("{}".format(line))
    f.close()

    g.write("\n")
    g.close()
   
    
def create_iso_xml(outfile,outname,pol,cpol,inFile,output,demType,log):

    hdf5_name = "hdf5_list.txt"
    path = inFile
    etc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "etc"))
    shutil.copy("{}/sentinel_xml.xsl".format(etc_dir),"sentinel_xml.xsl")
    
    out = "PRODUCT"

    cmd = "xsltproc --stringparam path {path} --stringparam timestamp timestring --stringparam file_size 1000 --stringparam server stuff --output out.xml sentinel_xml.xsl {path}/manifest.safe".format(path=path)
    execute(cmd,uselogging=True)

    m = sentinel2meta("out.xml")
    write_asf_meta(m, "out.meta")

    ver_file = "{}/version.txt".format(etc_dir)
    gap_ver = None
    if os.path.exists(ver_file):
        f = open(ver_file,"r")
        for line in f:
            gap_ver = line
    else:
        logging.warning("No version.txt file found in {}".format(etc_dir))

    ver_file = "{}/ASF_Gamma_version.txt".format(os.environ['GAMMA_HOME'])
    gamma_ver = None
    if os.path.exists(ver_file):
        f = open(ver_file,"r")
        for line in f:
            gap_ver = line
    else:
        logging.warning("No ASF_Gamma_version.txt file found in {}".format(os.environ['GAMMA_HOME']))

    g = open(hdf5_name,"w")
    g.write("[GAMMA RTC]\n")
    g.write("granule = {}\n".format(outname))
    g.write("metadata = out.meta\n")
    
    geo_dir = "geo_{}".format(pol)
    dem_seg = "{}/area.dem".format(geo_dir)
    dem_seg_par = "{}/area.dem_par".format(geo_dir)

    g.write("oversampled dem file = {}\n".format(dem_seg))
    g.write("oversampled dem metadata = {}\n".format(dem_seg_par))
    g.write("original dem file = {}/{}-dem.tif\n".format(out,outname))
    g.write("layover shadow mask = {}/{}-ls_map.tif\n".format(out,outname))
    g.write("layover shadow stats = {}/ls_map.stat\n".format(geo_dir))
    g.write("incidence angle file = {}/{}-inc_map.tif\n".format(out,outname))
    g.write("incidence angle metadata = {}/inc_map.meta\n".format(geo_dir))

    g.write("input {} file = {}\n".format(pol,outfile))
    g.write("terrain corrected {pol} metadata = {dir}/tc_{pol}.meta\n".format(pol=pol,dir=geo_dir))
    g.write("terrain corrected {} file = {}/{}\n".format(pol,out,outfile))

    if cpol:
        outfile2 = outfile.replace(pol,cpol)
        g.write("input {} file = {}\n".format(pol,outfile))
        geo_dir2 = geo_dir.replace(pol,cpol)
        g.write("terrain corrected {pol} metadata = {dir}/tc_{pol}.meta\n".format(pol=cpol,dir=geo_dir2))
        g.write("terrain corrected {} file = {}/{}\n".format(cpol,out,outfile2))

    g.write("initial processing log = {}\n".format(log))
    g.write("terrain correction log = {}\n".format(log))
    g.write("main log = {}\n".format(log))
    g.write("mk_geo_radcal_0 log = {}/mk_geo_radcal_0.log\n".format(geo_dir))
    g.write("mk_geo_radcal_1 log = {}/mk_geo_radcal_1.log\n".format(geo_dir))
    g.write("mk_geo_radcal_2 log = {}/mk_geo_radcal_2.log\n".format(geo_dir))
    g.write("mk_geo_radcal_3 log = {}/mk_geo_radcal_3.log\n".format(geo_dir))
    g.write("coreg_check log = coreg_check.log\n")
    g.write("mli.par file = {}.{}.mgrd.par\n".format(output,pol))
    g.write("gamma version = {}\n".format(gamma_ver))
    g.write("gap_rtc version = {}\n".format(gap_ver))
    g.write("dem source = {}\n".format(demType))
    g.write("browse image = {}/{}.png\n".format(out,outname))
    g.write("kml overlay = {}/{}.kmz\n".format(out,outname))

    g.close()
    
    cmd = "write_hdf5_xml {} {}.xml".format(hdf5_name,outname)
    execute(cmd,uselogging=True)

    logging.info("Generating {}.iso.xml with {}/rtc_iso.xsl\n".format(outname,etc_dir))

    cmd = "xsltproc {etc}/rtc_iso.xsl {out}.xml > {out}.iso.xml".format(etc=etc_dir,out=outname)
    execute(cmd,uselogging=True)

    shutil.copy("{}.iso.xml".format(outname),"{}".format(out))


def clean_prod_dir():
    os.chdir("PRODUCT")
    for myfile in glob.glob("*ls_map*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*ls_map*kmz"):
        os.remove(myfile)
    for myfile in glob.glob("*inc_map*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*inc_map*kmz"):
        os.remove(myfile)
    for myfile in glob.glob("*dem*png*"):
        os.remove(myfile)
    for myfile in glob.glob("*dem*kmz"):
        os.remove(myfile)
    os.chdir("..")


def rtc_sentinel_gamma(inFile,outName,res=None,dem=None,aoi=None,shape=None,matchFlag=True,
                       deadFlag=None,gammaFlag=None,loFlag=None,pwrFlag=None,
                       filterFlag=None,looks=None):

    logging.info("===================================================================")
    logging.info("                Sentinel RTC Program - Starting")
    logging.info("===================================================================")

    browse_res = 30
    if res is None:
        res = 10
    if loFlag:
        res = 30
	
    if looks is None:
        looks = int(res/10+0.5)
        logging.info("Setting looks to {}".format(looks))

    report_kwargs(inFile,outName,res,dem,aoi,shape,matchFlag,deadFlag,gammaFlag,loFlag,
                  pwrFlag,filterFlag,looks)

    if not os.path.exists(inFile):
        logging.error("ERROR: Input file {} does not exist".format(inFile))
        exit(1)
    if "zip" in inFile:
        zip_ref = zipfile.ZipFile(myfile, 'r')
        zip_ref.extractall(".")
        zip_ref.close()    
        inFile = inFile.replace(".zip",".SAFE")

    mode = inFile[4:6].lower()
    plat = inFile[2:3].lower()
    inputType = inFile[7:11]
    date = inFile[17:25]
    
    if 'SLC' in inputType:
        inputType = 'SLC'

    if (res > 10):
        outType = "rtcm"
    else:
        outType = "rtch"

    auxName= "s1{}-{}-{}-{}".format(plat,mode,outType,outName)

    try:
        cmd = "get_orb.py {}".format(inFile)
        logging.info("Getting precision orbit information")
        execute(cmd,uselogging=True)
    except:
        logging.warning("Unable to fetch precision state vectors... continuing")
    
    if dem is None:
        logging.info("Getting DEM file covering this SAR image")
	demfile,demType = getDemFile(inFile,"tmpdem.tif",utmFlag=True,post=30)
	dem = "area.dem"
	parfile = "area.dem.par"
	utm2dem("tmpdem.tif",dem,parfile)
    elif ".tif" in dem:
        tiff_dem = dem
	parfile = "area.dem.par"
        utm2dem(tiff_dem,dem,parfile)          
        demType = "Unknown"
    elif os.path.isfile("{}.par".format(dem)):
        parfile = "{}.par".format(dem)
        demType = "Unknown"
    else:
        logging.error("ERROR: Unrecognized DEM: {}".format(dem))
	exit(1)

    vvlist = glob.glob("{}/*/*vv*.tiff".format(inFile))
    vhlist = glob.glob("{}/*/*vh*.tiff".format(inFile))
    hhlist = glob.glob("{}/*/*hh*.tiff".format(inFile))
    hvlist = glob.glob("{}/*/*hv*.tiff".format(inFile))
    
    cpol = None

    if vvlist:
        logging.info("Found VV polarization - processing")
        pol = "vv"
        rtcName= "s1{}-{}-{}-{}-{}.tif".format(plat,mode,outType,pol,outName)
        process_pol(inFile,rtcName,auxName,pol,res,looks,matchFlag,deadFlag,gammaFlag,filterFlag,pwrFlag,
            browse_res,outName,dem,inputType,date)
        if vhlist:
            cpol = "vh"
            rtcName= "s1{}-{}-{}-{}-{}.tif".format(plat,mode,outType,cpol,outName)
            logging.info("Found VH polarization - processing")
            process_2nd_pol(inFile,rtcName,cpol,res,looks,gammaFlag,filterFlag,pwrFlag,browse_res,
                            outName,dem,inputType,date)

    if hhlist:
        logging.info("Found HH polarization - processing")
        pol = "hh"
        rtcName= "s1{}-{}-{}-{}-{}.tif".format(plat,mode,outType,pol,outName)
        process_pol(inFile,rtcName,auxName,pol,res,looks,matchFlag,deadFlag,gammaFlag,filterFlag,pwrFlag,
            browse_res,outName,dem,inputType,date)
        if vhlist:
            cpol = "hv"
            logging.info("Found HV polarization - processing")
            rtcName= "s1{}-{}-{}-{}-{}.tif".format(plat,mode,outType,cpol,outName)
            process_2nd_pol(inFile,rtcName,cpol,res,looks,gammaFlag,filterFlag,pwrFlag,browse_res,
                            outName,dem,inputType,date)

    if hhlist is None and vvlist is None:
        logging.error("ERROR: Can not find VV or HH polarization in {}".inFile)
        exit(1)

    create_browse_images(outName,auxName,res,pol,cpol,browse_res)
    logFile = glob.glob("*_log.txt")[0]
    rtcName= "s1{}-{}-{}-{}-{}.tif".format(plat,mode,outType,pol,outName)
    create_iso_xml(rtcName,auxName,pol,cpol,inFile,outName,demType,logFile)
    create_arc_xml(inFile,auxName,inputType,gammaFlag,pwrFlag,filterFlag,looks,pol,cpol,demType)
    clean_prod_dir()
    perform_sanity_checks()
    logging.info("===================================================================")
    logging.info("               Sentinel RTC Program - Completed")
    logging.info("===================================================================")

    create_consolidated_log(auxName,outName,loFlag,deadFlag,matchFlag,gammaFlag,aoi,
                            shape,pwrFlag,filterFlag,pol,looks,logFile)


if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='rtc_sentinel',
      description='Creates an RTC image from a Sentinel 1 Scene using GAMMA software')
  parser.add_argument('input',help='Name of input file, either .zip or .SAFE')
  parser.add_argument('output', help='base name of the output files')
  parser.add_argument("-o","--outputResolution",type=float,help="Desired output resolution")
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-e","--externalDEM",help="Specify a DEM file to use")
  group.add_argument("-a","--aoi",help="Specify AOI to use",type=float,nargs=4,
      metavar=('LON_MIN','LAT_MIN','LON_MAX','LAT_MAX'))
  group.add_argument("-s","--shape",help="Specify shape file to use")
  parser.add_argument("-n",action="store_false",help="Do not perform matching")
  parser.add_argument("-d",action="store_true",help="if matching fails, use dead reckoning")
  parser.add_argument("-g",action="store_true",help="create gamma0 instead of sigma0")
  parser.add_argument("-l",action="store_true",help="create a lo-res output (30m)")
  parser.add_argument("-p",action="store_true",help="create power images instead of amplitude")
  parser.add_argument("-f",action="store_true",help="run enhanced lee filter")
  parser.add_argument("-k","--looks",type=int,help="set the number of looks to take")
  args = parser.parse_args()

  logFile = "{}_{}_log.txt".format(args.output,os.getpid())
  logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
  logging.getLogger().addHandler(logging.StreamHandler())
  logging.info("Starting run")

  rtc_sentinel_gamma(args.input,args.output,res=args.outputResolution,dem=args.externalDEM,
                     aoi=args.aoi,shape=args.shape,matchFlag=args.n,deadFlag=args.d,
                     gammaFlag=args.g,loFlag=args.l,pwrFlag=args.p,filterFlag=args.f,
                     looks=args.looks)
			
