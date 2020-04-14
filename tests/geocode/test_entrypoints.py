def test_hyp3_geocode(script_runner):
    ret = script_runner.run('hyp3_geocode', '-h')
    assert ret.success


def test_proc_geocode(script_runner):
    ret = script_runner.run('proc_geocode', '-h')
    assert ret.success
