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
Version:    0.7

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


class BgpPeerEntry(NamedTuple):
    addr: str
    conn_attempts: str
    conn_drop: str
    conn_est: str
    local_ip: str
    local_port: str
    oper_st: str
    remote_port: str
    type: str

    @property
    def summary(self) -> str:
        return (
            f'state={self.oper_st} type={self.type}'
            f'remote={self.addr}:{self.remote_port} '
            f'local={self.local_ip}:{self.local_port} '
            f'connAttempts={self.conn_attempts} '
            f'connDrop={self.conn_drop} connEst={self.conn_est}'
        )

    @property
    def cmk_state(self) -> State:
        if self.oper_st == 'established':
            return State.OK
        if self.oper_st == 'idle':
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
        controller 1 APIC1 in-service FCH1835V2FM APIC-SERVER-M1 APIC-SERVER-M1

        controller 1 ACI01 in-service FCH1935V1Z8 APIC-SERVER-M2 APIC-SERVER-M2
    """
    return [
        BgpPeerEntry.from_string_table(line) for line in string_table
        if not line[0].startswith('#')
    ]


register.agent_section(
    name='aci_bgp_peer_entry',
    parse_function=parse_aci_bgp_peer_entry,
)


def discover_aci_bgp_peer_entry(section: List[BgpPeerEntry]) -> DiscoveryResult:
    for bgp_peer_entry in section:
        yield Service(item=bgp_peer_entry.addr)


def check_aci_bgp_peer_entry(item: str, section: List[BgpPeerEntry]) -> CheckResult:
    for entry in section:
        if item == entry.addr:
            yield Result(
                state=entry.cmk_state,
                summary=entry.summary
            )
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')


register.check_plugin(
    name='aci_bgp_peer_entry',
    service_name='BGP peer entry %s',
    discovery_function=discover_aci_bgp_peer_entry,
    check_function=check_aci_bgp_peer_entry,
)
