from datetime import datetime

import pytest

import hyp3_metadata.rtc
import hyp3_metadata.util
from hyp3_metadata import create_metadata_file_set_rtc, rtc
from hyp3_metadata.rtc import SUPPORTED_DEMS


def test_create_rtc_gamma_readme(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file = writer.create_readme()
    assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.README.md.txt'
    assert output_file.exists()


def test_rtc_gamma_product(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file_list = writer.create_product_xmls()
    assert output_file_list == [
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VV.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VH.tif.xml',
    ]
    for output_file in output_file_list:
        assert output_file.exists()


def test_create_dem_xml(rtc_product_dir):
    for dem_name in SUPPORTED_DEMS:
        payload = hyp3_metadata.rtc.marshal_metadata(
            product_dir=rtc_product_dir,
            granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
            dem_name=dem_name,
            processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
            looks=1,
            plugin_name='hyp3_rtc_gamma',
            plugin_version='2.3.0',
            processor_name='GAMMA',
            processor_version='20191203',
        )
        writer = rtc.RtcMetadataWriter(payload)
        output_file = writer.create_dem_xml()
        assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_dem.tif.xml'
        assert output_file.exists()
        output_file.unlink()

    payload['dem_name'] = 'unknown'
    writer = rtc.RtcMetadataWriter(payload)
    unknown_dem_file = writer.create_dem_xml()
    assert unknown_dem_file is None

    payload['dem_name'] = ''
    writer = rtc.RtcMetadataWriter(payload)
    empty_name_file = writer.create_dem_xml()
    assert empty_name_file is None

    payload['dem_name'] = None
    with pytest.raises(AttributeError):
        writer = rtc.RtcMetadataWriter(payload)
        _ = writer.create_dem_xml()


def test_create_browse_xmls(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_files = writer.create_browse_xmls()
    assert output_files == [
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.png.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.png.xml',
    ]
    for file in output_files:
        assert file.exists()


def test_rtc_gamma_area(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file = writer.create_area_xml()
    assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_area.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_inc_map(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file = writer.create_inc_map_xml()
    assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_inc_map.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_ls_map(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file = writer.create_ls_map_xml()
    assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_ls_map.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_rgb(rtc_product_dir):
    payload = hyp3_metadata.rtc.marshal_metadata(
        product_dir=rtc_product_dir,
        granule_name='S1A_IW_SLC__1SDV_20150621T120220_20150621T120232_006471_008934_72D8',
        dem_name='SRTMGL1',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=1,
        plugin_name='hyp3_rtc_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = rtc.RtcMetadataWriter(payload)
    output_file = writer.create_rgb_xml()
    assert output_file == rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.tif.xml'
    assert output_file.exists()


def test_rtc_gamma_all_files(rtc_product_dir):
    files = create_metadata_file_set_rtc(
        product_dir=rtc_product_dir,
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
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VV.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_VH.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.png.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.png.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2.README.md.txt',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_dem.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_inc_map.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_ls_map.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_area.tif.xml',
        rtc_product_dir / 'S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2_rgb.tif.xml',
    ]
    for f in files:
        assert f.exists()


def test_thumbnail_no_such_reference_file(test_data_folder):
    reference_file = test_data_folder / 'rtc' / 'no_such_file'
    assert hyp3_metadata.util.get_thumbnail_encoded_string(reference_file) == ''


def test_thumbnail_reference_file_is_browse(test_data_folder):
    reference_file = test_data_folder / 'rtc' / 'rtc.png'
    encoded_string = hyp3_metadata.util.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844


def test_thumbnail_reference_file_is_pol(test_data_folder):
    reference_file = test_data_folder / 'rtc' / 'rtc.png'
    encoded_string = hyp3_metadata.util.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844

    reference_file = test_data_folder / 'rtc' / 'rtc.png'
    encoded_string = hyp3_metadata.util.get_thumbnail_encoded_string(reference_file)
    assert len(encoded_string) == 844


def test_thumbnail_reference_file_is_dem(test_data_folder):
    browse_file = test_data_folder / 'rtc' / 'rtc_dem.png'
    encoded_string = hyp3_metadata.util.get_thumbnail_encoded_string(browse_file)
    assert len(encoded_string) == 844


def test_decode_product():
    name = 'S1A_IW_20150621T120220_SVP_RTC10_G_sauned_F8E2'
    assert hyp3_metadata.rtc.decode_product(name) == {
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
    assert hyp3_metadata.rtc.decode_product(name) == {
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
    writer = rtc.RtcMetadataWriter({})
    assert writer.create_metadata_file(
        payload={},
        template=test_data_folder / 'rtc_dem.tif',
        reference_file=test_data_folder / 'does_not_exist.tif',
    ) is None
