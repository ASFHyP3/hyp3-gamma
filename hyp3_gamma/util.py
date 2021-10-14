import logging
import os
from zipfile import ZipFile

from hyp3lib.fetch import download_file
from hyp3lib.scene import get_download_url
from osgeo import gdal
import numpy as np
from osgeo.gdal_array import GDALTypeCodeToNumericTypeCode


log = logging.getLogger(__name__)
gdal.UseExceptions()


class GDALConfigManager:
    """Context manager for setting GDAL config options temporarily"""
    def __init__(self, **options):
        """
        Args:
            **options: GDAL Config `option=value` keyword arguments.
        """
        self.options = options.copy()
        self._previous_options = {}

    def __enter__(self):
        for key in self.options:
            self._previous_options[key] = gdal.GetConfigOption(key)

        for key, value in self.options.items():
            gdal.SetConfigOption(key, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self._previous_options.items():
            gdal.SetConfigOption(key, value)


def get_granule(granule):
    download_url = get_download_url(granule)
    zip_file = download_file(download_url, chunk_size=10485760)
    safe_dir = unzip_granule(zip_file, remove=True)
    return safe_dir


def unzip_granule(zip_file, remove=False):
    log.info(f'Unzipping {zip_file}')
    with ZipFile(zip_file) as z:
        z.extractall()
        safe_dir = next(item.filename for item in z.infolist() if item.is_dir() and item.filename.endswith('.SAFE/'))
    if remove:
        os.remove(zip_file)
    return safe_dir.strip('/')


def earlier_granule_first(g1, g2):
    if g1[17:32] <= g2[17:32]:
        return g1, g2
    return g2, g1


def set_pixel_as_point(tif_file, shift_origin=False):
    ds = gdal.Open(tif_file, gdal.GA_Update)
    ds.SetMetadataItem('AREA_OR_POINT', 'Point')
    if shift_origin:
        transform = list(ds.GetGeoTransform())
        transform[0] += transform[1] / 2
        transform[3] += transform[5] / 2
        ds.SetGeoTransform(transform)
    del ds


def get_minimum_value_for_gdal_datatype(file):
    """get the minimum value of the data type in the geotiff file
    Args:
        file: geotiff file name
    return:
        min_val: minimum value of the data type in the geotiff file
    """
    ds = gdal.Open(file)
    dtype = GDALTypeCodeToNumericTypeCode(ds.GetRasterBand(1).DataType)
    try:
        return np.finfo(dtype).min
    except ValueError:
        return np.iinfo(dtype).min


def get_minimum_value_for_gamma_dtype(dtype):
    """Get the minimum numeric value for a GAMMA data type

    GAMMA provides these data types:
    * 0: RASTER 8 or 24 bit uncompressed raster image, SUN (`*.ras`), BMP:(`*.bmp`), or TIFF: (`*.tif`)
    * 1: SHORT integer (2 bytes/value)
    * 2: FLOAT (4 bytes/value)
    * 3: SCOMPLEX (short complex, 4 bytes/value)
    * 4: FCOMPLEX (float complex, 8 bytes/value)
    * 5: BYTE
    """
    dtype_map = {
        0: np.int8,
        1: np.int16,
        2: np.float32,
        3: np.float32,
        4: np.float64,
        5: np.int8,
    }
    try:
        return np.iinfo(dtype_map[dtype]).min
    except ValueError:
        return np.finfo(dtype_map[dtype]).min
    except KeyError:
        raise ValueError(f'Unknown GAMMA data type: {dtype}')


def set_nodata(file, nodata):
    """
    The output geotiff files produced by gamma package always has 0.0 as nodata value.
    This function changes the nodata value in the geotiff file.

    """
    ds = gdal.Open(file, gdal.GA_Update)
    def_nodata = ds.GetRasterBand(1).GetNoDataValue()
    if def_nodata == 0.0:
        for i in range(1, ds.RasterCount + 1):
            band = ds.GetRasterBand(i)
            band_data = band.ReadAsArray()
            mask = band.GetMaskBand()
            mask_data = mask.ReadAsArray()
            band_data[mask_data == 0] = nodata
            band.WriteArray(band_data)
            band.SetNoDataValue(float(nodata))

    del ds
