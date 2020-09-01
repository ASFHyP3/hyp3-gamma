from datetime import datetime, timezone

from hyp3_metadata import __main__


def test_create_rtc_gamma_readme(tmp_path):
    readme_filename = tmp_path / 'readme.txt'
    __main__.create_rtc_gamma_readme(
        readme_filename=readme_filename,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        resolution=30.0,
        radiometry='gamma-0',
        scale='power',
        filter_applied=False,
        looks=3,
        projection='WGS 1984 UTM Zone 15N',
        dem_name='SRTMGL1',
        plugin_version='2.3.0',
        gamma_version='20191203',
        processing_date=datetime.now(timezone.utc),
    )
    assert readme_filename.exists()


def test_create_dem_xml(tmp_path, test_data_folder):
    output_filename = tmp_path / 'readme.txt'
    __main__.create_dem_xml(
        output_filename=output_filename,
        dem_filename=test_data_folder / 'S1A_IW_20150621T120220_SVP_RTC10_G_saufem_F8E2_dem.tif',
        dem_name='SRTMGL1',
        processing_date=datetime.now(timezone.utc),
        plugin_version='2.3.0',
        gamma_version='20191203',
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8'
    )
    assert output_filename.exists()
