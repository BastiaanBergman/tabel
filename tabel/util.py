#!/usr/bin/env python
"""
.. module:: tabel.util
.. moduleauthor:: Bastiaan Bergman <Bastiaan.Bergman@gmail.com>

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys


if sys.version_info >= (3, 0):
    PV = 3
    ImpError = ModuleNotFoundError                      # pylint: disable=invalid-name
elif sys.version_info >= (2, 0):
    PV = 2
    ImpError = ImportError
else:
    print("Forget about it!")
    sys.exit(1)

def isstring(strng):
    """ Python version independent string checking """
    if PV == 2:
        return isinstance(strng, basestring)            # pylint: disable=undefined-variable
    if PV == 3:
        return isinstance(strng, str)
    raise NotImplementedError("Unknown python verison: {}".format(PV))
