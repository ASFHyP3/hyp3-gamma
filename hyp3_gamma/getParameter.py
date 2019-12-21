#!/usr/bin/python

import re, os
import logging
#
# Read a value from a par file
#
def getParameter(parFile,parameter,uselogging=False):

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

