from tempfile import NamedTemporaryFile
from typing import List, Tuple

from hyp3lib import DemError
from hyp3lib.execute import execute
from lxml import etree
from osgeo import gdal, ogr

DEM_GEOJSON = '/vsicurl/https://asf-dem-west.s3.us-west-2.amazonaws.com/v2/cop30.geojson'

gdal.UseExceptions()
ogr.UseExceptions()


def get_polygon_from_manifest(manifest_file: str) -> ogr.Geometry:
    root = etree.parse(manifest_file)
    coordinates_string = root.find('//gml:coordinates', namespaces={'gml': 'http://www.opengis.net/gml'}).text
    points = [point.split(',') for point in coordinates_string.split(' ')]
    points.append(points[0])
    wkt = ','.join([f'{p[1]} {p[0]}' for p in points])
    wkt = f'POLYGON(({wkt}))'
    return ogr.CreateGeometryFromWkt(wkt)


def intersects_dem(polygon: ogr.Geometry) -> bool:
    intersects = False
    ds = ogr.Open(DEM_GEOJSON)
    layer = ds.GetLayer()
    for feature in layer:
        if feature.GetGeometryRef().Intersects(polygon):
            intersects = True
            break
    ds = None
    return intersects


def get_dem_file_paths(polygon: ogr.Geometry) -> List[str]:
    file_paths = []
    ds = ogr.Open(DEM_GEOJSON)
    layer = ds.GetLayer()
    for feature in layer:
        if feature.GetGeometryRef().Intersects(polygon):
            file_paths.append(feature.GetField('file_path'))
    ds = None
    return file_paths


def utm_from_lon_lat(lon: float, lat: float) -> int:
    hemisphere = 32600 if lat >= 0 else 32700
    zone = int(lon // 6 + 30) % 60 + 1
    return hemisphere + zone


def prepare_dem(dem_file: str, dem_par_file: str, manifest_file: str, pixel_size: float = 30.0) -> Tuple[str, str]:
    polygon = get_polygon_from_manifest(manifest_file)
    if not intersects_dem(polygon):
        raise DemError('DEM does not cover this area')

    centroid = polygon.Centroid()
    epsg_code = utm_from_lon_lat(centroid.GetX(), centroid.GetY())

    dem_file_paths = get_dem_file_paths(polygon.Buffer(0.15))
    with NamedTemporaryFile() as vrt, NamedTemporaryFile() as dem_tif:
        gdal.BuildVRT(vrt.name, dem_file_paths)
        gdal.Warp(dem_tif.name, vrt.name, dstSRS=f'EPSG:{epsg_code}', xRes=pixel_size, yRes=pixel_size,
                  targetAlignedPixels=True, resampleAlg='cubic', multithread=True)
        execute(f'dem_import {dem_tif.name} {dem_file} {dem_par_file} - - $DIFF_HOME/scripts/egm2008-5.dem '
                f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1', uselogging=True)

    return dem_file, dem_par_file
