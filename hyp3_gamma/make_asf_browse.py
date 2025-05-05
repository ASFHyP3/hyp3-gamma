"""Resamples a GeoTIFF file to make a KML and a PNG browse image for ASF"""

import logging

from hyp3lib.resample_geotiff import resample_geotiff
from osgeo import gdal


def make_asf_browse(geotiff: str, base_name: str, use_nn=False, width: int = 2048):
    """
    Make a KML and PNG browse image for ASF
    Args:
        geotiff: name of GeoTIFF file
        base_name: base name of output files
        use_nn: Use GDAL's GRIORA_NearestNeighbour interpolation instead of GRIORA_Cubic
            to resample the GeoTIFF
        width: browse image width

    Returns:
        browse_width: the width of the created browse image
    """
    tiff = gdal.Open(geotiff)
    tiff_width = tiff.RasterXSize
    tiff = None  # How to close with gdal

    if tiff_width < width:
        logging.warning(f'Requested image dimension of {width} exceeds GeoTIFF width {tiff_width}. Using GeoTIFF width')
        browse_width = tiff_width
    else:
        browse_width = width

    resample_geotiff(geotiff, browse_width, 'KML', f'{base_name}.kmz', use_nn)
    resample_geotiff(geotiff, browse_width, 'PNG', f'{base_name}.png', use_nn)

    return browse_width
