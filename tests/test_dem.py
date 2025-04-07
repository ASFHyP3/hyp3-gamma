import json

import pytest
from hyp3lib import DemError
from osgeo import gdal, ogr

from hyp3_gamma import dem


gdal.UseExceptions()


def test_utm_from_lon_lat():
    assert dem.utm_from_lon_lat(0, 0) == 32631
    assert dem.utm_from_lon_lat(-179, -1) == 32701
    assert dem.utm_from_lon_lat(179, 1) == 32660
    assert dem.utm_from_lon_lat(27, 89) == 32635
    assert dem.utm_from_lon_lat(182, 1) == 32601
    assert dem.utm_from_lon_lat(-182, 1) == 32660
    assert dem.utm_from_lon_lat(-360, -1) == 32731



def test_prepare_dem_geotiff_no_coverage():
    geojson = {
        'type': 'Point',
        'coordinates': [0, 0],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    with pytest.raises(DemError):
        dem.prepare_dem_geotiff('foo', geometry)


def test_prepare_dem_geotiff(tmp_path):
    dem_geotiff = tmp_path / 'dem.tif'
    geojson = {
        'type': 'Polygon',
        'coordinates': [
            [
                [0.4, 10.16],
                [0.4, 10.86],
                [0.6, 10.86],
                [0.6, 10.16],
                [0.4, 10.16],
            ]
        ],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))

    dem.prepare_dem_geotiff(str(dem_geotiff), geometry, pixel_size=60)
    assert dem_geotiff.exists()

    info = gdal.Info(str(dem_geotiff), format='json')
    assert info['geoTransform'] == [171000.0, 60.0, 0.0, 1328400.0, 0.0, -60.0]
    assert info['size'] == [1854, 3706]


def test_prepare_dem_geotiff_antimeridian(tmp_path):
    dem_geotiff = tmp_path / 'dem.tif'
    geojson = {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    [179.5, 51.4],
                    [179.5, 51.6],
                    [180.0, 51.6],
                    [180.0, 51.4],
                    [179.5, 51.4],
                ]
            ],
            [
                [
                    [-180.0, 51.4],
                    [-180.0, 51.6],
                    [-179.5, 51.6],
                    [-179.5, 51.4],
                    [-180.0, 51.4],
                ]
            ],
        ],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))

    dem.prepare_dem_geotiff(str(dem_geotiff), geometry)
    assert dem_geotiff.exists()

    info = gdal.Info(str(dem_geotiff), format='json')
    assert info['geoTransform'] == [219330.0, 30.0, 0.0, 5768640.0, 0.0, -30.0]
    assert info['size'] == [4780, 3897]
