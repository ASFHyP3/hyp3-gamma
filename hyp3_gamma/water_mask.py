"""Create and apply a water body mask"""
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
import pandas as pd
import s3fs
from osgeo import gdal
from shapely import geometry, wkt

from hyp3_gamma.util import GDALConfigManager

gdal.UseExceptions()


def get_geo_partition(coordinate, partition_size=90):
    """Get the geo-partition for a given coordinate (i.e., the lat/lon box it falls in)

    Args:
        coordinate: A coordinate tuple (lon, lat)
        partition_size: The partition size (in degrees) to use for the geo-partition
            using a value of 90 will result in geo-partitions of 90x90 degrees

    Returns:
        A string representing the geo-partition for the given coordinate and partition size
    """
    x, y = coordinate
    x_rounded = 0 if int(np.floor(x / partition_size)) * partition_size == 180 \
        else int(np.floor(x / partition_size)) * partition_size

    y_rounded = int(np.floor(y / partition_size)) * partition_size
    x_fill = str(x_rounded).zfill(4)
    y_fill = str(y_rounded).zfill(4)
    partition = f'{y_fill}_{x_fill}'
    return partition


def split_geometry_on_antimeridian(geometry: dict):
    geometry_as_bytes = json.dumps(geometry).encode()
    cmd = ['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '/vsistdout/', '/vsistdin/']
    geojson_str = subprocess.run(cmd, input=geometry_as_bytes, stdout=subprocess.PIPE, check=True).stdout
    return json.loads(geojson_str)['features'][0]['geometry']


def poly_from_box(bbox: list):
    """ Create a polygon from a bbox

    Args:
        bbox: The extent bounding box, e.g. [min_lon, min_lat, max_lon, max_lat]

    Returns:
        Polygon: The extent Polygon: [(min_lon, min_lat), (min_lon, max_lat), ...]
    """
    min_lon = geometry.Point(bbox[0], bbox[1])
    min_lat = geometry.Point(bbox[2], bbox[1])
    max_lon = geometry.Point(bbox[2], bbox[3])
    max_lat = geometry.Point(bbox[0], bbox[3])
    return geometry.Polygon([min_lon, min_lat, max_lon, max_lat])


def envelope(extent: dict):
    """Returns an evelope surrounding a split extent. 

    Args:
        extent: A dict representing a Polygon or MultiPolygon from split_geometry_on_antimeridian.

    Returns:
        A MultiPolygon representing the envelope surrounding the input Polygon(s).
    """
    min_lat_col = 1
    max_lat_col = 3
    if extent["type"] == 'Polygon':
        polys = geometry.MultiPolygon([geometry.shape(extent)])
        return polys
    else:
        polys = geometry.shape(extent)
        bounds = np.asarray([list(poly.bounds) for poly in polys.geoms])
        lat_min = bounds[:, min_lat_col].min()
        lat_max = bounds[:, max_lat_col].max()
        for i in range(len(bounds)):
            bounds[i][min_lat_col] = lat_min
            bounds[i][max_lat_col] = lat_max

        return geometry.MultiPolygon([poly_from_box(bound) for bound in bounds])


def get_water_mask_gdf(extent: dict) -> gpd.GeoDataFrame:
    """Get a GeoDataFrame of the water mask for a given extent

    Args:
        extent: The extent to get the water mask for

    Returns:
        GeoDataFrame of the water mask for the given extent
    """
    mask_location = 'asf-dem-west/WATER_MASK/GSHHG/hyp3_water_mask_20220912'

    polys = envelope(split_geometry_on_antimeridian(extent))

    filters = []
    for poly in polys.geoms:
        tmp = list(set([('lat_lon', '=', get_geo_partition(coord)) for coord in poly.envelope.exterior.coords]))
        for i in tmp:
            filters.append([i])

    s3_fs = s3fs.S3FileSystem(anon=True, default_block_size=5 * (2**20))

    # TODO the conversion from pd -> gpd can be removed when gpd adds the filter param for read_parquet
    df = pd.read_parquet(mask_location, filesystem=s3_fs, filters=filters)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    df['lat_lon'] = df['lat_lon'].astype(str)
    gdf = gpd.GeoDataFrame(df, crs='EPSG:4326')

    mask = gpd.clip(gdf, polys)
    return mask


def create_water_mask(input_image: str, output_image: str, gdal_format='GTiff'):
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from GSHHG v2.3.7 Levels 1, 2, 3, and 5 at full resolution. To learn more, visit
    https://www.soest.hawaii.edu/pwessel/gshhg/

    Shoreline data is unbuffered and pixel values of 1 indicate land touches the pixel and 0 indicates there is no
    land in the pixel.

    Args:
        input_imge: Path for the input GDAL-compatible image
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

    extent = gdal.Info(input_image, format='json')['wgs84Extent']

    mask = get_water_mask_gdf(extent)

    with TemporaryDirectory() as temp_dir:
        temp_file = str(Path(temp_dir) / 'mask.shp')
        mask.to_file(temp_file, driver='ESRI Shapefile')
        with GDALConfigManager(OGR_ENABLE_PARTIAL_REPROJECTION='YES'):
            gdal.Rasterize(dst_ds, temp_file, allTouched=True, burnValues=[1])

    del src_ds, dst_ds
