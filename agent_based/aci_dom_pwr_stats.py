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
from enum import Enum, unique
from typing import List, NamedTuple, Sequence, Tuple, Dict, Optional
import re

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    check_levels,
    Result,
    Service,
    ServiceLabel,
    State,
)
from .aci_general import (
    get_max_if_padding,
    get_discovery_item_name,
    get_orig_interface_id,
    DEFAULT_DISCOVERY_PARAMS,
)


@unique
class PowerStatType(Enum):
    RX: str = 'rx'
    TX: str = 'tx'


class DomPowerStatValues(NamedTuple):
    type: PowerStatType
    alert: str
    status: str
    hi_alarm: float
    hi_warn: float
    lo_alarm: float
    lo_warn: float
    value: float

    def from_string_table(stats_type: PowerStatType, line: Sequence) -> DomPowerStatValues:
        return DomPowerStatValues(
            type=stats_type,
            alert=line[0],
            status=line[1],
            hi_alarm=float(line[2]),
            hi_warn=float(line[3]),
            lo_alarm=float(line[4]),
            lo_warn=float(line[5]),
            value=float(line[6]),
        )

    @property
    def summary(self) -> str:
        return f'{self.type.name} alert: {self.alert}, {self.type.name} status: {self.status}'

    @property
    def state(self) -> State:
        return State.OK if self.alert == 'none' else State.WARN

    @property
    def upper_levels(self) -> Tuple:
        return (self.hi_warn, self.hi_alarm)

    @property
    def lower_levels(self) -> Tuple:
        return (self.lo_warn, self.lo_alarm)

    @property
    def details(self) -> str:
        return '\n'.join(f'{self.type.name} {val}' for val in (
            f'alert: {self.alert}',
            f'status: {self.status}',
            f'hi_alarm: {self.hi_alarm}',
            f'hi_warn: {self.hi_warn}',
            f'lo_alarm: {self.lo_alarm}',
            f'lo_warn: {self.lo_warn}',
            f'value: {self.value} (precise)',
        ))


class DomPowerStat(NamedTuple):
    dn: str
    rx: DomPowerStatValues
    tx: DomPowerStatValues

    @property
    def interface(self) -> str:
        IFACE_REGEX: str = r'\[(?P<iface>eth\d+(/\d+){1,2})\]'
        iface_regex = re.compile(IFACE_REGEX)
        matches = iface_regex.search(self.dn)
        return f'{matches.group("iface")}'

    @staticmethod
    def from_string_table(line: Sequence) -> DomPowerStat:
        return DomPowerStat(
            dn=line[0],
            rx=DomPowerStatValues.from_string_table(PowerStatType.RX, line[1:8]),
            tx=DomPowerStatValues.from_string_table(PowerStatType.TX, line[8:]),
        )

    @property
    def id_length(self) -> int:
        return len(self.interface.split('/')[-1].lower().replace('eth', ''))


def parse_aci_dom_pwr_stats(string_table) -> List[DomPowerStat]:
    """
    Exmple output:
        #iface_dn rx_alert rx_status rx_hi_alarm rx_hi_warn rx_lo_alarm rx_lo_warn rx_value tx_alert tx_status tx_hi_alarm tx_hi_warn tx_lo_alarm tx_lo_warn tx_value
        topology/pod-1/node-112/sys/phys-[eth1/1]/phys none none 0.999912 0.000000 -13.098040 -12.097149 -2.599533 none none 0.999912 0.000000 -9.299622 -8.300319 -2.731099
        topology/pod-1/node-112/sys/phys-[eth1/11]/phys none none 0.999912 0.000000 -13.098040 -12.097149 -3.033815 none none 0.999912 0.000000 -9.299622 -8.300319 -2.668027
        topology/pod-1/node-112/sys/phys-[eth1/12]/phys none none 0.999912 0.000000 -13.098040 -12.097149 -2.896287 none none 0.999912 0.000000 -9.299622 -8.300319 -3.031196
    """
    return [
        DomPowerStat.from_string_table(line) for line in string_table
        if not line[0].startswith('#')
    ]


register.agent_section(
    name='aci_dom_pwr_stats',
    parse_function=parse_aci_dom_pwr_stats,
)


def _get_discovery_item_name(params: Dict, interface_id: str, pad_length: int) -> Tuple[Optional[str], List[ServiceLabel]]:
    """for example values for param, see tests"""
    return get_discovery_item_name(params, interface_id, pad_length)


def discover_aci_dom_pwr_stats(params, section: List[DomPowerStat]) -> DiscoveryResult:
    for pwr_stat in section:
        interface_id, labels = _get_discovery_item_name(params, pwr_stat.interface, pad_length=get_max_if_padding(section))
        if interface_id:
            yield Service(item=interface_id, labels=labels)


def check_aci_dom_pwr_stats(item: str, section: List[DomPowerStat]) -> CheckResult:
    for stat in section:
        if get_orig_interface_id(item) == stat.interface:
            for s in (stat.rx, stat.tx):

                yield Result(state=s.state, notice=s.summary, details=s.details)

                # Alerting works with dynamic warn/alert levels that are received from ACI
                yield from check_levels(s.value,
                                        levels_upper=s.upper_levels,
                                        levels_lower=s.lower_levels,
                                        metric_name=f'dom_{s.type.value}_power',
                                        label=f'{s.type.name} value')
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')


register.check_plugin(
    name='aci_dom_pwr_stats',
    service_name='Interface %s DOM Power',
    discovery_function=discover_aci_dom_pwr_stats,
    check_function=check_aci_dom_pwr_stats,
    discovery_ruleset_name='cisco_aci_if_discovery',
    discovery_default_parameters=DEFAULT_DISCOVERY_PARAMS,
)
