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
from dataclasses import dataclass
from enum import Enum
import time
from typing import Dict, NamedTuple, Optional

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


ROUND_TO_DIGITS: int = 2


class ConversionFactor(Enum):
    MIN: int = 60


def convert_rate(value: float, factor: ConversionFactor = ConversionFactor.MIN) -> float:
    return value * factor.value


class ErrorRates(NamedTuple):
    crc: Optional[float] = None
    fcs: Optional[float] = None
    stomped_crc: Optional[float] = None


@dataclass
class AciL1Interface:
    dn: str
    id: str
    admin_state: str
    layer: str
    crc_errors: int
    fcs_errors: int
    op_state: str
    op_speed: str
    rates: Optional[ErrorRates] = None

    def calculate_error_counters(self) -> ErrorRates:
        """calculate the error rate using value_store and get_rate

        values are stored using dn, which is a unique ID per Apic
        """
        if not self.rates:
            value_store = get_value_store()
            now = time.time()

            crc_rate = convert_rate(get_rate(value_store,
                                             f'cisco_aci.{self.dn}.crc',
                                             now,
                                             self.crc_errors))

            fcs_rate = convert_rate(get_rate(value_store,
                                             f'cisco_aci.{self.dn}.fcs',
                                             now,
                                             self.fcs_errors))

            stomped_crc_rate = crc_rate - fcs_rate

            self.rates = ErrorRates(crc=crc_rate, fcs=fcs_rate, stomped_crc=stomped_crc_rate)

            return self.rates

        return self.rates

    @staticmethod
    def from_string_table(line) -> AciL1Interface:
        line[4] = int(line[4]) if line[4] is not None else 0
        line[5] = int(line[5]) if line[5] is not None else 0

        return AciL1Interface(*line)

    @property
    def state(self) -> State:
        self.calculate_error_counters()

        if self.rates.fcs > 0 or self.rates.stomped_crc > 12:
            return State.CRIT

        if self.rates.stomped_crc > 0:
            return State.WARN

        if self.admin_state == 'up' and self.op_state == 'down':
            return State.WARN

        return State.OK

    @property
    def stomped_crc(self):
        return self.crc_errors - self.fcs_errors

    @property
    def layer_short(self) -> str:
        return self.layer.lower().replace('layer', '')

    @property
    def summary(self):
        self.calculate_error_counters()

        return (
            f'state: {self.admin_state}/{self.op_state} (admin/op) '
            f'layer: {self.layer_short} '
            f'op_speed: {self.op_speed} | '
            f'errors: FCS={round(self.rates.fcs, ROUND_TO_DIGITS)}/min ({self.fcs_errors} total) '
            f'CRC={round(self.rates.crc, ROUND_TO_DIGITS)}/min ({self.crc_errors} total) '
            f'stomped_CRC={round(self.rates.stomped_crc, ROUND_TO_DIGITS)}/min ({self.stomped_crc} total)'
        )

    @property
    def details(self):
        self.calculate_error_counters()

        return (
            f'Admin state: {self.admin_state} \n'
            f'Operational state: {self.op_state} \n'
            f'Layer: {self.layer} \n'
            f'Operational speed: {self.op_speed} \n\n'
            f'FCS errors: {round(self.rates.fcs, ROUND_TO_DIGITS)}/min ({self.fcs_errors} errors in total) \n'
            f'CRC errors: {round(self.rates.crc, ROUND_TO_DIGITS)}/min ({self.crc_errors} errors in total) \n'
            f'Stomped CRC errors: {round(self.rates.stomped_crc, ROUND_TO_DIGITS)}/min ({self.stomped_crc} errors in total)'
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
        yield Result(state=interface.state, summary=interface.summary, details=interface.details)
        yield Metric('fcs_errors', round(interface.rates.fcs, ROUND_TO_DIGITS), levels=(0.001, 0.001))
        yield Metric('crc_errors', round(interface.rates.crc, ROUND_TO_DIGITS))
        yield Metric('stomped_crc_errors', round(interface.rates.stomped_crc, ROUND_TO_DIGITS), levels=(0.001, 100))


register.check_plugin(
    name='aci_l1_phys_if',
    service_name='L1 phys interface %s',
    discovery_function=discover_aci_l1_phys_if,
    check_function=check_aci_l1_phys_if,
)
