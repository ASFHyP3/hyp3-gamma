import os
import shutil

from osgeo import gdal

from hyp3_gamma import util


def test_earlier_granule_first():
    a = 'S1A_EW_GRDM_1SSH_20141112T235735_20141112T235835_003255_003C39_913F'
    b = 'S1A_EW_GRDM_1SSH_20141112T235835_20141112T235935_003255_003C39_D8E7'
    c = 'S1A_IW_SLC__1SDV_20200701T170703_20200701T170730_033264_03DA9B_CAB2'

    assert util.earlier_granule_first(a, a) == (a, a)

    assert util.earlier_granule_first(a, c) == (a, c)
    assert util.earlier_granule_first(c, a) == (a, c)

    assert util.earlier_granule_first(a, b) == (a, b)
    assert util.earlier_granule_first(b, a) == (a, b)


def test_unzip_granule(tmp_path, test_data_dir):
    zip_file = 'S1A_IW_SLC__1SDV_20170525T025145_20170525T025157_016732_01BCA6_CEBE.zip'
    shutil.copy(test_data_dir / zip_file, tmp_path)
    os.chdir(tmp_path)

    safe_dir = util.unzip_granule(zip_file)
    assert safe_dir == 'S1A_IW_SLC__1SDV_20170525T025145_20170525T025157_016732_01BCA6_CEBE.SAFE'
    assert os.path.isdir(safe_dir)
    assert os.path.isfile(zip_file)


def test_unzip_granule_and_remove(tmp_path, test_data_dir):
    zip_file = 'S1A_IW_SLC__1SDV_20170525T025145_20170525T025157_016732_01BCA6_CEBE.zip'
    shutil.copy(test_data_dir / zip_file, tmp_path)
    os.chdir(tmp_path)

    safe_dir = util.unzip_granule(zip_file, remove=True)
    assert safe_dir == 'S1A_IW_SLC__1SDV_20170525T025145_20170525T025157_016732_01BCA6_CEBE.SAFE'
    assert os.path.isdir(safe_dir)
    assert not os.path.exists(zip_file)


def test_set_pixel_as_point(tmp_path, test_data_dir):
    shutil.copy(test_data_dir / 'test_geotiff.tif', tmp_path)
    geotiff = str(tmp_path / 'test_geotiff.tif')
    info = gdal.Info(geotiff, format='json')
    assert info['geoTransform'] == [440720.0, 60.0, 0.0, 3751320.0, 0.0, -60.0]
    assert info['metadata']['']['AREA_OR_POINT'] == 'Area'

    util.set_pixel_as_point(geotiff)
    info = gdal.Info(geotiff, format='json')
    assert info['geoTransform'] == [440750.0, 60.0, 0.0, 3751290.0, 0.0, -60.0]
    assert info['metadata']['']['AREA_OR_POINT'] == 'Point'
