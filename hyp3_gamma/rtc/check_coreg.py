"""Checks results of Gamma RTC co-registration process"""

import logging

import numpy as np
from hyp3lib.getParameter import getParameter

log = logging.getLogger()


class CoregistrationError(Exception):
    """Error to raise when co-registration fails"""


def get_offset(point, range_coefficients, azimuth_coefficients):
    vector = np.array([1, point[0], point[1], point[0] * point[1], point[0] ** 2, point[1] ** 2])
    range_offset = sum(vector * range_coefficients)
    azimuth_offset = sum(vector * azimuth_coefficients)
    return np.sqrt(range_offset ** 2 + azimuth_offset ** 2)


def check_coregistration(mk_geo_radcal2_log, diff_par, pixel_size=30.0, max_offset=75, max_error=2.0):
    with open(mk_geo_radcal2_log) as f:
        line = [line for line in f.readlines() if line.startswith('final model fit std. dev. (samples)')][0]
    range_std_dev = float(line.split(':')[1].split()[0].strip())
    azimuth_std_dev = float(line.split(':')[2].strip())
    std_dev = np.sqrt(range_std_dev ** 2 + azimuth_std_dev ** 2)
    if std_dev > max_error:
        log.warning(f'Standard deviation of {std_dev} is larger than {max_error}')
        raise CoregistrationError()

    range_samples = int(getParameter(diff_par, 'range_samp_1'))
    azimuth_samples = int(getParameter(diff_par, 'az_samp_1'))
    corners = [
        (1, 1),
        (range_samples, 1),
        (1, azimuth_samples),
        (range_samples, azimuth_samples),
    ]

    range_coefficients = np.array([float(c) for c in getParameter(diff_par, 'range_offset_polynomial').split()])
    azimuth_coefficients = np.array([float(c) for c in getParameter(diff_par, 'azimuth_offset_polynomial').split()])
    corner_offsets = [get_offset(corner, range_coefficients, azimuth_coefficients) for corner in corners]
    absolute_offset = pixel_size * max(corner_offsets)

    if absolute_offset >= max_offset:
        log.warning(f'Absolute offset of {absolute_offset} is larger than {max_offset}')
        raise CoregistrationError()

    log.info("Granule passed co-registration")
