#!/usr/bin/env python
"""
.. module:: tabel
.. moduleauthor:: Bastiaan Bergman <Bastiaan.Bergman@gmail.com>

"""
from .tabel import Tabel, read_tabel, transpose, T
from .hashjoin import first
from ._version import __version__
__all__ = ["Tabel", "first", "transpose", "T", "read_tabel", "__version__"]
name = "tabel"                                      # pylint: disable=invalid-name
