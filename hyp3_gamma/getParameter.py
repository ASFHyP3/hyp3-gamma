from __future__ import print_function, absolute_import, division, unicode_literals

import logging
import re


def getParameter(parFile, parameter, uselogging=False):
    """Read a value from a par file"""
    value = None
    try:
        with open(parFile, "r") as myfile:
            parameter = parameter.lower()
            for line in myfile:
                if parameter in line.lower():
                    t = re.split(":", line)
                    value = t[1].strip()
    except IOError:
        if uselogging:
            logging.error("Unable to find file {}".format(parFile))
        raise Exception("ERROR: Unable to find file {}".format(parFile))

    if value is None:
        if uselogging:
            logging.error("Unable to find parameter {} in file {}".format(parameter, parFile))
        raise Exception("ERROR: Unable to find parameter {} in file {}".format(parameter, parFile))

    return value
