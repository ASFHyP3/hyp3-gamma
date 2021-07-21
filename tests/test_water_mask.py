import numpy as np
from osgeo import gdal

from hyp3_gamma import water_mask

gdal.UseExceptions()


def test_split_geometry_on_antimeridian():
    geometry = {
        'type': 'Polygon',
        'coordinates': [[
            [170, 50],
            [175, 55],
            [-170, 55],
            [-175, 50],
            [170, 50],
        ]],
    }
    result = water_mask.split_geometry_on_antimeridian(geometry)
    assert result == {
        'type': 'MultiPolygon',
        'coordinates': [
            [[
                [175.0, 55.0],
                [180.0, 55.0],
                [180.0, 50.0],
                [170.0, 50.0],
                [175.0, 55.0],
            ]],
            [[
                [-170.0, 55.0],
                [-175.0, 50.0],
                [-180.0, 50.0],
                [-180.0, 55.0],
                [-170.0, 55.0],
            ]],
        ],
    }

    geometry = {
        'type': 'Polygon',
        'coordinates': [[
            [150, 50],
            [155, 55],
            [-150, 55],
            [-155, 50],
            [150, 50],
        ]],
    }
    result = water_mask.split_geometry_on_antimeridian(geometry)
    assert result == geometry


def test_create_water_mask_with_no_water(tmp_path, test_data_dir):
    input_tif = str(test_data_dir / 'test_geotiff.tif')
    output_tif = str(tmp_path / 'water_mask.tif')
    water_mask.create_water_mask(input_tif, output_tif)

    info = gdal.Info(output_tif, format='json', stats=True)
    assert info['size'] == [20, 20]
    assert info['geoTransform'] == [440720.0, 60.0, 0.0, 3751320.0, 0.0, -60.0]
    assert info['bands'][0]['type'] == 'Byte'
    assert info['bands'][0]['minimum'] == 1
    assert info['bands'][0]['maximum'] == 1
    assert info['metadata']['']['AREA_OR_POINT'] == 'Area'


def test_create_water_mask_with_water_and_land(tmp_path, test_data_dir):
    input_tif = str(test_data_dir / 'water_mask_input.tif')
    output_tif = str(tmp_path / 'water_mask.tif')
    water_mask.create_water_mask(input_tif, output_tif)

    info = gdal.Info(output_tif, format='json')
    assert info['geoTransform'] == [199880.0, 80.0, 0.0, 1753560.0, 0.0, -80.0]
    assert info['bands'][0]['type'] == 'Byte'
    assert info['metadata']['']['AREA_OR_POINT'] == 'Point'

    ds = gdal.Open(str(output_tif))
    data = ds.GetRasterBand(1).ReadAsArray()
    expected = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])
    assert np.array_equal(data, expected)
    del ds
