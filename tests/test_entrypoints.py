def test_hyp3_gamma(script_runner):
    ret = script_runner.run('hyp3_gamma', '+h')
    assert ret.success


def test_rtc_passthrough(script_runner):
    ret = script_runner.run(
        'hyp3_gamma', '++process', 'rtc', '--help')
    assert ret.success
    assert 'rtc' in ret.stdout
    assert '--radiometry' in ret.stdout


def test_rtc(script_runner):
    ret = script_runner.run('rtc', '-h')
    assert ret.success


def test_check_coreg(script_runner):
    ret = script_runner.run('check_coreg.py', '-h')
    assert ret.success


def test_hyp3_sentinel(script_runner):
    ret = script_runner.run('rtc_sentinel.py', '-h')
    assert ret.success


def test_smooth_dem_tiles(script_runner):
    ret = script_runner.run('smooth_dem_tiles.py', '-h')
    assert ret.success
