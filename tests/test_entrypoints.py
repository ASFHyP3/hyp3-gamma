def test_hyp3_rtc_gamma(script_runner):
    ret = script_runner.run('hyp3_rtc_gamma', '-h')
    assert ret.success


def test_proc_rtc_gamma(script_runner):
    ret = script_runner.run('proc_rtc_gamma', '-h')
    assert ret.success
