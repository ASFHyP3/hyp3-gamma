"""Create and apply a water body mask"""
import json
import subprocess
from pathlib import Path
import warnings
from tempfile import TemporaryDirectory

import geopandas as gpd
from osgeo import gdal
from pyproj import CRS
from shapely import geometry

from hyp3_gamma.util import GDALConfigManager

gdal.UseExceptions()


def split_geometry_on_antimeridian(geometry: dict):
    geometry_as_bytes = json.dumps(geometry).encode()
    cmd = ['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '/vsistdout/', '/vsistdin/']
    geojson_str = subprocess.run(cmd, input=geometry_as_bytes, stdout=subprocess.PIPE, check=True).stdout
    return json.loads(geojson_str)['features'][0]['geometry']


def get_envelope(input_image: str):
    """Get the envelope around a GeoTIFF.
    Args:
        input_image: The path to the desired GeoTIFF, as a string.
    Returns:
        envelope_wgs84_gdf: The WGS84 envelope around the GeoTIFF, as a GeoDataFrame.
    """
    info = gdal.Info(input_image, format='json')
    prj = CRS.from_wkt(info["coordinateSystem"]["wkt"])
    epsg = prj.to_epsg()
    extent = info['wgs84Extent']
    poly = geometry.shape(extent).buffer(0.15)
    poly_gdf = gpd.GeoDataFrame(index=[0], geometry=[poly], crs='EPSG:4326')
    # envelope of the extent in epsg coordinates
    poly_gdf_epsg = poly_gdf.to_crs(epsg)
    envelope_gdf_epsg = poly_gdf_epsg.envelope

    # envelope of extent in wgs84 coordinates
    envelope_gdf = envelope_gdf_epsg.to_crs(4326)

    envelope_poly = envelope_gdf.geometry[0]
    envelope = geometry.mapping(envelope_poly)

    correct_extent = split_geometry_on_antimeridian(envelope)
    correct_envelope = geometry.shape(correct_extent)
    envelope_gdf_wgs84 = gpd.GeoDataFrame(index=[0], geometry=[correct_envelope], crs='EPSG:4326')

    return envelope_gdf_epsg, envelope_gdf_wgs84, epsg


def create_water_mask(input_image: str, output_image: str, gdal_format='GTiff'):
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from GSHHG v2.3.7 Levels 1, 2, 3, and 5 at full resolution. To learn more, visit
    https://www.soest.hawaii.edu/pwessel/gshhg/

    Shoreline data is unbuffered and pixel values of 1 indicate land touches the pixel and 0 indicates there is no
    land in the pixel.

    Args:
        input_image: Path for the input GDAL-compatible image
        output_image: Path for the output image
        gdal_format: GDAL format name to create output image as
    """
    src_ds = gdal.Open(input_image)

    driver_options = []
    if gdal_format == 'GTiff':
        driver_options = ['COMPRESS=LZW', 'TILED=YES', 'NUM_THREADS=ALL_CPUS']

    dst_ds = gdal.GetDriverByName(gdal_format).Create(
        output_image,
        src_ds.RasterXSize,
        src_ds.RasterYSize,
        1,
        gdal.GDT_Byte,
        driver_options,
    )
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjection())
    dst_ds.SetMetadataItem('AREA_OR_POINT', src_ds.GetMetadataItem('AREA_OR_POINT'))

    envelope_gdf_epsg, envelope_gdf_wgs84, epsg = get_envelope(input_image)

    mask_location = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/GSHHG/hyp3_water_mask_20220912.shp'

    mask = gpd.read_file(mask_location, mask=envelope_gdf_wgs84)

    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        try:
            mask = gpd.clip(mask.to_crs(epsg), envelope_gdf_epsg).to_crs(epsg)
        except (Warning, Exception) as e:
            print('error found', e)
            mask = gpd.clip(mask, envelope_gdf_wgs84)

    with TemporaryDirectory() as temp_dir:
        temp_file = str(Path(temp_dir) / 'mask.shp')
        mask.to_file(temp_file, driver='ESRI Shapefile')
        with GDALConfigManager(OGR_ENABLE_PARTIAL_REPROJECTION='YES'):
            gdal.Rasterize(dst_ds, temp_file, allTouched=True, burnValues=[1])

    del src_ds, dst_ds
