from __future__ import print_function, absolute_import, division, unicode_literals

import logging
import os
import re


def getParameter(parFile,parameter,uselogging=False):
    """Read a value from a par file"""

    if os.path.isfile(parFile):
        myfile = open(parFile,"r")
    else: 
        if (uselogging):
            logging.error("ERROR: Unable to find file {}".format(parFile))
        else:
            print("ERROR: Unable to file file {}".format(parFile))
        exit(1)

    value = None
    parameter = parameter.lower()
    for line in myfile:
        if parameter in line.lower():
            t = re.split(":",line)
            value = t[1].strip()
    myfile.close()

    if value is None:
        if uselogging:
            logging.error("ERROR: Unable to find parameter {} in file {}".format(parameter,parFile))
        else:
            print("ERROR: Unable to find parameter {} in file {}".format(parameter, parFile))
        exit(1)
    return value

