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
from typing import Dict, List, NamedTuple, Optional
import time

from cmk.agent_based.v2 import (
    check_levels,
    CheckResult,
    DiscoveryResult,
    CheckPlugin,
    AgentSection,
    Result,
    Service,
    State,
    get_rate,
    get_value_store,
)
from .aci_general import convert_rate, to_int


# by default we only alert on BGP connection drop
DEFAULT_BGP_RATE_LEVELS: Dict = {
    "level_bgp_drop": (1.0, 6.0),
}


def con_rate(value: float) -> str:
    return f"{value:0.2f}/min"


class ConnectionRates(NamedTuple):
    attempts: float
    drop: float
    est: float

    @staticmethod
    def get_connection_rates(addr: str, attempts: int, drop: int, est: int):
        value_store = get_value_store()
        now = time.time()

        return ConnectionRates(
            attempts=convert_rate(get_rate(value_store, f"cisco_aci.{addr}.bgp.conn_attempts", now, attempts)),
            drop=convert_rate(get_rate(value_store, f"cisco_aci.{addr}.bgp.conn_drop", now, drop)),
            est=convert_rate(get_rate(value_store, f"cisco_aci.{addr}.bgp.conn_est", now, est)),
        )


@dataclass
class BgpPeerEntry:
    addr: str
    conn_attempts: str
    conn_drop: str
    conn_est: str
    local_ip: str
    local_port: str
    oper_st: str
    remote_port: str
    type: str
    rates: Optional[ConnectionRates] = None

    def calculate_counters(self) -> ConnectionRates:
        """calculate the error rate using value_store and get_rate

        values are stored using bgp address
        """
        if not self.rates:
            self.rates = ConnectionRates.get_connection_rates(
                addr=self.addr,
                attempts=to_int(self.conn_attempts),
                drop=to_int(self.conn_drop),
                est=to_int(self.conn_est),
            )

            return self.rates

        return self.rates

    @property
    def summary(self) -> str:
        return f"type: {self.type}, " f"remote: {self.addr}:{self.remote_port}, " f"local: {self.local_ip}:{self.local_port}"

    @property
    def details(self) -> str:
        self.calculate_counters()
        return f"type: {self.type}\n" f"remote: {self.addr}:{self.remote_port}\n" f"local: {self.local_ip}:{self.local_port}\n" f"connAttempts: {self.rates.attempts}/min (Total: {self.conn_attempts})\n" f"connDrop: {self.rates.drop}/min (Total: {self.conn_drop})\n" f"connEst: {self.rates.est}/min (Total: {self.conn_est})"

    @property
    def cmk_state(self) -> State:
        if self.oper_st == "established":
            return State.OK
        if self.oper_st == "idle":
            return State.WARN
        return State.CRIT

    @staticmethod
    def from_string_table(line) -> BgpPeerEntry:
        return BgpPeerEntry(
            addr=line[0],
            conn_attempts=line[1],
            conn_drop=line[2],
            conn_est=line[3],
            local_ip=line[4],
            local_port=line[5],
            oper_st=line[6],
            remote_port=line[7],
            type=line[8],
        )


def parse_aci_bgp_peer_entry(string_table) -> List[BgpPeerEntry]:
    """
    Exmple output:
        #addr connAttempts connDrop connEst localIp localPort operSt remotePort type
        10.77.128.64 na 0 1 10.77.128.65 179 established 35090 ibgp
        10.77.128.66 na 0 1 10.77.128.65 179 established 57895 ibgp
        172.16.0.167 na 0 1 172.16.0.166 179 established 51984 ebgp
        172.16.0.171 1 0 1 172.16.0.170 179 established 24988 ebgp
        10.79.7.34 11428 0 0 0.0.0.0 unspecified idle unspecified ebgp
        10.79.7.38 11428 0 0 0.0.0.0 unspecified idle unspecified ebgp
    """
    return [BgpPeerEntry.from_string_table(line) for line in string_table if not line[0].startswith("#")]





def discover_aci_bgp_peer_entry(section: List[BgpPeerEntry]) -> DiscoveryResult:
    for bgp_peer_entry in section:
        yield Service(item=bgp_peer_entry.addr)


def _check_rates(params: Dict, bgp_peer_entry: BgpPeerEntry) -> CheckResult:
    """execute check_levels for all types of ConnectionRates."""
    bgp_peer_entry.calculate_counters()
    for rate_type in ConnectionRates._fields:
        yield from check_levels(getattr(bgp_peer_entry.rates, rate_type), levels_upper=params.get(f"level_bgp_{rate_type}"), metric_name=f"bgp_conn_{rate_type}", boundaries=(0.0, None), label=f"BGP connection {rate_type} value", render_func=con_rate, notice_only=True)


def check_aci_bgp_peer_entry(item: str, params: Dict, section: List[BgpPeerEntry]) -> CheckResult:
    for entry in section:
        if item == entry.addr:
            yield Result(state=entry.cmk_state, summary=f"state: {entry.oper_st}")
            yield Result(state=State.OK, summary=entry.summary, details=entry.details)
            yield from _check_rates(params, entry)
            break
    else:
        yield Result(state=State.UNKNOWN, summary="Sorry - item not found")


agent_section_cisco_aci_bgp_peer_entry = AgentSection(
    name="aci_bgp_peer_entry",
    parse_function=parse_aci_bgp_peer_entry,
)


check_plugin_cisco_aci_bgp_peer_entry = CheckPlugin(
    name="aci_bgp_peer_entry",
    service_name="BGP peer entry %s",
    discovery_function=discover_aci_bgp_peer_entry,
    check_function=check_aci_bgp_peer_entry,
    check_ruleset_name="aci_bgp_peer_entry_levels",
    check_default_parameters=DEFAULT_BGP_RATE_LEVELS,
)
