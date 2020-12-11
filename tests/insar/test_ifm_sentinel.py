from re import match

import pytest
from hyp3lib import GranuleError

from hyp3_gamma.insar import ifm_sentinel


def test_get_copol():
    assert ifm_sentinel.get_copol('S1B_WV_SLC__1SSV_20200923T184541_20200923T185150_023506_02CA71_AABB') == 'vv'
    assert ifm_sentinel.get_copol('S1B_IW_GRDH_1SDV_20200924T092954_20200924T093026_023515_02CABC_6C62') == 'vv'
    assert ifm_sentinel.get_copol('S1B_IW_GRDH_1SSH_20200924T112903_20200924T112932_023516_02CAC7_D003') == 'hh'
    assert ifm_sentinel.get_copol('S1B_IW_OCN__2SDH_20200924T090450_20200924T090519_023515_02CAB8_917B') == 'hh'
    with pytest.raises(GranuleError):
        ifm_sentinel.get_copol('S1A_EW_GRDM_1SHH_20150513T080355_20150513T080455_005900_007994_35D2')
    with pytest.raises(GranuleError):
        ifm_sentinel.get_copol('S1A_EW_GRDM_1SHV_20150509T230833_20150509T230912_005851_00787D_3BE5')
    with pytest.raises(GranuleError):
        ifm_sentinel.get_copol('S1A_IW_SLC__1SVH_20150706T015744_20150706T015814_006684_008EF7_9B69')
    with pytest.raises(GranuleError):
        ifm_sentinel.get_copol('S1A_IW_GRDH_1SVV_20150706T015720_20150706T015749_006684_008EF7_54BA')


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
    assert match(r'S1AA_20160527T014319_20160714T014322_VVP049_INT80_G_ueF_[0-9A-F]{4}$', name)

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
    assert match(r'S1BA_20200918T073646_20200906T073646_HHR012_INT40_G_ueF_[0-9A-F]{4}$', name)

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
    assert match(r'S1AB_20150101T230038_20200924T005722_VVO2093_INT40_G_ueF_[0-9A-F]{4}$', name)
