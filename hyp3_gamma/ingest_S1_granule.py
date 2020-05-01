from __future__ import print_function, absolute_import, division, unicode_literals

from hyp3lib.execute import execute
import logging
import shutil
from hyp3lib.par_s1_slc_single import par_s1_slc_single
from hyp3lib.SLC_copy_S1_fullSW import SLC_copy_S1_fullSW
from hyp3lib.getBursts import getBursts
from hyp3lib.get_orb import downloadSentinelOrbitFile
import os


def ingest_S1_granule(inFile,pol,look_fact,outFile):

    pol = pol.lower()
    inputType = inFile[7:11]
    grd = "{}.grd".format(pol)
    
    # Ingest the granule into gamma format
    if "GRD" in inputType:
        cmd = "par_S1_GRD {inf}/*/*{pol}*.tiff {inf}/*/*{pol}*.xml {inf}/*/*/calibration-*{pol}*.xml " \
              "{inf}/*/*/noise-*{pol}*.xml {grd}.par {grd}".format(inf=inFile,pol=pol,grd=grd)
        execute(cmd,uselogging=True)

        # Fetch precision state vectors

        try:
            logging.info("Trying to get orbit file information from file {}".format(inFile))
            orbfile,tmp = downloadSentinelOrbitFile(inFile)
            logging.debug("Applying precision orbit information")
            cmd = "S1_OPOD_vec {grd}.par {eof}".format(grd=grd,eof=orbfile)
            execute(cmd,uselogging=True)
        except:
            logging.warning("Unable to fetch precision state vectors... continuing")
        
        # Multi-look the image
        if look_fact > 1.0:
            cmd = "multi_look_MLI {grd} {grd}.par {outFile} {outFile}.par {lks} {lks}".format(grd=grd,outFile=outFile,lks=look_fact)
            execute(cmd,uselogging=True)
        else:
            shutil.copy(grd,outFile)
            shutil.copy("{}.par".format(grd),"{}.par".format(outFile))

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
        shutil.move(name,outFile)
        name = "{}.mli.par".format(date)
        shutil.move(name,"{}.par".format(outFile))
