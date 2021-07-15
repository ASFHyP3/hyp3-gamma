from osgeo import gdal

from hyp3_gamma import water_mask

gdal.UseExceptions()


def test_create_water_mask(tmp_path, test_data_dir):
    input_tif = str(test_data_dir / 'test_geotiff.tif')
    output_tif = str(tmp_path / 'water_mask.tif')
    water_mask.create_water_mask(input_tif, output_tif)

    info = gdal.Info(output_tif, format='json', stats=True)
    assert info['size'] == [20, 20]
    assert info['geoTransform'] == [440720.0, 60.0, 0.0, 3751320.0, 0.0, -60.0]
    assert info['bands'][0]['type'] == 'Byte'
    assert info['bands'][0]['minimum'] == 1
    assert info['bands'][0]['maximum'] == 1
