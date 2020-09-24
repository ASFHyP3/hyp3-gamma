from re import match

from hyp3_insar_gamma import ifm_sentinel


def test_least_precise_orbit_of():
    precise = 'S1A_OPER_AUX_POEORB_OPOD_20160616T121500_V20160526T225943_20160528T005943'
    restituted = 'S1B_OPER_AUX_RESORB_OPOD_20200907T115242_V20200906T042511_20200906T074241'
    predicted = None
    assert ifm_sentinel.least_precise_orbit_of([precise, precise]) == 'P'
    assert ifm_sentinel.least_precise_orbit_of([precise, restituted]) == 'R'
    assert ifm_sentinel.least_precise_orbit_of([precise, predicted]) == 'O'
    assert ifm_sentinel.least_precise_orbit_of([restituted, restituted]) == 'R'
    assert ifm_sentinel.least_precise_orbit_of([restituted, predicted]) == 'O'
    assert ifm_sentinel.least_precise_orbit_of([predicted, predicted]) == 'O'


def test_get_product_name():
    payload = {
        'reference_name': 'S1A_IW_SLC__1SSV_20160527T014319_20160527T014346_011438_011694_26B0',
        'secondary_name': 'S1A_IW_SLC__1SSV_20160714T014322_20160714T014349_012138_012CE7_96A0',
        'orbit_files': [
            'S1A_OPER_AUX_POEORB_OPOD_20160616T121500_V20160526T225943_20160528T005943.EOF',
            'S1A_OPER_AUX_POEORB_OPOD_20160616T121500_V20160526T225943_20160528T005943.EOF',
        ],
        'pixel_spacing': 80,
    }
    name = ifm_sentinel.get_product_name(**payload)
    assert match(r'S1AA_20160527T014319_20160714T014322_SVP049_INT80_G_ueF_[0-9A-F]{4}$', name)

    payload = {
        'reference_name': 'S1B_IW_SLC__1SDH_20200918T073646_20200918T073716_023426_02C7FC_6374',
        'secondary_name': 'S1A_IW_SLC__1SDH_20200906T073646_20200906T073716_023251_02C278_AE75',
        'orbit_files': [
            'S1B_OPER_AUX_RESORB_OPOD_20200907T115242_V20200906T042511_20200906T074241.EOF',
            'S1A_OPER_AUX_POEORB_OPOD_20160616T121500_V20160526T225943_20160528T005943.EOF',
        ],
        'pixel_spacing': 40
    }
    name = ifm_sentinel.get_product_name(**payload)
    assert match(r'S1BA_20200918T073646_20200906T073646_DHR012_INT40_G_ueF_[0-9A-F]{4}$', name)

    payload = {
        'reference_name': 'S1A_IW_SLC__1SSV_20150101T230038_20150101T230114_003984_004CC1_0481',
        'secondary_name': 'S1B_IW_SLC__1SDV_20200924T005722_20200924T005750_023510_02CA91_4873',
        'orbit_files': [
            'S1B_OPER_AUX_RESORB_OPOD_20200907T115242_V20200906T042511_20200906T074241.EOF',
            None,
        ],
        'pixel_spacing': 40
    }
    name = ifm_sentinel.get_product_name(**payload)
    assert match(r'S1AB_20150101T230038_20200924T005722_SVO2093_INT40_G_ueF_[0-9A-F]{4}$', name)
