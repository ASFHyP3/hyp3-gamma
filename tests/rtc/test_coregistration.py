import pytest

from hyp3_gamma.rtc import coregistration


def test_get_offset(tmp_path):
    diff_par = tmp_path / 'diff_par'

    with open(diff_par, 'w') as f:
        f.write('range_offset_polynomial:    -3.00000  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00\n')
        f.write('azimuth_offset_polynomial:   4.00000  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00\n')
    assert coregistration.get_offset(diff_par) == 5.0

    with open(diff_par, 'w') as f:
        f.write('range_offset_polynomial:     1.00000 -2.0000e+00  3.0000e+00 -4.0000e+00   5.0000e+00 -6.0000e+00\n')
        f.write('azimuth_offset_polynomial:  -7.00000  8.0000e+00 -9.0000e+00 10.0000e+00 -11.0000e+00 12.0000e+00\n')
    assert coregistration.get_offset(diff_par) == 7.0710678118654755


def test_get_stddev(tmp_path):
    log = tmp_path / 'mk_geo_radcal2_2.log'

    with open(log, 'w') as f:
        f.write('final model fit std. dev. (samples) range: 3.0000   azimuth: 4.0000')
    assert coregistration.get_std_dev(log) == 5.0

    with open(log, 'w') as f:
        f.write('final model fit std. dev. (samples) range: 50.9111   azimuth: 79.8217')
    assert coregistration.get_std_dev(log) == 94.67546616785154


def test_check_coreg(tmp_path):
    log = tmp_path / 'mk_geo_radcal2_2.log'
    with open(log, 'w') as f:
        f.write('final model fit std. dev. (samples) range: 3.0000   azimuth: 4.0000')

    diff_par = tmp_path / 'diff_par'
    with open(diff_par, 'w') as f:
        f.write('range_offset_polynomial:    -5.00000  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00\n')
        f.write('azimuth_offset_polynomial:  12.00000  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00  0.0000e+00\n')

    coregistration.check_coregistration(log, diff_par, max_stddev=5.0, max_offset=13.0, pixel_size=1.0)
    with pytest.raises(coregistration.CoregistrationError):
        coregistration.check_coregistration(log, diff_par, max_stddev=4.99, max_offset=13.0, pixel_size=1.0)
    with pytest.raises(coregistration.CoregistrationError):
        coregistration.check_coregistration(log, diff_par, max_stddev=5.0, max_offset=12.99, pixel_size=1.0)

    coregistration.check_coregistration(log, diff_par, max_stddev=5.0, max_offset=26.0, pixel_size=2.0)
    with pytest.raises(coregistration.CoregistrationError):
        coregistration.check_coregistration(log, diff_par, max_stddev=5.0, max_offset=25.99, pixel_size=2.0)
