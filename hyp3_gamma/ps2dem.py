#!/usr/bin/python

import argparse
import hyp3lib.saa_func_lib as saa
import numpy as np
import os, sys
import logging
from osgeo import gdal, osr
from hyp3lib.execute import execute

def ps2dem(inDem,outDem,demPar):
    demParIn = "dem_par.in"
    basename = os.path.basename(inDem)

    logging.info("PS DEM in GEOTIFF format: {}".format(inDem))
    logging.info("output DEM: {}".format(outDem))
    logging.info("output DEM parameter file: {}".format(demPar))

    xsize,ysize,trans,proj,data = saa.read_gdal_file(saa.open_gdal_file(inDem))

    east = trans[0]
    north = trans[3]
    pix_east = trans[1]
    pix_north = trans[5]

    # Open DEM file
    src_ds=gdal.Open(inDem)

    # Get projection parameters
    prj=src_ds.GetProjection()

    srs=osr.SpatialReference(wkt=prj)
    lat_of_origin = srs.GetProjParm("latitude_of_origin")
    central_meridian = srs.GetProjParm("central_meridian")
   
    s = prj.split("[")
    for t in s:
        if "false_northing" in t:
             u = t.split('"')
             v = u[2].split(",")
             w = v[1].split("]")
             false_north = w[0]

    logging.info("latitude of origin {}".format(lat_of_origin))
    logging.info("central_meridian   {}".format(central_meridian))
    logging.info("found false_north {}".format(false_north))

    string = src_ds.GetMetadata()
    pixasarea = string["AREA_OR_POINT"]
    if "AREA" in pixasarea:
        logging.info("Pixel as Area! Updating corner coordinates to pixel as point")
        logging.info("pixel upper northing (m): {}    easting (m): {}".format(north,east))
        east = east + pix_east / 2.0
        north = north + pix_north / 2.0
        logging.info("Update pixel upper northing (m): {}    easting (m): {}".format(north,east))

    pix_size = pix_east

    # Create the input file for create_dem_par    
    f = open(demParIn,"w")
    f.write("PS\n")
    f.write("WGS84\n")
    f.write("1\n")
    f.write("{}\n".format(lat_of_origin))
    f.write("{}\n".format(central_meridian))
    f.write("{}\n".format(basename))
    f.write("REAL*4\n")
    f.write("0\n")
    f.write("1\n")
    f.write("{}\n".format(np.abs(xsize)))
    f.write("{}\n".format(np.abs(ysize)))
    f.write("{} {}\n".format(pix_north,pix_east))
    f.write("{} {}\n".format(north,east))
    f.close()

    # Create a new dem par file
    if os.path.isfile(demPar): 
        os.remove(demPar)
    execute("create_dem_par {} < {}".format(demPar,demParIn))
    os.remove(demParIn)

    # Since 0 is the invalid pixel sentinel for gamma software,
    # Replace 0 with 1, because zero in a DEM is assumed valid 
    # Then, replace anything <= -32767 with 0
    # (but first remove NANs)
    srcband = src_ds.GetRasterBand(1) 
    noData = srcband.GetNoDataValue() 

    data[np.isnan(data)]=0.0001
    data[data==0] = 1
    data[data<=noData] = 0
    
    # Convert to ENVI (binary) format
    tmptif = "temporary_dem_file.tif"
    if data.dtype == np.float32:
        fdata = data.byteswap()
#    elif data.type == np.int16:
    else:
        # Convert to floating point
        fdata = data.astype(np.float32)
        fdata = fdata.byteswap()
    saa.write_gdal_file_float(tmptif,trans,proj,fdata)
    gdal.Translate(outDem,tmptif,format="ENVI")
    os.remove(tmptif)
    os.remove(outDem + ".aux.xml")
    filename, file_extension = os.path.splitext(outDem)
    os.remove(outDem.replace(file_extension,".hdr"))

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='ps2dem.py',
    description='Convert a polar stereo geotiff DEM into GAMMA internal format')
  parser.add_argument('ps_dem', help='name of GeoTIFF file (input)')
  parser.add_argument('dem', help='DEM data (output)')
  parser.add_argument('dempar', help='Gamma DEM parameter file (output)')

  logFile = "{}_{}_log.txt".format("ps2dem",os.getpid())
  logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
  logging.getLogger().addHandler(logging.StreamHandler())
  logging.info("Starting run")

  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()

  if not os.path.exists(args.ps_dem):
    logging.info('ERROR: GeoTIFF file (%s) does not exist!' % args.ps_dem)
    sys.exit(1)

  ps2dem(args.ps_dem,args.dem,args.dempar)
