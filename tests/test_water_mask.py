import numpy as np
import pytest
from osgeo import gdal

from hyp3_isce2 import water_mask

gdal.UseExceptions()

TILE_PATH = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/'


def test_get_corners(tmp_path):
    filepath_1 = 'tests/data/water_mask_input.tif'
    corners_1 = np.round(np.asarray(water_mask.get_corners(filepath_1, tmp_path=str(tmp_path))), 13)
    filepath_2 = 'tests/data/test_geotiff.tif'
    corners_2 = np.round(np.asarray(water_mask.get_corners(filepath_2, tmp_path=str(tmp_path))), 13)
    assert corners_1.all() == np.round(np.asarray([
        [-95.79788474283704, 15.873371301597947],
        [-95.79788474283704, 15.86602285408288],
        [-95.79053629532197, 15.873371301597947],
        [-95.79053629532197, 15.86602285408288]
    ]), 13).all()
    assert corners_2.all() == np.round(np.asarray([
        [-117.64205396140792, 33.902434573500166],
        [-117.64205396140792, 33.89166840507894],
        [-117.62889531111531, 33.902434573500166],
        [-117.62889531111531, 33.89166840507894]
    ]), 13).all()


def test_coord_to_tile():
    case_1 = ((0, 0), 'n00e000.tif')
    case_2 = ((-179, 0), 'n00w180.tif')
    case_3 = ((179, 0), 'n00e175.tif')
    case_4 = ((55, -45), 's45e055.tif')
    case_5 = ((-45, 55), 'n55w045.tif')
    assert water_mask.coord_to_tile(case_1[0]) == case_1[1]
    assert water_mask.coord_to_tile(case_2[0]) == case_2[1]
    assert water_mask.coord_to_tile(case_3[0]) == case_3[1]
    assert water_mask.coord_to_tile(case_4[0]) == case_4[1]
    assert water_mask.coord_to_tile(case_5[0]) == case_5[1]


def test_get_tiles(tmp_path):
    case_1 = (
        'tests/data/water_mask_input.tif',
        ['/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n15w100.tif']
    )
    case_2 = (
        'tests/data/test_geotiff.tif',
        ['/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n30w120.tif']
    )
    assert water_mask.get_tiles(case_1[0], tmp_path=str(tmp_path)) == case_1[1]
    assert water_mask.get_tiles(case_2[0], tmp_path=str(tmp_path)) == case_2[1]


@pytest.mark.integration
def test_create_water_mask(tmp_path):
    input_image = 'tests/data/water_mask_input.tif'
    output_image = 'tests/data/water_mask_output.wgs84'
    validation_text = 'tests/data/water_mask_output_info.txt'
    water_mask.create_water_mask(input_image, output_image, gdal_format='ISCE', tmp_path=tmp_path)
    info_from_img = gdal.Info(output_image)
    info_from_txt = open(validation_text).read()
    assert info_from_img == info_from_txt
