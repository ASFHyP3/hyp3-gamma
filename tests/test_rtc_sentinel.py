from re import match

from hyp3_rtc_gamma import rtc_sentinel


def test_get_product_name():
    payload = {
        'granule_name': 'S1B_IW_SLC__1SDV_20200714T152128_20200714T152150_022469_02AA50_9A64',
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1B_IW_20200714T152128_DVO_RTC30_G_uepng_[0-9A-F]{6}$', name)

    payload = {
        'granule_name': 'S1A_S1_GRDH_1SSH_20181121T184017_20181121T184046_024690_02B6ED_6946',
        'orbit_file': 'S1A_OPER_AUX_POEORB_OPOD_20181211T120749_V20181120T225942_20181122T005942.EOF',
        'resolution': 30,
        'water_mask': False,
        'clipped': False,
        'gamma0': False,
        'power': False,
        'filtered': False,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1A_S1_20181121T184017_SHP_RTC30_G_ueans_[0-9A-F]{6}$', name)

    payload = {
        'granule_name': 'S1B_WV_OCN__2SSV_20200714T162902_20200714T163511_022469_02AA55_1A7D',
        'orbit_file': 'S1B_OPER_AUX_RESORB_OPOD_20200714T223706_V20200714T150658_20200714T182428.EOF',
        'resolution': 10,
        'water_mask': True,
        'clipped': True,
        'gamma0': True,
        'power': True,
        'filtered': True,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1B_WV_20200714T162902_SVR_RTC10_G_wcpfg_[0-9A-F]{6}$', name)

    payload = {
        'granule_name': 'S1A_EW_RAW__0SDH_20151118T190420_20151118T190529_008663_00C507_0A5F',
        'orbit_file': None,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1A_EW_20151118T190420_DHO_RTC30_G_uepng_[0-9A-F]{6}$', name)
