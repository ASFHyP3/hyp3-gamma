import json

import pytest
from hyp3lib import DemError
from osgeo import gdal, ogr

from hyp3_gamma import dem


gdal.UseExceptions()


def test_crosses_antimeridian():
    geometry = {
        'type': 'Point',
        'coordinates': [177.0, 50.0],
    }
    with pytest.raises(ValueError, match='only Polygon is supported'):
        dem.crosses_antimeridian(geometry)

    geometry = {
        'type': 'Polygon',
        'coordinates': [
            [
                [-154.0, 71.0],
                [-147.0, 71.0],
                [-146.0, 70.0],
                [-153.0, 69.0],
                [-154.0, 71.0],
            ]
        ],
    }
    assert not dem.crosses_antimeridian(geometry)

    geometry = {
        'type': 'Polygon',
        'coordinates': [
            [
                [179.5, 51.4],
                [179.5, 51.6],
                [-179.5, 51.6],
                [-179.5, 51.4],
                [179.5, 51.4],
            ],
        ],
    }
    assert dem.crosses_antimeridian(geometry)


def test_get_geometry_from_kml(test_data_dir):
    kml = test_data_dir / 'alaska.kml'
    expected = {
        'type': 'Polygon',
        'coordinates': [
            [
                [-154.0, 71.0],
                [-147.0, 71.0],
                [-146.0, 70.0],
                [-153.0, 69.0],
                [-154.0, 71.0],
            ]
        ],
    }
    geometry = dem.get_geometry_from_kml(kml)
    assert json.loads(geometry.ExportToJson()) == expected

    kml = test_data_dir / 'antimeridian.kml'
    expected = {
        'type': 'Polygon',
        'coordinates': [
            [
                [181.0, 50.0],
                [176.0, 51.0],
                [177.0, 52.0],
                [181.0, 52.0],
                [181.0, 50.0],
            ],
        ],
    }
    geometry = dem.get_geometry_from_kml(kml)
    assert json.loads(geometry.ExportToJson()) == expected


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
    assert info['geoTransform'] == [159720.0, 60.0, 0.0, 1218060.0, 0.0, -60.0]
    assert info['size'] == [928, 1839]


def test_prepare_dem_geotiff_antimeridian(tmp_path):
    dem_geotiff = tmp_path / 'dem.tif'
    geojson = {
        'type': 'Polygon',
        'coordinates': [
            [
                [179.5, 51.4],
                [179.5, 51.6],
                [180.5, 51.6],
                [180.5, 51.4],
                [179.5, 51.4],
            ],
        ],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))

    dem.prepare_dem_geotiff(str(dem_geotiff), geometry)
    assert dem_geotiff.exists()

    info = gdal.Info(str(dem_geotiff), format='json')
    assert info['geoTransform'] == [218760.0, 30.0, 0.0, 5774070.0, 0.0, -30.0]
    assert info['size'] == [3084, 1730]
