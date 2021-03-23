import json

from osgeo import gdal, ogr

from hyp3_gamma import dem

gdal.UseExceptions()


def test_gdal_config_manager():
    gdal.SetConfigOption('OPTION1', 'VALUE1')
    gdal.SetConfigOption('OPTION2', 'VALUE2')

    assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
    assert gdal.GetConfigOption('OPTION2') == 'VALUE2'
    assert gdal.GetConfigOption('OPTION3') is None
    assert gdal.GetConfigOption('OPTION4') is None

    with dem.GDALConfigManager(OPTION2='CHANGED', OPTION3='VALUE3'):
        assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
        assert gdal.GetConfigOption('OPTION2') == 'CHANGED'
        assert gdal.GetConfigOption('OPTION3') == 'VALUE3'
        assert gdal.GetConfigOption('OPTION4') is None

        gdal.SetConfigOption('OPTION4', 'VALUE4')

    assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
    assert gdal.GetConfigOption('OPTION2') == 'VALUE2'
    assert gdal.GetConfigOption('OPTION3') is None
    assert gdal.GetConfigOption('OPTION4') == 'VALUE4'


def test_get_geometry_from_kml(test_data_dir):
    kml = test_data_dir / 'alaska.kml'
    geometry = dem.get_geometry_from_kml(kml)
    expected = {
        'type': 'Polygon',
        'coordinates': [[
            [-154.765991, 71.443138],
            [- 147.69957, 71.992523],
            [-146.76358, 70.338882],
            [-153.28656, 69.820648],
            [-154.765991, 71.443138],
        ]],
    }
    assert json.loads(geometry.ExportToJson()) == expected

    kml = test_data_dir / 'antimeridian.kml'
    geometry = dem.get_geometry_from_kml(kml)
    expected = {
        'type': 'MultiPolygon',
        'coordinates': [
            [[
                [176.674484, 51.302433],
                [177.037384, 52.755581],
                [180.0, 52.43662881351332],
                [180.0, 50.93483522676132],
                [176.674484, 51.302433]
            ]],
            [[
                [-180.0, 50.93483522676132],
                [-180.0, 52.43662881351332],
                [-179.303116, 52.361603],
                [-179.781296, 50.91066],
                [-180.0, 50.93483522676132],
            ]]
        ],
    }
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
        'coordinates': [169, -45],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == [
        '/vsicurl/https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/'
        'Copernicus_DSM_COG_10_S46_00_E169_00_DEM/Copernicus_DSM_COG_10_S46_00_E169_00_DEM.tif'
    ]

    geojson = {
        'type': 'Point',
        'coordinates': [0, 0],
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == []

    geojson = {
        'type': 'MultiPoint',
        'coordinates': [[0, 0], [169, -45], [-121.5, 73.5]]
    }
    geometry = ogr.CreateGeometryFromJson(json.dumps(geojson))
    assert dem.get_dem_file_paths(geometry) == [
        '/vsicurl/https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/'
        'Copernicus_DSM_COG_10_S46_00_E169_00_DEM/Copernicus_DSM_COG_10_S46_00_E169_00_DEM.tif',
        '/vsicurl/https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/'
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
