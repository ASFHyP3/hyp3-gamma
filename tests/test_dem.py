from osgeo import gdal

from hyp3_gamma import dem

gdal.UseExceptions()


def test_gdal_config_manager():
    gdal.SetConfigOption('OPTION1', 'VALUE1')

    assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
    assert gdal.GetConfigOption('OPTION2') is None
    assert gdal.GetConfigOption('OPTION3') is None
    assert gdal.GetConfigOption('OPTION4') is None

    with dem.GDALConfigManager(OPTION2='VALUE2', OPTION3='VALUE3'):
        assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
        assert gdal.GetConfigOption('OPTION2') == 'VALUE2'
        assert gdal.GetConfigOption('OPTION3') == 'VALUE3'
        assert gdal.GetConfigOption('OPTION4') is None

        gdal.SetConfigOption('OPTION4', 'VALUE4')

    assert gdal.GetConfigOption('OPTION1') == 'VALUE1'
    assert gdal.GetConfigOption('OPTION2') is None
    assert gdal.GetConfigOption('OPTION3') is None
    assert gdal.GetConfigOption('OPTION4') == 'VALUE4'
