import logging
import os

from hyp3lib.getDemFor import getDemFile
from osgeo import gdal

from hyp3_gamma.utm2dem import utm2dem

log = logging.getLogger(__name__)


def get_dem_file_gamma(filename, alooks):
    demfile, demtype = getDemFile(filename, "tmpdem.tif")

    # If we downsized the SAR image, downsize the DEM file
    # if alks == 1, then the SAR image is roughly 20 m square -> use native dem res
    # if alks == 2, then the SAR image is roughly 40 m square -> set dem to 80 meters
    # if alks == 3, then the SAR image is roughly 60 m square -> set dem to 120 meters
    # etc.
    #
    # The DEM is set to double the res because it will be 1/2'd by the procedure
    # I.E. if you give a 100 meter DEM as input, the output Igram is 50 meters
    pix_size = 20 * int(alooks) * 2
    log.info("Changing DEM resolution")
    gdal.Warp("tmpdem2.tif", demfile, xRes=pix_size, yRes=pix_size, resampleAlg="cubic", dstNodata=-32767,
              creationOptions=['COMPRESS=LZW'])
    os.remove(demfile)

    utm2dem("tmpdem2.tif", "big.dem", "big.par")

    return "big", demtype
