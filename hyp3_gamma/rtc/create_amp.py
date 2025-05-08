"""Convert Geotiff Power to Amplitude"""


import numpy as np
from osgeo import gdal

from hyp3_gamma.rtc import gdal_file


def create_amp(fi, nodata=None):
    handle = gdal.Open(fi)
    (x, y, trans, proj, data) = gdal_file.read(handle)
    ampdata = np.sqrt(data)
    outfile = fi.replace('.tif', '_amp.tif')
    gdal_file.write_fload(outfile, trans, proj, ampdata, nodata=nodata)
    return outfile
