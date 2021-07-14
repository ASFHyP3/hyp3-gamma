import json
from pathlib import Path
from subprocess import PIPE, run
from tempfile import TemporaryDirectory
from typing import Generator, List

from hyp3lib import DemError
from osgeo import gdal, ogr

from hyp3_gamma.util import GDALConfigManager

DEM_GEOJSON = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/v2/cop30.geojson'

gdal.UseExceptions()
ogr.UseExceptions()


def get_geometry_from_kml(kml_file: str) -> ogr.Geometry:
    cmd = ['ogr2ogr', '-wrapdateline', '-datelineoffset', '20', '-f', 'GeoJSON', '-mapfieldtype', 'DateTime=String',
           '/vsistdout', kml_file]
    geojson_str = run(cmd, stdout=PIPE, check=True).stdout
    geometry = json.loads(geojson_str)['features'][0]['geometry']
    return ogr.CreateGeometryFromJson(json.dumps(geometry))


def get_dem_features() -> Generator[ogr.Feature, None, None]:
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


def prepare_dem_geotiff(output_name: str, geometry: ogr.Geometry, pixel_size: float = 30.0):
    """Create a DEM mosaic GeoTIFF covering a given geometry

    The DEM mosaic is assembled from the Copernicus GLO-30 Public DEM.  The output GeoTIFF covers the input geometry
    buffered by 0.15 degrees, is projected to the UTM zone of the geometry centroid, and has a pixel size of 30m.

    Args:
        output_name: Path for the output GeoTIFF
        geometry: Geometry in EPSG:4326 (lon/lat) projection for which to prepare a DEM mosaic
        pixel_size: Pixel size for the output GeoTIFF in meters

    """
    with GDALConfigManager(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        if not intersects_dem(geometry):
            raise DemError(f'Copernicus GLO-30 Public DEM does not intersect this geometry: {geometry}')

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            centroid = geometry.Centroid()
            dem_file_paths = get_dem_file_paths(geometry.Buffer(0.15))

            if geometry.GetGeometryName() == 'MULTIPOLYGON':
                centroid = get_centroid_crossing_antimeridian(geometry)
                dem_file_paths = shift_for_antimeridian(dem_file_paths, temp_path)

            dem_vrt = temp_path / 'dem.vrt'
            gdal.BuildVRT(str(dem_vrt), dem_file_paths)

            epsg_code = utm_from_lon_lat(centroid.GetX(), centroid.GetY())

            gdal.Warp(str(output_name), str(dem_vrt), dstSRS=f'EPSG:{epsg_code}', xRes=pixel_size, yRes=pixel_size,
                      targetAlignedPixels=True, resampleAlg='cubic', multithread=True)