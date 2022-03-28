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
Place into local check-mk checks directory, e.g ~/local/share/check_mk/checks in OMD

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""

from __future__ import annotations
from typing import List, NamedTuple

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
)

HEALTHY_CONTROLLER_STATUS: str = "in-service"


class ACIController(NamedTuple):
    controller_id: str  # keep the ID a str to avoid unnecessary casting
    name: str
    status: str
    serial: str
    model: str
    descr: str


def parse_aci_controller(string_table) -> List[ACIController]:
    """
    Exmple output:
        controller 1 APIC1 in-service  FCH1835V2FM APIC-SERVER-M1 APIC-SERVER-M1

        controller 1 ACI01 in-service  FCH1935V1Z8 APIC-SERVER-M2 APIC-SERVER-M2
    """
    return [
        ACIController(controller_id, name, status, serial, model, descr)
        for _, controller_id, name, status, serial, model, descr
        in string_table
    ]


register.agent_section(
    name='aci_controller',
    parse_function=parse_aci_controller,
)


def discover_aci_controller(section: List[ACIController]) -> DiscoveryResult:
    for controller in section:
        yield Service(item=controller.controller_id)


def check_aci_controller(item: str, section: List[ACIController]) -> CheckResult:
    for ctrl in section:
        if item == ctrl.controller_id:
            yield Result(
                state=State.OK if ctrl.status == HEALTHY_CONTROLLER_STATUS else State.CRIT,
                summary=f'{ctrl.name} is {ctrl.status}, Model: {ctrl.model}, Serial: {ctrl.serial}'
            )
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')


register.check_plugin(
    name='aci_controller',
    service_name='APIC %s',
    discovery_function=discover_aci_controller,
    check_function=check_aci_controller,
)
