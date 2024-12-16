"""Checks results of GAMMA RTC co-registration process"""

import logging
from math import sqrt

from hyp3lib.getParameter import getParameter

log = logging.getLogger()


class CoregistrationError(Exception):
    """Error to raise when co-registration fails"""


def get_std_dev(mk_geo_radcal2_log):
    with open(mk_geo_radcal2_log) as f:
        line = [line for line in f.readlines() if line.startswith('final model fit std. dev. (samples)')][0]
    range_std_dev = float(line.split(':')[1].split()[0].strip())
    azimuth_std_dev = float(line.split(':')[2].strip())
    std_dev = sqrt(range_std_dev**2 + azimuth_std_dev**2)
    return std_dev


def get_offset(diff_par):
    # assumes one term offset polynomial; see docs for GAMMA DIFF offset_fitm command
    range_offset = float(getParameter(diff_par, 'range_offset_polynomial').split()[0])
    azimuth_offset = float(getParameter(diff_par, 'azimuth_offset_polynomial').split()[0])
    offset = sqrt(range_offset**2 + azimuth_offset**2)
    return offset


def check_coregistration(mk_geo_radcal2_log, diff_par, max_stddev=2.0, max_offset=75, pixel_size=30.0):
    offset = pixel_size * get_offset(diff_par)
    if offset > max_offset:
        log.warning(f'Absolute offset of {offset} is larger than {max_offset}')
        raise CoregistrationError()

    std_dev = get_std_dev(mk_geo_radcal2_log)
    if std_dev > max_stddev:
        log.warning(f'Standard deviation of {std_dev} is larger than {max_stddev}')
        raise CoregistrationError()

    log.info('Granule passed co-registration')
