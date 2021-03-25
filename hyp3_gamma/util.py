import logging
import os
from zipfile import ZipFile

from hyp3lib.fetch import download_file
from hyp3lib.scene import get_download_url
from osgeo import gdal

log = logging.getLogger(__name__)
gdal.UseExceptions()


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


def set_pixel_as_point(tif_file):
    ds = gdal.Open(tif_file, gdal.GA_Update)
    ds.SetMetadataItem('AREA_OR_POINT', 'Point')
    del ds
