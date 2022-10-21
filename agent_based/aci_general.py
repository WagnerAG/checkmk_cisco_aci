#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

"""
Check_MK Checks to use with agent_cisco_aci Datasource

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""

from __future__ import annotations
from contextlib import suppress
from enum import Enum


class ConversionFactor(Enum):
    """Enum used to """
    MINUTES: int = 60
    HOURS: int = 3600


def convert_rate(value: float, factor: ConversionFactor = ConversionFactor.MINUTES) -> float:
    """convert values from x/second into other rate. Default converts into x/min."""
    return value * factor.value


def to_int(value: str) -> int:
    """return input value as int if casting is possible, otherwise return zero"""
    with suppress(ValueError):
        return int(value)
    return 0
