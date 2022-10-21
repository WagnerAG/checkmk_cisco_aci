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

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from __future__ import annotations
from dataclasses import dataclass

import time
from typing import Dict, NamedTuple, Optional, Tuple

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
from .aci_general import convert_rate


ROUND_TO_DIGITS: int = 2
DEFAULT_ERROR_LEVELS: Dict = {
    'level_fcs_errors': (0.01, 1.0),
    'level_crc_errors': (1.0, 12.0),
    'level_stomped_crc_errors': (1.0, 12.0),
}


class ErrorRates(NamedTuple):
    crc: Optional[float] = None
    fcs: Optional[float] = None
    stomped_crc: Optional[float] = None

    @staticmethod
    def _get_levels(params: Dict, state: State) -> Tuple:
        fcs_warn, fcs_crit = params.get('level_fcs_errors')
        crc_warn, crc_crit = params.get('level_crc_errors')
        stomped_crc_warn, stomped_crc_crit = params.get('level_stomped_crc_errors')

        if state == State.CRIT:
            return fcs_crit, crc_crit, stomped_crc_crit
        elif state == State.WARN:
            return fcs_warn, crc_warn, stomped_crc_warn
        else:
            raise ValueError(f'No valid state provided. Allowed are State.CRIT and State.WARN. Got state={state}')

    def _check_state(self, params, state: State) -> bool:
        fcs_level, crc_level, stomped_crc_level = self._get_levels(params, state)
        return self.fcs >= fcs_level or \
            self.crc >= crc_level or \
            self.stomped_crc >= stomped_crc_level

    def is_crit(self, params) -> bool:
        return self._check_state(params, state=State.CRIT)

    def is_warn(self, params) -> bool:
        return self._check_state(params, state=State.WARN)


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

    def get_state(self, params: Dict) -> State:
        self.calculate_error_counters()

        if self.rates.is_crit(params):
            return State.CRIT

        if self.rates.is_warn(params):
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


def check_aci_l1_phys_if(item: str, params: Dict, section: Dict[str, AciL1Interface]) -> CheckResult:
    interface: AciL1Interface = section.get(item)

    if not interface:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')
    else:
        yield Result(state=interface.get_state(params), summary=interface.summary, details=interface.details)
        yield Metric('fcs_errors', round(interface.rates.fcs, ROUND_TO_DIGITS), levels=params.get('level_fcs_errors'))
        yield Metric('crc_errors', round(interface.rates.crc, ROUND_TO_DIGITS), levels=params.get('level_crc_errors'))
        yield Metric('stomped_crc_errors', round(interface.rates.stomped_crc, ROUND_TO_DIGITS), levels=params.get('level_stomped_crc_errors'))


register.check_plugin(
    name='aci_l1_phys_if',
    service_name='L1 phys interface %s',
    discovery_function=discover_aci_l1_phys_if,
    check_function=check_aci_l1_phys_if,
    check_ruleset_name='aci_l1_phys_if_levels',
    check_default_parameters=DEFAULT_ERROR_LEVELS,
)
