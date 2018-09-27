#!/usr/bin/env python
"""
.. module:: tabel
.. moduleauthor:: Bastiaan Bergman <Bastiaan.Bergman@gmail.com>

"""
from .tabel import Tabel, read_tabel, transpose, T
from .hashjoin import first
__all__ = ["Tabel", "first", "transpose", "T", "read_tabel"]
name = "tabel"                                      # pylint: disable=invalid-name
