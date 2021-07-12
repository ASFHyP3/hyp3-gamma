from datetime import datetime


import hyp3_metadata.util
from hyp3_metadata import create_metadata_file_set_insar, insar


def test_create_insar_gamma_readme(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_readme()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1.README.md.txt'
    assert output_file.exists()


def test_create_amp_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_amp_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_amp.tif.xml'
    assert output_file.exists()


def test_create_coherence_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_coherence_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_corr.tif.xml'
    assert output_file.exists()


def test_create_dem_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_dem_tif_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_dem.tif.xml'
    assert output_file.exists()


def test_create_los_displacement_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_los_displacement_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_los_disp.tif.xml'
    assert output_file.exists()


def test_create_look_vector_xmls(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_files = writer.create_look_vector_xmls()
    assert output_files == [
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_lv_phi.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_lv_theta.tif.xml',
    ]
    for file in output_files:
        assert file.exists()


def test_create_browse_xmls(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_files = writer.create_browse_xmls()
    assert output_files == [
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_color_phase.png.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_unw_phase.png.xml',
    ]
    for file in output_files:
        assert file.exists()


def test_unwrapped_phase_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_unwrapped_phase_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_unw_phase.tif.xml'
    assert output_file.exists()


def test_vertical_displacement_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_vertical_displacement_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_vert_disp.tif.xml'
    assert output_file.exists()


def test_wrapped_phase_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_wrapped_phase_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_wrapped_phase.tif.xml'
    assert output_file.exists()


def test_inc_map_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_inc_map_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_inc_map.tif.xml'
    assert output_file.exists()


def test_water_mask_xml(insar_product_dir):
    payload = hyp3_metadata.insar.marshal_metadata(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    writer = insar.InSarMetadataWriter(payload)
    output_file = writer.create_water_mask_xml()
    assert output_file == insar_product_dir / \
           'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_water_mask.tif.xml'
    assert output_file.exists()


def test_insar_gamma_all_files(insar_product_dir):
    files = create_metadata_file_set_insar(
        product_dir=insar_product_dir,
        reference_granule_name='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
        secondary_granule_name='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
        processing_date=datetime.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks='20x4',
        dem_name='GLO-30',
        plugin_name='hyp3_insar_gamma',
        plugin_version='2.3.0',
        processor_name='GAMMA',
        processor_version='20191203',
    )
    assert files == [
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1.README.md.txt',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_amp.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_corr.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_dem.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_los_disp.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_lv_phi.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_lv_theta.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_color_phase.png.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_unw_phase.png.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_unw_phase.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_vert_disp.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_wrapped_phase.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_inc_map.tif.xml',
        insar_product_dir / 'S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1_water_mask.tif.xml',
    ]
    for f in files:
        assert f.exists()
