def test_hyp3_rtc_gamma(script_runner):
    ret = script_runner.run('hyp3_rtc_gamma', '-h')
    assert ret.success


def test_check_coreg(script_runner):
    ret = script_runner.run('check_coreg.py', '-h')
    assert ret.success


def test_rtc_sentinel(script_runner):
    ret = script_runner.run('rtc_sentinel.py', '-h')
    assert ret.success


def test_smooth_dem_tiles(script_runner):
    ret = script_runner.run('smooth_dem_tiles.py', '-h')
    assert ret.success


def test_xml2meta(script_runner):
    ret = script_runner.run('xml2meta.py', '-h')
    assert ret.success
