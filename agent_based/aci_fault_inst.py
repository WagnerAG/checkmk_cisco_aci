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

Authors:    Fabian Binder <fabian.binder@comnetgmbh.com>

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


class ACIFaultInst(NamedTuple):
    severity: str
    code: str
    descr: str
    dn: str
    ack: str

    @staticmethod
    def from_string_table(line) -> ACIFaultInst:
        severity, code, descr, dn, ack = line

        return ACIFaultInst(
            severity, code, descr, dn, ack
        )


def parse_aci_fault_inst(string_table) -> ACIFaultInst:
    """
    Example output:
    major   F609802 [FSM:FAILED]: Task for updating Number of Uplinks on DVS/AVE for VMM controller: hostname with name xyz in datacenter DC01 in domain: DC01-GENERIC(TASK:ifc:vmmmgr:CompPolContUpdateCtrlrNoOfUplinksPol)      comp/prov-VMware/ctrlr-[DC01-GENERIC]-dc01/polCont/fault-F609802 no
    """
    return [
        ACIFaultInst.from_string_table(line) for line in string_table
        if not line[0].startswith('#') and not line[0] == 'severity'
    ]


register.agent_section(
    name='aci_fault_inst',
    parse_function=parse_aci_fault_inst,
)


def discover_aci_fault_inst(section: ACIFaultInst) -> DiscoveryResult:
    yield Service()


def check_aci_fault_inst(section: ACIFaultInst) -> CheckResult:
    minor = 0
    major = 0
    cleared = 0

    for fault in section:
        if fault.severity == "critical" and fault.ack == "no":
            yield Result(state=State.CRIT, summary="Critical unacknowledged error: %s" % fault.descr)
        else:
            if fault.severity == "major":
                major += 1
            elif fault.severity == "minor":
                minor += 1
            elif fault.severity == "cleared":
                cleared += 1
    yield Result(state=State.OK, summary= "%s major alarms, %s minor alarms, %s cleared alarms" % (major, minor, cleared))


register.check_plugin(
    name='aci_fault_inst',
    service_name='Fabric Faults',
    discovery_function=discover_aci_fault_inst,
    check_function=check_aci_fault_inst,
)
