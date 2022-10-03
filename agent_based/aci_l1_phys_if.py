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
Version:    0.7

"""

from __future__ import annotations
import time
from typing import Dict, NamedTuple, Tuple

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    Metric,
    get_rate,
    get_value_store,
)


class AciL1Interface(NamedTuple):
    dn: str
    id: str
    admin_state: str
    layer: str
    crc_errors: int
    fcs_errors: int
    op_state: str
    op_speed: str

    def calculate_error_counters(self) -> Tuple:
        """calculate the error rate using value_store and get_rate

        values are stored using dn, which is a unique ID per Apic
        """
        value_store = get_value_store()
        now = time.time()

        crc_rate = get_rate(value_store,
                            f'cisco_aci.{self.dn}.crc',
                            now,
                            self.crc_errors)

        fcs_rate = get_rate(value_store,
                            f'cisco_aci.{self.dn}.fcs',
                            now,
                            self.fcs_errors)

        stomped_crc_rate = crc_rate - fcs_rate

        return crc_rate, fcs_rate, stomped_crc_rate

    @staticmethod
    def from_string_table(line) -> AciL1Interface:
        line[4] = int(line[4]) if line[4] is not None else 0
        line[5] = int(line[5]) if line[5] is not None else 0

        return AciL1Interface(*line)

    @property
    def state(self) -> State:
        if self.admin_state == 'up' and self.op_state == 'down':
            return State.WARN

        return State.OK

    def get_summary(self, fcs, crc, stomped_crc):
        return (
            f'admin_state={self.admin_state} '
            f'op_state={self.op_state} '
            f'layer={self.layer} '
            f'op_speed={self.op_speed} | '
            f'errors: FCS={fcs} '
            f'CRC={crc} '
            f'stomped_CRC={stomped_crc}'
        )


def parse_aci_l1_phys_if(string_table) -> Dict[str, AciL1Interface]:
    return {line[1]: AciL1Interface.from_string_table(line) for line in string_table
            if not line[0].startswith('#')}


register.agent_section(
    name='aci_l1_phys_if',
    parse_function=parse_aci_l1_phys_if,
)


def discover_aci_l1_phys_if(section: Dict[str, AciL1Interface]) -> DiscoveryResult:
    for interface_id in section.keys():
        yield Service(item=interface_id)


def check_aci_l1_phys_if(item: str, section: Dict[str, AciL1Interface]) -> CheckResult:
    interface: AciL1Interface = section.get(item)

    if not interface:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')
    else:
        crc_rate, fcs_rate, stomped_crc_rate = interface.calculate_error_counters()

        yield Result(state=interface.state, summary=interface.get_summary(crc_rate, fcs_rate, stomped_crc_rate))
        yield Metric('fcs_errors', fcs_rate, levels=(0.001, 0.001))
        yield Metric('crc_errors', crc_rate)
        yield Metric('stomped_crc_errors', stomped_crc_rate, levels=(0.001, 100))


register.check_plugin(
    name='aci_l1_phys_if',
    service_name='L1 phys interface %s',
    discovery_function=discover_aci_l1_phys_if,
    check_function=check_aci_l1_phys_if,
)
