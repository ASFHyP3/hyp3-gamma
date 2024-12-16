import numpy as np
from osgeo import gdal

from hyp3_gamma import water_mask


gdal.UseExceptions()

TILE_PATH = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/'


def test_get_corners(tmp_path, test_data_dir):
    filepath_1 = str(test_data_dir / 'water_mask_input.tif')
    corners_1 = np.round(np.asarray(water_mask.get_corners(filepath_1, tmp_path=str(tmp_path))), 13)
    filepath_2 = str(test_data_dir / 'test_geotiff.tif')
    corners_2 = np.round(np.asarray(water_mask.get_corners(filepath_2, tmp_path=str(tmp_path))), 13)
    assert (
        corners_1.all()
        == np.round(
            np.asarray(
                [
                    [-95.79788474283704, 15.873371301597947],
                    [-95.79788474283704, 15.86602285408288],
                    [-95.79053629532197, 15.873371301597947],
                    [-95.79053629532197, 15.86602285408288],
                ]
            ),
            13,
        ).all()
    )
    assert (
        corners_2.all()
        == np.round(
            np.asarray(
                [
                    [-117.64205396140792, 33.902434573500166],
                    [-117.64205396140792, 33.89166840507894],
                    [-117.62889531111531, 33.902434573500166],
                    [-117.62889531111531, 33.89166840507894],
                ]
            ),
            13,
        ).all()
    )


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


def test_get_tiles(tmp_path, test_data_dir):
    case_1 = (
        str(test_data_dir / 'water_mask_input.tif'),
        ['/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n15w100.tif'],
    )
    case_2 = (
        str(test_data_dir / 'test_geotiff.tif'),
        ['/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n30w120.tif'],
    )
    assert water_mask.get_tiles(case_1[0], tmp_path=str(tmp_path)) == case_1[1]
    assert water_mask.get_tiles(case_2[0], tmp_path=str(tmp_path)) == case_2[1]


def test_create_water_mask(tmp_path, test_data_dir):
    input_image = str(test_data_dir / 'water_mask_input.tif')
    output_image = str(tmp_path / 'water_mask_output.wgs84')
    validation_text = str(test_data_dir / 'water_mask_output_info.txt')
    water_mask.create_water_mask(input_image, output_image, gdal_format='ISCE', tmp_path=tmp_path)
    info_from_img = gdal.Info(output_image)
    info_from_txt = open(validation_text).read()
    # The first 4 lines are file paths; they will be different everytime and don't need to be checked.
    info_from_img = info_from_img.split('\n')[4:]
    info_from_txt = info_from_txt.split('\n')[4:]
    assert info_from_img == info_from_txt
