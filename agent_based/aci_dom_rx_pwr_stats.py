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

Authors:    Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.7

"""

from __future__ import annotations
from typing import List, NamedTuple, Sequence, Tuple
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
    State,
)


class DomPowerStat(NamedTuple):
    dn: str
    alert: str
    status: str
    hi_alarm: float
    hi_warn: float
    lo_alarm: float
    lo_warn: float
    value: float

    @property
    def details(self) -> str:
        return (
            f'alert: {self.alert}\n'
            f'status: {self.status}\n'
            f'hi_alarm: {self.hi_alarm}\n'
            f'hi_warn: {self.hi_warn}\n'
            f'lo_alarm: {self.lo_alarm}\n'
            f'lo_warn: {self.lo_warn}\n'
            f'value: {self.value} (precise)'
        )

    @property
    def summary(self) -> str:
        return f'alert: {self.alert}, status: {self.status}'

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
    def interface(self) -> str:
        IFACE_REGEX: str = r'\[(?P<iface>eth\d+(/\d+){1,2})\]'
        iface_regex = re.compile(IFACE_REGEX)
        matches = iface_regex.search(self.dn)
        return f'{matches.group("iface")}'

    @staticmethod
    def from_string_table(line: Sequence) -> DomPowerStat:
        return DomPowerStat(
            dn=line[0],
            alert=line[1],
            status=line[2],
            hi_alarm=float(line[3]),
            hi_warn=float(line[4]),
            lo_alarm=float(line[5]),
            lo_warn=float(line[6]),
            value=float(line[7]),
        )


def parse_aci_dom_rx_pwr_stats(string_table) -> List[DomPowerStat]:
    """
    Exmple output:
        #dn alert status hi_alarm hi_warn lo_alarm lo_warn value
        topology/pod-1/node-112/sys/phys-[eth1/1]/phys/domstats/rxpower none none 0.999912 0.000000 -13.098040 -12.097149 -2.599533
        topology/pod-1/node-112/sys/phys-[eth1/11]/phys/domstats/rxpower none none 0.999912 0.000000 -13.098040 -12.097149 -2.910695
        topology/pod-1/node-112/sys/phys-[eth1/12]/phys/domstats/rxpower none none 0.999912 0.000000 -13.098040 -12.097149 -2.814153
    """
    return [
        DomPowerStat.from_string_table(line) for line in string_table
        if not line[0].startswith('#')
    ]


register.agent_section(
    name='aci_dom_rx_pwr_stats',
    parse_function=parse_aci_dom_rx_pwr_stats,
)


def discover_aci_dom_rx_pwr_stats(section: List[DomPowerStat]) -> DiscoveryResult:
    for pwr_stat in section:
        yield Service(item=pwr_stat.interface)


def check_aci_dom_rx_pwr_stats(item: str, section: List[DomPowerStat]) -> CheckResult:
    for stat in section:
        if item == stat.interface:
            yield Result(state=stat.state, notice=stat.summary, details=stat.details)

            # Alerting works with dynamic warn/alert levels that are received from ACI
            yield from check_levels(stat.value,
                                    levels_upper=stat.upper_levels,
                                    levels_lower=stat.lower_levels,
                                    metric_name='dom_rx_power',
                                    label='value')
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')


register.check_plugin(
    name='aci_dom_rx_pwr_stats',
    service_name='DOM Rx Power %s',
    discovery_function=discover_aci_dom_rx_pwr_stats,
    check_function=check_aci_dom_rx_pwr_stats,
)
