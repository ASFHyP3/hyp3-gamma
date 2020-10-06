"""Checks results of Gamma RTC coregistration process"""

import glob
import logging
import os
import re

import numpy as np

from hyp3_gamma.getParameter import getParameter


class CoregistrationError(Exception):
    """Error to raise when coregistration fails"""


class CoregLogger:
    """A local logging context to create a coregistration log file"""
    def __init__(self, logger=None, file_name='coreg_check.log', file_mode='w'):
        """
        Args:
            logger: The logger to use for logging (defaults to root logger)
            file_name: file to write coregistation log to
            file_mode: mode to open the coregistration log file in
        """
        self.logger = logger
        self.file_handler = logging.FileHandler(file_name, mode=file_mode)

    def __enter__(self):
        if self.logger is None:
            self.logger = logging.getLogger()
        self.logger.addHandler(self.file_handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()


def calc(s, l, r, a):  # noqa: E741
    rpt = r[0] + r[1] * s + r[2] * l + r[3] * s * l + r[4] * s * s + r[5] * l * l
    apt = a[0] + a[1] * s + a[2] * l + a[3] * s * l + a[4] * s * s + a[5] * l * l
    return rpt, apt


def check_coreg(sar_file, post, max_offset=50, max_error=2):
    with CoregLogger():
        logging.info(f"SAR file: {sar_file}")
        logging.info(f"Checking coregistration using {post} meters")
        logging.info(f"Setting maximum offset to be {max_offset}")
        logging.info(f"Setting maximum error to be {max_error}")

        myfile = "mk_geo_radcal_2.log"
        if os.path.isdir("geo_HH"):
            mlog = "geo_HH/{}".format(myfile)
        elif os.path.isdir("geo_hh"):
            mlog = "geo_hh/{}".format(myfile)
        elif os.path.isdir("geo_VV"):
            mlog = "geo_VV/{}".format(myfile)
        elif os.path.isdir("geo_vv"):
            mlog = "geo_vv/{}".format(myfile)
        elif os.path.isdir("geo"):
            mlog = "geo/{}".format(myfile)
        else:
            raise CoregistrationError(f"Can't find {myfile}")

        a = np.zeros(6)
        r = np.zeros(6)

        with open(mlog, "r") as g:
            for line in g:
                if 'final range offset poly. coeff.:' in line:
                    tmp = re.split(":", line)
                    vals = tmp[1].split()
                    if len(vals) == 1:
                        r[0] = float(vals[0])
                        logging.info(f"Range offset is {r}")
                    elif len(vals) == 3:
                        r[0] = float(vals[0])
                        r[1] = float(vals[1])
                        r[2] = float(vals[2])
                        logging.info(f"Range polynomial is {r}")
                    elif len(vals) == 6:
                        r[0] = float(vals[0])
                        r[1] = float(vals[1])
                        r[2] = float(vals[2])
                        r[3] = float(vals[3])
                        r[4] = float(vals[4])
                        r[5] = float(vals[5])
                        logging.info(f"Range polynomial is {r}")

                if 'final azimuth offset poly. coeff.:' in line:
                    tmp = re.split(":", line)
                    vals = tmp[1].split()
                    if len(vals) == 1:
                        a[0] = float(vals[0])
                        logging.info(f"Azimuth offset is {a}")
                    elif len(vals) == 3:
                        a[0] = float(vals[0])
                        a[1] = float(vals[1])
                        a[2] = float(vals[2])
                        logging.info(f"Azimuth polynomial is {a}")
                    elif len(vals) == 6:
                        a[0] = float(vals[0])
                        a[1] = float(vals[1])
                        a[2] = float(vals[2])
                        a[3] = float(vals[3])
                        a[4] = float(vals[4])
                        a[5] = float(vals[5])
                        logging.info(f"Azimuth polynomial is {a}")

                if 'final model fit std. dev. (samples) range:' in line:
                    tmp = re.split(":", line)
                    vals = tmp[1].split()
                    rng_error = float(vals[0])
                    val = tmp[2].strip()
                    azi_error = float(val)
                    logging.info(f"Range std dev: {rng_error}  Azimuth std dev: {azi_error}")
                    error = np.sqrt(rng_error * rng_error + azi_error * azi_error)
                    logging.info(f"error is {error}")
                    if error > max_error:
                        logging.warning("error > max_error")
                        logging.warning("std dev is too high, using dead reckoning")
                        logging.warning("Granule failed coregistration")
                        raise CoregistrationError('error > max_error')

        mlog = glob.glob('geo_??/*.diff_par')[0]
        if not mlog:
            mlog = glob.glob('geo/*.diff_par')[0]
            if not mlog:
                raise CoregistrationError("Can't find diff_par file")

        if os.path.exists(mlog):
            ns = int(getParameter(mlog, "range_samp_1"))
            logging.info(f"Number of samples is {ns}")
            nl = int(getParameter(mlog, "az_samp_1"))
            logging.info(f"Number of lines is {nl}")
        else:
            raise CoregistrationError(f"Can't find diff par file {mlog}")

        rpt, apt = calc(1, 1, r, a)
        pt1 = np.sqrt(rpt * rpt + apt * apt)
        logging.info(f"Point 1 offset is {pt1} = sqrt({rpt}**2 + {apt}**2)")

        rpt, apt = calc(ns, 1, r, a)
        pt2 = np.sqrt(rpt * rpt + apt * apt)
        logging.info(f"Point 2 offset is {pt2} = sqrt({rpt}**2 + {apt}**2)")

        rpt, apt = calc(1, nl, r, a)
        pt3 = np.sqrt(rpt * rpt + apt * apt)
        logging.info(f"Point 3 offset is {pt3} = sqrt({rpt}**2 + {apt}**2)")

        rpt, apt = calc(ns, nl, r, a)
        pt4 = np.sqrt(rpt * rpt + apt * apt)
        logging.info(f"Point 4 offset is {pt4} = sqrt({rpt}**2 + {apt}**2)")

        top = max(pt1, pt2, pt3, pt4)
        offset = top * post

        logging.info(f"Found absolute offset of {offset} meters")
        if offset >= max_offset:
            raise CoregistrationError("offset too large, using dead reckoning")

        logging.info("Granule passed coregistration")
