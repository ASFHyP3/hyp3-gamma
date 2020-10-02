from __future__ import print_function, absolute_import, division, unicode_literals

import glob
import os
from hyp3lib import saa_func_lib as saa
from osgeo import gdal


# Gamma program data2geotiff shifts the corner coordinates
# by 1/2 a pixel.  This routine shifts them back.  It also
# sets the geotiff metadata to say Point.
def fix_geotiff_locations(dir="PRODUCT"):
    back = os.getcwd()
    os.chdir(dir)
    for myfile in glob.glob("*.tif"):
        x1,y1,t1,p1,data = saa.read_gdal_file(saa.open_gdal_file(myfile))
        easting = t1[0]
        resx = t1[1]
        rotx = t1[2]
        northing = t1[3]
        roty = t1[4]
        resy = t1[5]
        easting = easting + resx/2.0
        northing = northing + resy/2.0
        t1 = [easting, resx, rotx, northing, roty, resy]
        tmpfile = "tmp_tiff_{}.tif".format(os.getpid())
        if "dem" in myfile or "DEM" in myfile:
            saa.write_gdal_file(tmpfile,t1,p1,data)
        elif "ls_map" in myfile or "LS" in myfile:
            saa.write_gdal_file_byte(tmpfile,t1,p1,data)
        else:
            saa.write_gdal_file_float(tmpfile,t1,p1,data,nodata=0)
        gdal.Translate(myfile,tmpfile,metadataOptions=['AREA_OR_POINT=Point'],noData="0")
        os.remove(tmpfile)
    os.chdir(back)

