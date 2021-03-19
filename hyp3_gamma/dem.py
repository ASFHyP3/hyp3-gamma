import json
from os import path
from subprocess import PIPE, run
from tempfile import TemporaryDirectory
from typing import List, Tuple

from hyp3lib import DemError
from hyp3lib.execute import execute
from osgeo import gdal, ogr

DEM_GEOJSON = '/vsicurl/https://asf-dem-west.s3.us-west-2.amazonaws.com/v2/cop30.geojson'

gdal.UseExceptions()
ogr.UseExceptions()


def get_geometry_from_kml(kml_file: str) -> ogr.Geometry:
    # TODO suppress warnings about Date parsing?
    response = run(['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '/vsistdout', kml_file],
                   stdout=PIPE, check=True)
    geojson = json.loads(response.stdout)
    geometry = json.dumps(geojson['features'][0]['geometry'])
    return ogr.CreateGeometryFromJson(geometry)


def intersects_dem(geometry: ogr.Geometry) -> bool:
    intersects = False
    ds = ogr.Open(DEM_GEOJSON)
    layer = ds.GetLayer()
    for feature in layer:
        if feature.GetGeometryRef().Intersects(geometry):
            intersects = True
            break
    del ds
    return intersects


def get_dem_file_paths(geometry: ogr.Geometry) -> List[str]:
    file_paths = []
    ds = ogr.Open(DEM_GEOJSON)
    layer = ds.GetLayer()
    for feature in layer:
        if feature.GetGeometryRef().Intersects(geometry):
            file_paths.append(feature.GetField('file_path'))
    del ds
    return file_paths


def crosses_antimeridian(geometry: ogr.Geometry) -> bool:
    return geometry.GetGeometryCount() > 1


def utm_from_lon_lat(lon: float, lat: float) -> int:
    hemisphere = 32600 if lat >= 0 else 32700
    zone = int(lon // 6 + 30) % 60 + 1
    return hemisphere + zone


def utm_from_geometry(geometry: ogr.Geometry) -> int:
    centroid = geometry.Centroid()
    if crosses_antimeridian(geometry):
        x = 180  # TODO address antimeridian
    else:
        x = centroid.GetX()
    return utm_from_lon_lat(x, centroid.GetY())


def shift_for_antimeridian(dem_file_paths: List[str], directory: str) -> List[str]:
    shifted_file_paths = []
    for file_path in dem_file_paths:
        if '_W' in file_path:
            shifted_file_path = f'{directory}/{path.basename(file_path)}'  # TODO .vrt extension instead of .tif?
            # TODO use geoTransform instead of cornerCoordinates for higher precision?
            corners = gdal.Info(file_path, format='json')['cornerCoordinates']
            output_bounds = [
                corners['upperLeft'][0] + 360,
                corners['upperLeft'][1],
                corners['lowerRight'][0] + 360,
                corners['lowerRight'][1]
            ]
            gdal.Translate(shifted_file_path, file_path, format='VRT', outputBounds=output_bounds)
            shifted_file_paths.append(shifted_file_path)
        else:
            shifted_file_paths.append(file_path)
    return shifted_file_paths


def prepare_dem(dem_file: str, dem_par_file: str, kml_file: str) -> Tuple[str, str]:
    geometry = get_geometry_from_kml(kml_file)
    if not intersects_dem(geometry):
        raise DemError('DEM does not cover this area')

    epsg_code = utm_from_geometry(geometry)

    dem_file_paths = get_dem_file_paths(geometry.Buffer(0.15))
    with TemporaryDirectory() as temp_dir:
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')  # TODO use config context manager

        if crosses_antimeridian(geometry):
            dem_file_paths = shift_for_antimeridian(dem_file_paths, temp_dir)

        dem_vrt = 'dem.vrt'  # TODO use temp_dir for intermediate files
        gdal.BuildVRT(dem_vrt, dem_file_paths)

        dem_tif = 'dem.tif'  # TODO use temp_dir for intermediate files
        pixel_size = 30.0
        gdal.Warp(dem_tif, dem_vrt, dstSRS=f'EPSG:{epsg_code}', xRes=pixel_size, yRes=pixel_size,
                  targetAlignedPixels=True, resampleAlg='cubic', multithread=True)

        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', None)

    execute(f'dem_import {dem_tif} {dem_file} {dem_par_file} - - $DIFF_HOME/scripts/egm2008-5.dem '
            f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1', uselogging=True)

    return dem_file, dem_par_file
