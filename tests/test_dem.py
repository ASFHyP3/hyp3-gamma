import json

import pytest
from hyp3lib import DemError
from osgeo import gdal, ogr

from hyp3_gamma import dem

gdal.UseExceptions()


def test_get_geometry_from_kml(test_data_dir):
    kml = test_data_dir / 'alaska.kml'
    expected = {
        'type': 'Polygon',
        'coordinates': [[
            [-154.0, 71.0],
            [- 147.0, 71.0],
            [-146.0, 70.0],
            [-153.0, 69.0],
            [-154.0, 71.0],
        ]],
    }
    geometry = dem.get_geometry_from_kml(kml)
    assert json.loads(geometry.ExportToJson()) == expected

    kml = test_data_dir / 'antimeridian.kml'
    expected = {
        'type': 'MultiPolygon',
        'coordinates': [
            [[
                [176.0, 51.0],
                [177.0, 52.0],
                [180.0, 52.0],
                [180.0, 50.2],
                [176.0, 51.0],
            ]],
            [[
                [-180.0, 50.2],
                [-180.0, 52.0],
                [-179.0, 52.0],
                [-179.0, 50.0],
                [-180.0, 50.2],
            ]],
        ],
    }
    geometry = dem.get_geometry_from_kml(kml)
    assert json.loads(geometry.ExportToJson()) == expected


def test_intersects_dem():
    geojson = {
        'type': 'Point',
        'coordinates': [169, -45],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.intersects_dem(geometry)

    geojson = {
        'type': 'Point',
        'coordinates': [0, 0],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert not dem.intersects_dem(geometry)


def test_get_file_paths():
    geojson = {
        'type': 'Point',
        'coordinates': [0, 0],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == []

    geojson = {
        'type': 'Point',
        'coordinates': [169, -45],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == [
        '/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
        'Copernicus_DSM_COG_10_S46_00_E169_00_DEM/Copernicus_DSM_COG_10_S46_00_E169_00_DEM.tif'
    ]

    geojson = {
        'type': 'MultiPoint',
        'coordinates': [[0, 0], [169, -45], [-121.5, 73.5]]
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == [
        '/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
        'Copernicus_DSM_COG_10_S46_00_E169_00_DEM/Copernicus_DSM_COG_10_S46_00_E169_00_DEM.tif',
        '/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
        'Copernicus_DSM_COG_10_N73_00_W122_00_DEM/Copernicus_DSM_COG_10_N73_00_W122_00_DEM.tif',
    ]


def test_utm_from_lon_lat():
    assert dem.utm_from_lon_lat(0, 0) == 32631
    assert dem.utm_from_lon_lat(-179, -1) == 32701
    assert dem.utm_from_lon_lat(179, 1) == 32660
    assert dem.utm_from_lon_lat(27, 89) == 32635
    assert dem.utm_from_lon_lat(182, 1) == 32601
    assert dem.utm_from_lon_lat(-182, 1) == 32660
    assert dem.utm_from_lon_lat(-360, -1) == 32731


def test_get_centroid_crossing_antimeridian():
    geojson = {
        'type': 'MultiPolygon',
        'coordinates': [
            [[
                [177.0, 50.0],
                [177.0, 51.0],
                [180.0, 51.0],
                [180.0, 50.0],
                [177.0, 50.0],
            ]],
            [[
                [-180.0, 50.0],
                [-180.0, 51.0],
                [-179.0, 51.0],
                [-179.0, 50.0],
                [-180.0, 50.0],
            ]],
        ],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert geometry.Centroid().GetX() == 89.0
    assert geometry.Centroid().GetY() == 50.5

    centroid = dem.get_centroid_crossing_antimeridian(geometry)
    assert centroid.GetX() == 179.0
    assert centroid.GetY() == 50.5


def test_get_dem_features():
    assert len(list(dem.get_dem_features())) == 26445


def test_shift_for_antimeridian(tmp_path):
    file_paths = [
        '/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
        'Copernicus_DSM_COG_10_N51_00_W180_00_DEM/Copernicus_DSM_COG_10_N51_00_W180_00_DEM.tif',
        '/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/'
        'Copernicus_DSM_COG_10_N51_00_E179_00_DEM/Copernicus_DSM_COG_10_N51_00_E179_00_DEM.tif'
    ]

    with dem.GDALConfigManager(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        shifted_file_paths = dem.shift_for_antimeridian(file_paths, tmp_path)

    assert shifted_file_paths[0] == str(tmp_path / 'Copernicus_DSM_COG_10_N51_00_W180_00_DEM.vrt')
    assert shifted_file_paths[1] == file_paths[1]

    info = gdal.Info(shifted_file_paths[0], format='json')
    assert info['cornerCoordinates']['upperLeft'] == [179.9997917, 52.0001389]
    assert info['cornerCoordinates']['lowerRight'] == [180.9997917, 51.0001389]


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
        'coordinates': [[
            [0.4, 10.16],
            [0.4, 10.86],
            [0.6, 10.86],
            [0.6, 10.16],
            [0.4, 10.16],
        ]],
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
            [[
                [179.5, 51.4],
                [179.5, 51.6],
                [180.0, 51.6],
                [180.0, 51.4],
                [179.5, 51.4],
            ]],
            [[
                [-180.0, 51.4],
                [-180.0, 51.6],
                [-179.5, 51.6],
                [-179.5, 51.4],
                [-180.0, 51.4],
            ]],
        ],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))

    dem.prepare_dem_geotiff(str(dem_geotiff), geometry)
    assert dem_geotiff.exists()

    info = gdal.Info(str(dem_geotiff), format='json')
    assert info['geoTransform'] == [219330.0, 30.0, 0.0, 5768640.0, 0.0, -30.0]
    assert info['size'] == [4780, 3897]
