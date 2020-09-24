def test_insar_gamma(script_runner):
    default_help = script_runner.run('insar_gamma', '-h')
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
