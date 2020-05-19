def test_hyp3_insar_gamma(script_runner):
    ret = script_runner.run('hyp3_insar_gamma', '-h')
    assert ret.success


def test_proc_insar_gamma(script_runner):
    ret = script_runner.run('procS1StackGAMMA.py', '-h')
    assert ret.success
