def test_hyp3_gamma(script_runner):
    ret = script_runner.run('hyp3_gamma', '+h')
    assert ret.success


def test_rtc(script_runner):
    ret = script_runner.run('rtc', '-h')
    assert ret.success


def test_hyp3_gamma_rtc_passthrough(script_runner):
    ret = script_runner.run('hyp3_gamma', 'rtc', '--help')
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


def test_geocode(script_runner):
     ret = script_runner.run('geocode', '-h')
     assert ret.success


def test_geocode_not_implemented(script_runner):
    ret = script_runner.run('geocode')
    assert not ret.success
    assert 'NotImplementedError' in ret.stderr


def test_hyp3_gamma_geocode_passthrough(script_runner):
    ret = script_runner.run('hyp3_gamma', 'geocode', '--help')
    assert not ret.success
    assert 'invalid choice' in ret.stderr


def test_geocode_sentinel(script_runner):
    ret = script_runner.run('geocode_sentinel.py', '-h')
    assert ret.success


def test_insar(script_runner):
    ret = script_runner.run('insar', '-h')
    assert ret.success


def test_hyp3_gamma_rtc_passthrough(script_runner):
    ret = script_runner.run('hyp3_gamma', 'insar', '--help')
    assert ret.success
    assert 'insar' in ret.stdout
    assert '--bucket-prefix' in ret.stdout


def test_ifm_sentinel(script_runner):
    ret = script_runner.run('ifm_sentinel.py', '-h')
    assert ret.success


def test_interf_pwr_s1_lt_tops_proc(script_runner):
    ret = script_runner.run('interf_pwr_s1_lt_tops_proc.py', '-h')
    assert ret.success


def test_unwrapping_geocoding(script_runner):
    ret = script_runner.run('unwrapping_geocoding.py', '-h')
    assert ret.success
