def test_rtc_gamma(script_runner):
    ret = script_runner.run('rtc_gamma', '+h')
    assert ret.success


def test_rtc_gamma_passthrough(script_runner):
    ret = script_runner.run('rtc_gamma', '--version')
    assert ret.success
    assert 'rtc_gamma v' in ret.stdout
    assert 'hyp3lib v' in ret.stdout
    assert 'hyp3proclib v' in ret.stdout


def test_rtc_gamma_passthrough_v2(script_runner):
    ret = script_runner.run(
        'rtc_gamma', '++entrypoint', 'hyp3_rtc_gamma_v2', '--help')
    assert ret.success
    assert 'hyp3_rtc_gamma_v2' in ret.stdout
    assert '--bucket-prefix' in ret.stdout


def test_hyp3_rtc_gamma_v2(script_runner):
    ret = script_runner.run('hyp3_rtc_gamma_v2', '-h')
    assert ret.success


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
