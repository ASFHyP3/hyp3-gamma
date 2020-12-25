from os import chdir
from re import match

import pytest
from hyp3lib import GranuleError

from hyp3_gamma.rtc import rtc_sentinel


def test_get_product_name():
    payload = {
        'granule_name': 'S1A_S1_GRDH_1SSH_20181121T184017_20181121T184046_024690_02B6ED_6946',
        'orbit_file': 'S1A_OPER_AUX_POEORB_OPOD_20181211T120749_V20181120T225942_20181122T005942.EOF',
        'resolution': 30,
        'gamma0': False,
        'power': False,
        'filtered': False,
        'matching': False,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1A_S1_20181121T184017_SHP_RTC30_G_sauned_[0-9A-F]{4}$', name)

    payload = {
        'granule_name': 'S1B_WV_OCN__2SSV_20200714T162902_20200714T163511_022469_02AA55_1A7D',
        'orbit_file': 'S1B_OPER_AUX_RESORB_OPOD_20200714T223706_V20200714T150658_20200714T182428.EOF',
        'resolution': 10,
        'power': True,
        'filtered': True,
        'gamma0': True,
        'matching': True,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1B_WV_20200714T162902_SVR_RTC10_G_gpufem_[0-9A-F]{4}$', name)

    payload = {
        'granule_name': 'S1B_IW_SLC__1SDV_20200714T152128_20200714T152150_022469_02AA50_9A64',
        'resolution': 30.999,
    }
    name = rtc_sentinel.get_product_name(**payload)
    assert match('S1B_IW_20200714T152128_DVO_RTC30_G_gpuned_[0-9A-F]{4}$', name)

    name = rtc_sentinel.get_product_name('S1A_EW_RAW__0SDH_20151118T190420_20151118T190529_008663_00C507_0A5F', None)
    assert match('S1A_EW_20151118T190420_DHO_RTC30_G_gpuned_[0-9A-F]{4}$', name)

    name = rtc_sentinel.get_product_name('S1A_EW_RAW__0SDH_20151118T190420_20151118T190529_008663_00C507_0A5F', 'foo')
    assert match('S1A_EW_20151118T190420_DHO_RTC30_G_gpuned_[0-9A-F]{4}$', name)


def test_get_polarizations():
    granule = 'S1A_S1_GRDH_1SSH_20181121T184017_20181121T184046_024690_02B6ED_6946'
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=False) == ['hh']
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=True) == ['hh']

    granule = 'S1B_WV_OCN__2SSV_20200714T162902_20200714T163511_022469_02AA55_1A7D'
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=False) == ['vv']
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=True) == ['vv']

    granule = 'S1A_EW_RAW__0SDH_20151118T190420_20151118T190529_008663_00C507_0A5F'
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=False) == ['hh', 'hv']
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=True) == ['hh']

    granule = 'S1B_IW_SLC__1SDV_20200714T152128_20200714T152150_022469_02AA50_9A64'
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=False) == ['vv', 'vh']
    assert rtc_sentinel.get_polarizations(granule, skip_cross_pol=True) == ['vv']

    with pytest.raises(GranuleError):
        rtc_sentinel.get_polarizations('foo')


def test_get_looks():
    assert rtc_sentinel.get_looks('GRDH', 90.0) == 9
    assert rtc_sentinel.get_looks('GRDH', 30.0) == 6
    assert rtc_sentinel.get_looks('GRDH', 10.0) == 1
    assert rtc_sentinel.get_looks('GRDM', 90.0) == 9
    assert rtc_sentinel.get_looks('GRDM', 30.0) == 3
    assert rtc_sentinel.get_looks('GRDM', 10.0) == 1
    assert rtc_sentinel.get_looks('SLC', 90.0) == 9
    assert rtc_sentinel.get_looks('SLC', 30.0) == 3
    assert rtc_sentinel.get_looks('SLC', 10.0) == 1


def test_get_granule_type():
    granule = 'S1A_S1_GRDH_1SSH_20181121T184017_20181121T184046_024690_02B6ED_6946'
    assert rtc_sentinel.get_granule_type(granule) == 'GRDH'

    granule = 'S1B_IW_SLC__1SDV_20200714T152128_20200714T152150_022469_02AA50_9A64'
    assert rtc_sentinel.get_granule_type(granule) == 'SLC'

    with pytest.raises(ValueError):
        rtc_sentinel.get_granule_type('S1B_WV_OCN__2SSV_20200714T162902_20200714T163511_022469_02AA55_1A7D')

    with pytest.raises(ValueError):
        rtc_sentinel.get_granule_type('S1A_EW_RAW__0SDH_20151118T190420_20151118T190529_008663_00C507_0A5F')


def test_append_additional_log_files(tmp_path):
    chdir(tmp_path)
    main_log = 'main.log'
    with open(main_log, 'w') as f:
        f.write('hello world\n')

    log1 = '1.log'
    with open(log1, 'w') as f:
        f.write('foo\n')

    log2 = '2.log'
    with open(log2, 'w') as f:
        f.write('bar\n')

    rtc_sentinel.append_additional_log_files(main_log, '?.log')
    with open(main_log) as f:
        content = f.readlines()
    assert content == [
        'hello world\n',
        '==============================================\n',
        'Log: 1.log\n',
        '==============================================\n',
        'foo\n',
        '==============================================\n',
        'Log: 2.log\n',
        '==============================================\n',
        'bar\n'
    ]
