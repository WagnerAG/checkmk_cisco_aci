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
Check_MK agent based checks to be used with agent_cisco_aci Datasource

Authors:    Samuel Zehnder <zehnder@netcloud.ch>
            Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
from contextlib import suppress
from enum import Enum

from cmk.base.plugins.agent_based.agent_based_api.v1 import ServiceLabel


DEFAULT_DISCOVERY_PARAMS: Dict = {
    "discovery_single": (
        True,
        {
            "long_if_name": True,
            "pad_portnumbers": False,
        },
    ),
    "matching_conditions": (False, {}),
}


class ConversionFactor(Enum):
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


def get_max_if_padding(section: Dict):
    items = section.values() if isinstance(section, dict) else section
    return max((item.id_length for item in items))


def pad_interface_id(interface_id: str, pad_length: int = 3):
    """pad the last part of the interface id with zero, so it will be a three digit number"""
    return "/".join(interface_id.split("/")[:-1]) + "/" + interface_id.split("/")[-1].zfill(pad_length)


def format_interface_id(interface_id: str):
    """format the interface name"""
    return interface_id.lower().replace("eth", "Ethernet")


def get_orig_interface_id(interface_id: str):
    """pad the last part of the interface id with zero, so it will be a three digit number"""
    interface_id = interface_id.replace("Ethernet", "eth")
    suffix = interface_id.split("/")[-1].lstrip("0")
    return "/".join(interface_id.split("/")[:-1]) + "/" + (suffix if suffix else "0")  # handle case of eth0


def get_discovery_item_name(
    params: Dict,
    interface_id: str,
    pad_length: int,
) -> Tuple[Optional[str], List[ServiceLabel]]:
    """for example values for param, see tests"""
    labels = {}

    # check if we want to detect interfaces at all
    if not params["discovery_single"][0]:
        return None, []

    # check if we want to pad port numbers with zeros
    if params["discovery_single"][1]["pad_portnumbers"]:
        interface_id = pad_interface_id(interface_id, pad_length)

    # check if we want to replace interface name with a long version
    if params["discovery_single"][1]["long_if_name"]:
        interface_id = format_interface_id(interface_id)

    # get labels
    labels = params["discovery_single"][1].get("labels", {})

    return interface_id, [ServiceLabel(k, v) for k, v in labels.items()]
