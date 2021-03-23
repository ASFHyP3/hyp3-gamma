import json
from pathlib import Path
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
    response = run(['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '-mapfieldtype',
                    'DateTime=String', '/vsistdout', kml_file], stdout=PIPE, check=True)
    geojson = json.loads(response.stdout)
    geometry = json.dumps(geojson['features'][0]['geometry'])
    return ogr.CreateGeometryFromJson(geometry)


def get_dem_features():
    ds = ogr.Open(DEM_GEOJSON)
    layer = ds.GetLayer()
    for feature in layer:
        yield feature
    del ds


def intersects_dem(geometry: ogr.Geometry) -> bool:
    for feature in get_dem_features():
        if feature.GetGeometryRef().Intersects(geometry):
            return True


def get_dem_file_paths(geometry: ogr.Geometry) -> List[str]:
    file_paths = []
    for feature in get_dem_features():
        if feature.GetGeometryRef().Intersects(geometry):
            file_paths.append(feature.GetField('file_path'))
    return file_paths


def crosses_antimeridian(geometry: ogr.Geometry) -> bool:
    return geometry.GetGeometryCount() > 1


def utm_from_lon_lat(lon: float, lat: float) -> int:
    hemisphere = 32600 if lat >= 0 else 32700
    zone = int(lon // 6 + 30) % 60 + 1
    return hemisphere + zone


def get_centroid_crossing_antimeridian(geometry: ogr.Geometry) -> ogr.Geometry:
    geojson = json.loads(geometry.ExportToJson())
    for feature in geojson['coordinates']:
        for point in feature[0]:
            if point[0] < 0:
                point[0] += 360
    shifted_geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    return shifted_geometry.Centroid()


def shift_for_antimeridian(dem_file_paths: List[str], directory: Path) -> List[str]:
    shifted_file_paths = []
    for file_path in dem_file_paths:
        if '_W' in file_path:
            shifted_file_path = str(directory / Path(file_path).with_suffix('.vrt').name)
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


def prepare_dem(dem_file: str, dem_par_file: str, kml_file: str) -> Tuple[str, str]:
    with GDALConfigManager(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        geometry = get_geometry_from_kml(kml_file)
        if not intersects_dem(geometry):
            raise DemError('DEM does not cover this area')

        with Path(TemporaryDirectory().name) as temp_dir:
            centroid = geometry.Centroid()
            dem_file_paths = get_dem_file_paths(geometry.Buffer(0.15))

            if geometry.GetGeometryName() == 'MULTIPOLYGON':
                centroid = get_centroid_crossing_antimeridian(geometry)
                dem_file_paths = shift_for_antimeridian(dem_file_paths, temp_dir)

            dem_vrt = temp_dir / 'dem.vrt'
            gdal.BuildVRT(str(dem_vrt), dem_file_paths)

            dem_tif = temp_dir / 'dem.tif'
            pixel_size = 30.0
            epsg_code = utm_from_lon_lat(centroid.GetX(), centroid.GetY())
            gdal.Warp(str(dem_tif), str(dem_vrt), dstSRS=f'EPSG:{epsg_code}', xRes=pixel_size, yRes=pixel_size,
                      targetAlignedPixels=True, resampleAlg='cubic', multithread=True)

            execute(f'dem_import {str(dem_tif)} {dem_file} {dem_par_file} - - $DIFF_HOME/scripts/egm2008-5.dem '
                    f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1', uselogging=True)

    return dem_file, dem_par_file
