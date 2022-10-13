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
from typing import NamedTuple, List

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from .aci_general import ACIHealthLevels, get_state_by_health_score


class ACINode(NamedTuple):
    nnid: str  # nnid as string to avoid casting
    name: str
    status: str
    health: int
    serial: str
    model: str

    @staticmethod
    def from_string_table(line) -> ACINode:
        _, nnid, name, status, health, serial, model = line[:7]
        return ACINode(nnid, name, status, int(health), serial, model)


def parse_aci_node(string_table) -> List[ACINode]:
    """
    Example output:
        <<<aci_spine>>>
        spine 201 zh1wagsp201 in-service 95 FDO21101P2A N9K-C9336PQ Nexus9000 1-Slot Spine Chassis
        spine 202 zh1wagsp202 in-service 95 FDO21101P49 N9K-C9336PQ Nexus9000 1-Slot Spine Chassis
        <<<aci_leaf>>>
        leaf 114 be1wagle114 in-service 100 FDO210810PS N9K-C93180YC-EX Nexus C93180YC-EX Chassis
        leaf 112 be1wagle112 in-service 100 FDO210810QD N9K-C93180YC-EX Nexus C93180YC-EX Chassis
    """
    return [ACINode.from_string_table(line) for line in string_table]


def discover_aci_node(section: List[ACINode]) -> DiscoveryResult:
    for node in section:
        yield Service(item=node.nnid)


def check_aci_node(item: str, section: List[ACINode]) -> CheckResult:
    for node in section:
        if node.nnid == item:
            yield Result(
                state=get_state_by_health_score(node.health),
                summary=f"{node.name} is {node.status}, Health:{node.health}, "
                        f"Model: {node.model}, Serial {node.serial}"
            )
            yield Metric("health", node.health,
                         levels=(ACIHealthLevels.WARN.value, ACIHealthLevels.CRIT.value),
                         boundaries=(0, 100))
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')
