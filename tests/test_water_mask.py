from osgeo import gdal

from hyp3_gamma import water_mask


gdal.UseExceptions()

TILE_PATH = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/'


def test_get_corners(test_data_dir):
    filepath_1 = str(test_data_dir / 'water_mask_input.tif')
    assert water_mask.get_corners(filepath_1) == [
        [-95.7978847, 15.8732749],
        [-95.797785, 15.8660511],
        [-95.7903217, 15.8661475],
        [-95.7904211, 15.8733713]
    ]

    filepath_2 = str(test_data_dir / 'test_geotiff.tif')
    assert water_mask.get_corners(filepath_2) == [
        [-117.6420428, 33.9023684],
        [-117.6419617, 33.8915461],
        [-117.6289846, 33.8916131],
        [-117.629064, 33.9024353]
    ]


def test_coord_to_tile():
    assert water_mask.coord_to_tile((0, 0)) == 'n00e000.tif'
    assert water_mask.coord_to_tile((-179, 0)) == 'n00w180.tif'
    assert water_mask.coord_to_tile((179, 0)) == 'n00e175.tif'
    assert water_mask.coord_to_tile((55, -45)) == 's45e055.tif'
    assert water_mask.coord_to_tile((-45, 55)) == 'n55w045.tif'


def test_get_tiles(test_data_dir):
    input1 = str(test_data_dir / 'water_mask_input.tif')
    assert water_mask.get_tiles(input1) == ['https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n15w100.tif']

    input2 = str(test_data_dir / 'test_geotiff.tif')
    assert water_mask.get_tiles(input2) == ['https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/n30w120.tif']


def test_create_water_mask(tmp_path, test_data_dir):
    input_image = str(test_data_dir / 'water_mask_input.tif')
    output_image = str(tmp_path / 'water_mask_output.wgs84')
    validation_text = str(test_data_dir / 'water_mask_output_info.txt')
    water_mask.create_water_mask(input_image, output_image, gdal_format='ISCE')
    info_from_img = gdal.Info(output_image)
    info_from_txt = open(validation_text).read()
    assert info_from_img.split('\n')[4:] == info_from_txt.split('\n')[4:]
