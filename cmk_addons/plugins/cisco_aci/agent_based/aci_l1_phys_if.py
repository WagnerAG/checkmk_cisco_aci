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
from typing import Dict, NamedTuple, Optional, Tuple, Sequence, List
from pydantic import BaseModel, Field

from cmk.agent_based.v2 import (
    Result,
    Service,
    CheckResult,
    DiscoveryResult,
    AgentSection,
    CheckPlugin,
    ServiceLabel,
    State,
    Metric,
    get_rate,
    get_value_store,
)
from .aci_general import (
    convert_rate,
    get_discovery_item_name,
    get_orig_interface_id,
    get_max_if_padding,
    DEFAULT_DISCOVERY_PARAMS,
    ErrorLevels,
)


class L1ErrorLevels(BaseModel):
    fcs_errors: ErrorLevels = Field(alias='level_fcs_errors')
    crc_errors: ErrorLevels = Field(alias='level_crc_errors')
    stomped_crc_errors: ErrorLevels = Field(alias='level_stomped_crc_errors')


ROUND_TO_DIGITS: int = 2

DEFAULT_ERROR_LEVELS: Dict = {
    "level_fcs_errors": {'warn': 0.01, 'crit': 1.0},
    "level_crc_errors": {'warn': 1.0, 'crit': 12.0},
    "level_stomped_crc_errors": {'warn': 1.0, 'crit': 12.0},
}

OPERATIONAL_PORT_STATE = {
    "unknown": "0",
    "down": "1",
    "up": "2",
    "link-up": "3",
    "channel-admin-down": "4",
}

ADMIN_PORT_STATE = {
    "up": "1",
    "down": "2",
}


class ErrorRates(NamedTuple):
    crc: Optional[float] = None
    fcs: Optional[float] = None
    stomped_crc: Optional[float] = None

    @staticmethod
    def _get_levels(params: L1ErrorLevels, state: State) -> Tuple:
        if state == State.CRIT:
            return params.fcs_errors.crit, params.crc_errors.crit, params.stomped_crc_errors.crit
        elif state == State.WARN:
            return params.fcs_errors.warn, params.crc_errors.warn, params.stomped_crc_errors.warn
        else:
            raise ValueError(f"No valid state provided. Allowed are State.CRIT and State.WARN. Got state={state}")

    def _check_state(self, params: L1ErrorLevels, state: State) -> bool:
        fcs_level, crc_level, stomped_crc_level = self._get_levels(params, state)
        return self.fcs >= fcs_level or self.crc >= crc_level or self.stomped_crc >= stomped_crc_level

    def is_crit(self, params: L1ErrorLevels) -> bool:
        return self._check_state(params, state=State.CRIT)

    def is_warn(self, params: L1ErrorLevels) -> bool:
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

            crc_rate = convert_rate(get_rate(value_store, f"cisco_aci.{self.dn}.crc", now, self.crc_errors))

            fcs_rate = convert_rate(get_rate(value_store, f"cisco_aci.{self.dn}.fcs", now, self.fcs_errors))

            stomped_crc_rate = crc_rate - fcs_rate

            self.rates = ErrorRates(crc=crc_rate, fcs=fcs_rate, stomped_crc=stomped_crc_rate)

            return self.rates

        return self.rates

    @staticmethod
    def from_string_table(line: Sequence[str]) -> AciL1Interface:
        line[4] = int(line[4]) if line[4].isdigit() else 0
        line[5] = int(line[5]) if line[5].isdigit() else 0

        return AciL1Interface(*line)

    def get_state(self, params: ErrorRates) -> State:
        self.calculate_error_counters()

        if self.rates.is_crit(params):
            return State.CRIT

        if self.rates.is_warn(params):
            return State.WARN

        if self.admin_state == "up" and self.op_state == "down":
            return State.WARN

        return State.OK

    @property
    def stomped_crc(self):
        return self.crc_errors - self.fcs_errors

    @property
    def layer_short(self) -> str:
        return self.layer.lower().replace("layer", "")

    @property
    def summary(self):
        self.calculate_error_counters()

        return f"state: {self.admin_state}/{self.op_state} (admin/op) " f"layer: {self.layer_short} " f"op_speed: {self.op_speed} | " f"errors: FCS={round(self.rates.fcs, ROUND_TO_DIGITS)}/min ({self.fcs_errors} total) " f"CRC={round(self.rates.crc, ROUND_TO_DIGITS)}/min ({self.crc_errors} total) " f"stomped_CRC={round(self.rates.stomped_crc, ROUND_TO_DIGITS)}/min ({self.stomped_crc} total)"

    @property
    def details(self):
        self.calculate_error_counters()

        return f"Admin state: {self.admin_state} \n" f"Operational state: {self.op_state} \n" f"Layer: {self.layer} \n" f"Operational speed: {self.op_speed} \n\n" f"FCS errors: {round(self.rates.fcs, ROUND_TO_DIGITS)}/min ({self.fcs_errors} errors in total) \n" f"CRC errors: {round(self.rates.crc, ROUND_TO_DIGITS)}/min ({self.crc_errors} errors in total) \n" f"Stomped CRC errors: {round(self.rates.stomped_crc, ROUND_TO_DIGITS)}/min ({self.stomped_crc} errors in total)"

    @property
    def port_admin_state(self) -> int:
        """return port admin state as int"""
        return ADMIN_PORT_STATE.get(self.admin_state)

    @property
    def port_oper_state(self) -> int:
        """return port oper state as int"""
        return OPERATIONAL_PORT_STATE.get(self.op_state)

    @property
    def id_length(self):
        return len(self.id.split("/")[-1].lower().replace("eth", ""))


def parse_aci_l1_phys_if(string_table) -> Dict[str, AciL1Interface]:
    return {line[1]: AciL1Interface.from_string_table(line) for line in string_table if not line[0].startswith("#")}


def _check_port_state(port_matching_condition: Dict, interface: AciL1Interface) -> bool:
    admin_states = port_matching_condition.get("port_admin_states", [*ADMIN_PORT_STATE.values()])
    oper_states = port_matching_condition.get("port_oper_states", [*OPERATIONAL_PORT_STATE.values()])

    return (interface.port_admin_state in admin_states) and (interface.port_oper_state in oper_states)


def _check_interface_discovery(
    params: Dict,
    interface_id: str,
    interface: AciL1Interface,
    pad_length: int,
) -> Tuple[Optional[str], List[ServiceLabel]]:
    """for example values for param, see tests"""
    interface_id, labels = get_discovery_item_name(params, interface_id, pad_length)

    # check if we detect ports only on certain condition
    # value is False if we shall apply a filtering
    if not params["matching_conditions"][0]:
        port_matching_condition = params["matching_conditions"][1]
        if not _check_port_state(port_matching_condition, interface):
            # and return None if it does not match
            return None, []

    return interface_id, labels


def discover_aci_l1_phys_if(params, section: Dict[str, AciL1Interface]) -> DiscoveryResult:
    for interface_id in section.keys():
        interface_id, labels = _check_interface_discovery(
            params,
            interface_id,
            section.get(interface_id),
            pad_length=get_max_if_padding(section),
        )
        if interface_id:
            yield Service(item=interface_id, labels=labels)


def check_aci_l1_phys_if(item: str, params: Dict, section: Dict[str, AciL1Interface]) -> CheckResult:
    levels = L1ErrorLevels.model_validate(params)
    interface: AciL1Interface = section.get(get_orig_interface_id(item))

    if not interface:
        yield Result(state=State.UNKNOWN, summary="Sorry - item not found")
    else:
        yield Result(state=interface.get_state(levels), summary=interface.summary, details=interface.details)
        yield Metric("fcs_errors", round(interface.rates.fcs, ROUND_TO_DIGITS), levels=levels.fcs_errors.values())
        yield Metric("crc_errors", round(interface.rates.crc, ROUND_TO_DIGITS), levels=levels.crc_errors.values())
        yield Metric("stomped_crc_errors", round(interface.rates.stomped_crc, ROUND_TO_DIGITS), levels=levels.stomped_crc_errors.values())


agent_section_aci_l1_phys_if = AgentSection(
    name="aci_l1_phys_if",
    parse_function=parse_aci_l1_phys_if,
)


check_plugin_aci_l1_phys_if = CheckPlugin(
    name="aci_l1_phys_if",
    service_name="Interface %s L1 phys",
    discovery_function=discover_aci_l1_phys_if,
    check_function=check_aci_l1_phys_if,
    discovery_ruleset_name="cisco_aci_if_discovery",
    discovery_default_parameters=DEFAULT_DISCOVERY_PARAMS,
    check_ruleset_name="aci_l1_phys_if_levels",
    check_default_parameters=DEFAULT_ERROR_LEVELS,
)
