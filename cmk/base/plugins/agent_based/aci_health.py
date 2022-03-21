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
Check_MK Checks to use with aci-ds Datasource
Place into local check-mk checks directory, e.g ~/local/share/check_mk/checks in OMD

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""

from __future__ import annotations
from typing import NamedTuple

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Metric,
    Result,
    Service,
    State,
)
from .aci_general import ACIHealthLevels, get_state_by_health_score


class ACIHealthValues(NamedTuple):
    health: int
    fcrit: int
    fwarn: int
    fmaj: int
    fmin: int

    @staticmethod
    def from_string_table_line(line) -> ACIHealthValues:
        line = list(map(int, line[1:]))  # cast all values to int
        health, fcrit, fwarn, fmaj, fmin = line

        return ACIHealthValues(
            health, fcrit, fwarn, fmaj, fmin
        )


def parse_aci_health(string_table) -> ACIHealthValues:
    """
    Example output:
        health 99 3 28 34 95
    """
    if len(string_table) != 1:
        raise ValueError(f'section must <<<aci_health>>> be a single line but is {len(string_table)} lines')

    return ACIHealthValues.from_string_table_line(string_table[0])


register.agent_section(
    name='aci_health',
    parse_function=parse_aci_health,
)


def discover_aci_health(section: ACIHealthValues) -> DiscoveryResult:
    yield Service()


def check_aci_health(section: ACIHealthValues) -> CheckResult:
    yield Result(
        state=get_state_by_health_score(section.health),
        summary=f"Fabric Health Score: {section.health}, "
                f"Fabric-wide Faults (crit/warn/maj/min): "
                f"{section.fcrit}/{section.fwarn}/{section.fmaj}/{section.fmin}")

    yield Metric("health", section.health,
                 levels=(ACIHealthLevels.WARN.value, ACIHealthLevels.CRIT.value),
                 boundaries=(0, 100))
    yield Metric("fcrit", section.fcrit)
    yield Metric("fwarn", section.fwarn)
    yield Metric("fmaj", section.fmaj)
    yield Metric("fmin", section.fmin)


register.check_plugin(
    name='aci_health',
    service_name='Fabric Health Score',
    discovery_function=discover_aci_health,
    check_function=check_aci_health,
)
