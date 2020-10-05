"""General GAMMA utilities"""

import datetime
import logging
import os


def gamma_version():
    """Probe the system to find the version of GAMMA installed, if possible"""
    gamma_ver = os.getenv('GAMMA_VERSION')
    if gamma_ver is None:
        try:
            gamma_home = os.environ['GAMMA_HOME']
        except KeyError:
            logging.error('No GAMMA_VERSION or GAMMA_HOME environment variables defined! GAMMA is not installed.')
            raise

        try:
            with open(f"{gamma_home}/ASF_Gamma_version.txt") as f:
                gamma_ver = f.readlines()[-1].strip()
        except IOError:
            logging.warning(
                f"No GAMMA_VERSION environment variable or ASF_Gamma_version.txt "
                f"file found in GAMMA_HOME:\n     {os.getenv('GAMMA_HOME')}\n"
                f"Attempting to parse GAMMA version from its install directory"
            )
            gamma_ver = os.path.basename(gamma_home).split('-')[-1]
    try:
        datetime.datetime.strptime(gamma_ver, '%Y%m%d')
    except ValueError:
        logging.warning(f'GAMMA version {gamma_ver} does not conform to the expected YYYYMMDD format')

    return gamma_ver
