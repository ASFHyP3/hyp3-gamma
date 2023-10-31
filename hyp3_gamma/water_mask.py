"""Create and apply a water body mask"""
import json
import subprocess
from tempfile import TemporaryDirectory

import geopandas
from shapely.geometry import Polygon
from osgeo import gdal

from hyp3_gamma.util import GDALConfigManager

gdal.UseExceptions()


def split_geometry_on_antimeridian(geometry: dict):
    geometry_as_bytes = json.dumps(geometry).encode()
    cmd = ['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '/vsistdout/', '/vsistdin/']
    geojson_str = subprocess.run(cmd, input=geometry_as_bytes, stdout=subprocess.PIPE, check=True).stdout
    return json.loads(geojson_str)['features'][0]['geometry']


def create_water_mask(input_tif: str, output_tif: str):
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from GSHHG v2.3.7 Levels 1, 2, 3, and 5 at full resolution. To learn more, visit
    https://www.soest.hawaii.edu/pwessel/gshhg/

    Shoreline data is unbuffered and pixel values of 1 indicate land touches the pixel and 0 indicates there is no
    land in the pixel.

    Args:
        input_tif: Path for the input GeoTIFF
        output_tif: Path for the output GeoTIFF
    """
    mask_location = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/GSHHG/hyp3_water_mask_20220912.shp'

    src_ds = gdal.Open(input_tif)
    dst_ds = gdal.GetDriverByName('GTiff').Create(output_tif, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjection())
    dst_ds.SetMetadataItem('AREA_OR_POINT', src_ds.GetMetadataItem('AREA_OR_POINT'))

    # need assign values for the band, otherwise, the gdal.Rasterize does not work correctly.
    data = dst_ds.ReadAsArray()
    data[:, :] = 0
    dst_ds.GetRasterBand(1).WriteArray(data)

    extent = gdal.Info(input_tif, format='json')['wgs84Extent']
    extent = split_geometry_on_antimeridian(extent)

    poly = Polygon(extent['coordinates'][0])
    mask = (geopandas.read_file(mask_location)).clip(poly)  # very slow, but it produces correct water_mask.tif

    # mask = geopandas.read_file(mask_location, mask=extent),
    # This mask has a wrong extent, can not be used to produce water_mask.tif

    with TemporaryDirectory() as temp_shapefile:
        mask.to_file(temp_shapefile, driver='ESRI Shapefile')
        with GDALConfigManager(OGR_ENABLE_PARTIAL_REPROJECTION='YES'):
            gdal.Rasterize(dst_ds, temp_shapefile, allTouched=True, burnValues=[1])

    del src_ds, dst_ds
