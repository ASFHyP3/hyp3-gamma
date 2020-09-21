from re import match

from hyp3_insar_gamma import __main__ as main


def test_get_product_name():
    payload = {
        'reference_name': 'S1A_IW_SLC__1SSV_20160527T014319_20160527T014346_011438_011694_26B0',
        'secondary_name': 'S1A_IW_SLC__1SSV_20160714T014322_20160714T014349_012138_012CE7_96A0',
        'orbit_file': 'S1A_OPER_AUX_POEORB_OPOD_20160616T121500_V20160526T225943_20160528T005943.EOF',
        'pixel_spacing': 30,
        'masked': False,
    }
    name = main.get_product_name(**payload)
    assert match(r'S1AA_20160527T014319_20160714T014322_SVP049_INT30_G_ueF_[0-9A-F]{4}$', name)

    payload = {
        'reference_name': 'S1B_IW_SLC__1SDH_20200918T073646_20200918T073716_023426_02C7FC_6374',
        'secondary_name': 'S1A_IW_SLC__1SDH_20200906T073646_20200906T073716_023251_02C278_AE75',
        'orbit_file': 'S1B_OPER_AUX_RESORB_OPOD_20200907T115242_V20200906T042511_20200906T074241.EOF',
        'pixel_spacing': 10,
        'masked': True,
    }
    name = main.get_product_name(**payload)
    assert match(r'S1BA_20200918T073646_20200906T073646_DHR012_INT10_G_weF_[0-9A-F]{4}$', name)
