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


def test_hyp3_sentinel(script_runner):
    ret = script_runner.run('rtc_sentinel.py', '-h')
    assert ret.success


def test_insar_passthrough(script_runner):
    ret = script_runner.run(
        'hyp3_gamma', '++process', 'insar', '--help')
    assert ret.success
    assert 'insar' in ret.stdout
    assert '--include-los-displacement' in ret.stdout


def test_insar(script_runner):
    default_help = script_runner.run('insar', '-h')
    assert default_help.success


def test_ifm_sentinel(script_runner):
    ret = script_runner.run('ifm_sentinel.py', '-h')
    assert ret.success


def test_interf_pwr_s1_lt_tops_proc(script_runner):
    ret = script_runner.run('interf_pwr_s1_lt_tops_proc.py', '-h')
    assert ret.success


def test_unwrapping_geocoding(script_runner):
    ret = script_runner.run('unwrapping_geocoding.py', '-h')
    assert ret.success


def test_water_mask(script_runner):
    ret = script_runner.run('mask_water_bodies.py', '-h')
    assert ret.success
