def test_rtc_gamma(script_runner):
    ret = script_runner.run('hyp3_gamma', '+h')
    assert ret.success


def test_rtc_gamma_passthrough(script_runner):
    ret = script_runner.run(
        'hyp3_gamma', 'rtc', '--help')
    assert ret.success
    assert 'rtc' in ret.stdout
    assert '--bucket-prefix' in ret.stdout


def test_check_coreg(script_runner):
    ret = script_runner.run('check_coreg.py', '-h')
    assert ret.success


def test_rtc_sentinel(script_runner):
    ret = script_runner.run('rtc_sentinel.py', '-h')
    assert ret.success


def test_smooth_dem_tiles(script_runner):
    ret = script_runner.run('smooth_dem_tiles.py', '-h')
    assert ret.success
