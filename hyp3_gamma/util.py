import logging
import os
from pathlib import Path
from zipfile import ZipFile

from hyp3lib.fetch import download_file
from hyp3lib.scene import get_download_url
from osgeo import gdal


log = logging.getLogger(__name__)
gdal.UseExceptions()


class GDALConfigManager:
    """Context manager for setting GDAL config options temporarily"""

    def __init__(self, **options):
        """Args:
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


def unzip_granule(zip_file: str, remove: bool = False) -> str:
    log.info(f'Unzipping {zip_file}')
    with ZipFile(zip_file) as z:
        z.extractall()
    if remove:
        os.remove(zip_file)
    return Path(zip_file).with_suffix('.SAFE').name


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
