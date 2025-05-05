import logging
import os

from PIL import Image
from hyp3_gamma.make_asf_browse import make_asf_browse
from osgeo import gdal


def test_width_smaller(geotiff):
    geotiff_base = geotiff.replace('.tif', '')
    browse_width = make_asf_browse(geotiff, geotiff_base, width=10)

    assert browse_width == 10
    with Image.open(f'{geotiff_base}.png') as png:
        assert png.size[0] == browse_width

    assert os.path.exists(f'{geotiff_base}.png.aux.xml')
    assert os.path.exists(f'{geotiff_base}.kmz')


def test_width_larger(geotiff, caplog):
    tiff = gdal.Open(geotiff)
    tiff_width = tiff.RasterXSize
    tiff = None  # How to close with gdal

    geotiff_base = geotiff.replace('.tif', '')

    with caplog.at_level(logging.DEBUG):
        browse_width = make_asf_browse(geotiff, geotiff_base, width=2048)

        assert browse_width == tiff_width
        assert 'Using GeoTIFF width' in caplog.text
        with Image.open(f'{geotiff_base}.png') as png:
            assert png.size[0] == tiff_width
