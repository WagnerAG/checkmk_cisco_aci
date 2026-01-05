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

from typing import List, NamedTuple

from cmk.agent_based.v2 import AgentSection, CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State

HEALTHY_CONTROLLER_STATUS: str = "in-service"


class ACIController(NamedTuple):
    controller_id: str  # keep the ID a str to avoid unnecessary casting
    name: str
    status: str
    serial: str
    model: str
    fault_crit: str
    fault_maj: str
    fault_minor: str
    fault_warn: str
    descr: str


def parse_aci_controller(string_table) -> List[ACIController]:
    """
    Exmple output:
        controller 1 APIC1 in-service FCH1835V2FM APIC-SERVER-M4 0 -1 0 0 APIC-SERVER-M4

        controller 1 ACI01 in-service FCH1935V1Z8 APIC-SERVER-M4 0 -1 0 0APIC-SERVER-M4
    """
    return [ACIController(controller_id, name, status, serial, model, fault_crit, fault_maj, fault_minor, fault_warn, descr) for _, controller_id, name, status, serial, model, fault_crit, fault_maj, fault_minor, fault_warn, descr in string_table]


def discover_aci_controller(section: List[ACIController]) -> DiscoveryResult:
    for controller in section:
        yield Service(item=controller.controller_id)


def check_aci_controller(item: str, section: List[ACIController]) -> CheckResult:
    for ctrl in section:
        if item == ctrl.controller_id:
            fault_crit = int(ctrl.fault_crit)
            fault_maj = int(ctrl.fault_maj)
            fault_minor = int(ctrl.fault_minor)
            fault_warn = int(ctrl.fault_warn)

            details = f"""
                    Unacknowledged APIC Faults:
                    - Crit: {fault_crit}
                    - Maj: {fault_maj}
                    - Minor: {fault_minor}
                    - Warning: {fault_warn}
                """

            if fault_crit > 0 or fault_maj > 0 or ctrl.status != HEALTHY_CONTROLLER_STATUS:
                faults = fault_maj + fault_crit
                yield Result(
                    state=State.CRIT,
                    summary=f"{ctrl.name} is {ctrl.status}, Unacknowledged Faults: {faults}, Model: {ctrl.model}, Serial: {ctrl.serial}",
                    details=details,
                )
                break
            elif fault_minor > 0 or fault_warn > 0:
                faults = str(fault_minor + fault_warn)
                yield Result(
                    state=State.WARN,
                    summary=f"{ctrl.name} is {ctrl.status}, Unacknowledged Faults: {faults}, Model: {ctrl.model}, Serial: {ctrl.serial}",
                    details=details,
                )
                break
            elif fault_crit < 0 or fault_maj < 0 or fault_minor < 0 or fault_warn < 0:
                yield Result(
                    state=State.WARN,
                    summary=f"{ctrl.name} is {ctrl.status}, Unacknowledged Faults: got negative number, Model: {ctrl.model}, Serial: {ctrl.serial}",
                    details=f'{details}\nThe difference between “faults - faultsAcknowledged” results in a negative number for one of the error categories crit/maj/minor/warn.\nThis means that there are probably "stale faults" on the APIC, which are output via the API but are not visible in the GUI.\nPlease investigate and correct the errors.',
                )
                break
            else:
                faults = fault_maj + fault_crit + fault_minor + fault_warn
                yield Result(
                    state=State.OK,
                    summary=f"{ctrl.name} is {ctrl.status}, Unacknowledged Faults: {faults}, Model: {ctrl.model}, Serial: {ctrl.serial}",
                )
            break
    else:
        yield Result(state=State.UNKNOWN, summary="Sorry - item not found")


agent_section_cisco_aci_controller = AgentSection(
    name="aci_controller",
    parse_function=parse_aci_controller,
)

check_plugin_cisco_aci_controller = CheckPlugin(
    name="aci_controller",
    service_name="APIC %s",
    discovery_function=discover_aci_controller,
    check_function=check_aci_controller,
)
