def test_insar_gamma(script_runner):
    ret = script_runner.run('insar_gamma', '-h')
    assert ret.success


def test_hyp3_insar_gamma(script_runner):
    ret = script_runner.run('hyp3_insar_gamma', '-h')
    assert ret.success


def test_hyp3_insar_gamma_v2(script_runner):
    ret = script_runner.run('hyp3_insar_gamma_v2', '-h')
    assert ret.success


def test_proc_insar_gamma(script_runner):
    ret = script_runner.run('procS1StackGAMMA.py', '-h')
    assert ret.success


def test_ifm_sentinel(script_runner):
    ret = script_runner.run('ifm_sentinel.py', '-h')
    assert ret.success


def test_interf_pwr_s1_lt_tops_proc(script_runner):
    ret = script_runner.run('interf_pwr_s1_lt_tops_proc.py', '-h')
    assert ret.success


def test_par_s1_slc(script_runner):
    ret = script_runner.run('par_s1_slc.py', '-h')
    assert ret.success


def test_unwrapping_geocoding(script_runner):
    ret = script_runner.run('unwrapping_geocoding.py', '-h')
    assert ret.success
