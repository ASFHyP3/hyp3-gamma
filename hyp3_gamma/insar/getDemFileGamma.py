#/usr/bin/python

from getDemFor import getDemFile
from getSubSwath import get_bounding_box_file
import logging
from apply_wb_mask import apply_wb_mask
import shutil
import saa_func_lib as saa
from osgeo import gdal
from ps2dem import ps2dem
from utm2dem import utm2dem
import os

def getDemFileGamma(filename,use_opentopo,alooks,mask):

    # first get a DEM to check the type
    demfile,demtype = getDemFile(filename,"tmpdem.tif",opentopoFlag=use_opentopo,utmFlag=True)
    if not os.path.isfile(demfile):
        logging.error("Got no return demfile ({}) from getDemfile".format(demfile))
        exit(1)

    ps = False        
    if "REMA" in demtype or "GIMP" in demtype:
        ps = True

    if mask and not ps:
        # Make a DEM for use with wb_mask
        ymax,ymin,xmax,xmin = get_bounding_box_file(filename)
        if (xmax >= 177 and xmin <= -177):
            logging.info("Using anti-meridian special UTM file")
        
            # Need to pass wb mask routine a UTM DEM file
            tmpdem = "temp_mask_dem_{}.tif".format(os.getpid())

            # Apply the water body mask
            logging.info("Applying water body mask")
            apply_wb_mask(demfile,tmpdem,maskval=-32767,gcs=False)
            logging.info("Done with water body mask")
            shutil.move(tmpdem,demfile)
        else:
            # Need to pass wb mask routine a lat,lon DEM file
            demfile,demtype = getDemFile(filename,"tmpdem.tif",opentopoFlag=use_opentopo,utmFlag=False)
            tmpdem = "temp_mask_dem_{}.tif".format(os.getpid())

            # Apply the water body mask
            apply_wb_mask(demfile,tmpdem,maskval=-32767,gcs=True)
     
            # Reproject DEM file into UTM coordinates
            pixsize = 30.0
            if demtype == "SRTMGL3":
                pixsize = 90.
            if demtype == "NED2":
                pixsize = 60.

            saa.reproject_gcs_to_utm(tmpdem,demfile,pixsize)
    elif mask and ps:
        logging.info("WARNING: water masking not supported or polar stereo projections - skipping")


    # If we downsized the SAR image, downsize the DEM file
    # if alks == 1, then the SAR image is roughly 20 m square -> use native dem res
    # if alks == 2, then the SAR image is roughly 40 m square -> set dem to 80 meters
    # if alks == 3, then the SAR image is roughly 60 m square -> set dem to 120 meters 
    # etc.
    #
    # The DEM is set to double the res because it will be 1/2'd by the procedure
    # I.E. if you give a 100 meter DEM as input, the output Igram is 50 meters

    pix_size = 20 * int(alooks) * 2;
    logging.info("Changing resolution")
    gdal.Warp("tmpdem2.tif",demfile,xRes=pix_size,yRes=pix_size,resampleAlg="cubic",dstNodata=-32767,creationOptions=['COMPRESS=LZW'])
    os.remove(demfile)

    if not ps:
      if use_opentopo == True:
        utm2dem("tmpdem2.tif","big.dem","big.par",dataType="int16")
      else:
        utm2dem("tmpdem2.tif","big.dem","big.par")
    else:
        ps2dem("tmpdem2.tif","big.dem","big.par")
      
    return("big",demtype)
