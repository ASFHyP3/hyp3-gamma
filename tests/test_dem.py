from osgeo import gdal

from hyp3_gamma import dem

gdal.UseExceptions()


def test_gdal_config_manager():
    assert gdal.GetConfigOption('FOO') is None
    assert gdal.GetConfigOption('HELLO') is None
    assert gdal.GetConfigOption('FOREVER') is None
    assert gdal.GetConfigOption('ANOTHER') is None

    gdal.SetConfigOption('FOREVER', 'TOGETHER')

    with dem.GDALConfigManager(FOO='BAR', HELLO='WORLD'):
        assert gdal.GetConfigOption('FOO') == 'BAR'
        assert gdal.GetConfigOption('HELLO') == 'WORLD'
        assert gdal.GetConfigOption('FOREVER') == 'TOGETHER'
        gdal.SetConfigOption('ANOTHER', 'OPTION')

    assert gdal.GetConfigOption('FOO') is None
    assert gdal.GetConfigOption('HELLO') is None
    assert gdal.GetConfigOption('FOREVER') == 'TOGETHER'
    assert gdal.GetConfigOption('ANOTHER') == 'OPTION'
