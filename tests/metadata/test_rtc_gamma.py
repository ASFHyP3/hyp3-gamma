from datetime import datetime

import pytest

from hyp3_metadata import create


def test_create_rtc_gamma_readme(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file = create.create_readme(payload)
    assert output_file == product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.README.md.txt'
    assert output_file.exists()


def test_rtc_gamma_product(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file_list = create.create_product_xmls(payload)
    assert output_file_list == [
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VV.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VH.tif.xml',
    ]
    for output_file in output_file_list:
        assert output_file.exists()


def test_create_dem_xml(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file = create.create_dem_xml(payload)
    assert output_file == product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_dem.tif.xml'
    assert output_file.exists()

    output_file.unlink()
    payload['dem_name'] = 'unknown'
    unknown_dem_file = create.create_dem_xml(payload)
    assert unknown_dem_file is None

    payload['dem_name'] = ''
    empty_name_file = create.create_dem_xml(payload)
    assert empty_name_file is None

    payload['dem_name'] = None
    with pytest.raises(AttributeError):
        _ = create.create_dem_xml(payload)


def test_create_browse_xmls(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_files = create.create_browse_xmls(payload)
    assert output_files == [
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.png.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.png.xml',
    ]
    for file in output_files:
        assert file.exists()


def test_rtc_gamma_area(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file = create.create_area_xml(payload)
    assert output_file == product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_area.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_inc_map(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file = create.create_inc_map_xml(payload)
    assert output_file == product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_inc_map.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_ls_map(product_dir):
    payload = create.marshal_metadata(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )

    output_file = create.create_ls_map_xml(payload)
    assert output_file == product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_ls_map.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_all_files(product_dir):
    files = create.create_metadata_file_set(
        product_dir=product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    assert files == [
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VV.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VH.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.png.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.png.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.README.md.txt',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_dem.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_inc_map.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_ls_map.tif.xml',
        product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_area.tif.xml',
    ]
    for f in files:
        assert f.exists()


def test_thumbnail_no_such_reference_file(test_data_folder):
    reference_file = test_data_folder / 'no_such_file'
    assert create.get_thumbnail_encoded_string(reference_file) == ''


def test_thumbnail_reference_file_is_browse(test_data_folder):
    reference_file = test_data_folder / 'rtc.png'
    encoded_string = create.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844


def test_thumbnail_reference_file_is_pol(test_data_folder):
    reference_file = test_data_folder / 'rtc_VV.png'
    encoded_string = create.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844

    reference_file = test_data_folder / 'rtc_VH.png'
    encoded_string = create.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844


def test_thumbnail_reference_file_is_dem(test_data_folder):
    reference_file = test_data_folder / 'rtc_dem.tif'
    encoded_string = create.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844


def test_decode_product():
    name = 'S1A_IW_20150621T120220_SVP_RTC10_G_sauned_F8E2'
    assert create.decode_product(name) == {
        'pixel_spacing': 10,
        'radiometry': 'sigma-0',
        'scale': 'amplitude',
        'masked': False,
        'filter_applied': False,
        'clipped': False,
        'matching': False,
        'polarizations': ('VV',),
    }

    name = 'S1B_IW_20150621T120220_DHR_RTC30_G_gpwfcm_F8E2'
    assert create.decode_product(name) == {
        'pixel_spacing': 30,
        'radiometry': 'gamma-0',
        'scale': 'power',
        'masked': True,
        'filter_applied': True,
        'clipped': True,
        'matching': True,
        'polarizations': ('HH', 'HV'),
    }


def test_create_metadata_no_such_reference_file(test_data_folder):
    assert create.create_metadata_file(
        payload={},
        template=test_data_folder / 'rtc_dem.tif',
        reference_file=test_data_folder / 'does_not_exist.tif',
    ) is None
