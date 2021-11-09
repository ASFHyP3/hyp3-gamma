import logging
import os
import subprocess
from zipfile import ZipFile

from hyp3lib.fetch import download_file
from hyp3lib.scene import get_download_url
from osgeo import gdal

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


def is_shift(in_mli_par, in_dem_par, infile):
    """
    determine if input geotiff is shifted from the map space
    """
    shift_flag = False
    ds = gdal.Open(infile)
    gt = ds.GetGeoTransform()

    cmd = ['coord_to_sarpix', in_mli_par, '-', in_dem_par, str(gt[3]), str(gt[0]), '0.0']
    result = subprocess.run(cmd, capture_output=True, text=True)
    coord_log_lines = result.stdout.splitlines()
    selected_coords = [ line for line in coord_log_lines if "map_row,map_col,hgt_new:" in line]
    coord_lst = selected_coords[0].split(":")[-1].strip().split(" ")
    coord_lst = [ float(s) for s in coord_lst]
    map_row = coord_lst[0]
    map_col = coord_lst[1]

    if map_row != 0.0 or map_col != 0.0:
        gt_new_0 = gt[0] - gt[1]*map_row
        gt_new_3 = gt[3] - gt[5]*map_col
        gt_new =(gt_new_0, gt[1], gt[2], gt_new_3, gt[4], gt[5])
        shift_flag = True
        return shift_flag, gt_new
    else:
        return shift_flag, gt


def set_pixel_as_point(tif_file, shift_origin=False):
    ds = gdal.Open(tif_file, gdal.GA_Update)
    ds.SetMetadataItem('AREA_OR_POINT', 'Point')
    if shift_origin:
        transform = list(ds.GetGeoTransform())
        transform[0] += transform[1] / 2
        transform[3] += transform[5] / 2
        ds.SetGeoTransform(transform)

    # figured out it needs to set projection again, otherwise, the projection info may loses
    ds.SetProjection(ds.GetProjection())
    del ds
