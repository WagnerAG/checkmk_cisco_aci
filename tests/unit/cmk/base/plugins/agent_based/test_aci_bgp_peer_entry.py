#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from typing import Tuple, List

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.aci_bgp_peer_entry import (
    parse_aci_bgp_peer_entry,
    check_aci_bgp_peer_entry,
    BgpPeerEntry,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            []
        ),
        (
            [
                ["#", "addr", "connAttempts", "connDrop", "connEst", "localIp", "localPort", "operSt", "remotePort", "type"],
                ["10.77.128.64", "na", "0", "1", "10.77.128.65", "179", "established", "49916", "ibgp"],
            ],
            [
                BgpPeerEntry(
                    addr='10.77.128.64',
                    conn_attempts='na',
                    conn_drop='0',
                    conn_est='1',
                    local_ip='10.77.128.65',
                    local_port='179',
                    oper_st='established',
                    remote_port='49916',
                    type='ibgp',
                ),
            ]
        ),
        (
            [
                ["#", "addr", "connAttempts", "connDrop", "connEst", "localIp", "localPort", "operSt", "remotePort", "type"],
                ["10.77.128.64", "na", "0", "1", "10.77.128.65", "179", "established", "49916", "ibgp"],
                ["10.79.7.34", "1144", "4", "4", "0.0.0.0", "unspecified", "idle", "unspecified", "ebgp"],
            ],
            [
                BgpPeerEntry(
                    addr='10.77.128.64',
                    conn_attempts='na',
                    conn_drop='0',
                    conn_est='1',
                    local_ip='10.77.128.65',
                    local_port='179',
                    oper_st='established',
                    remote_port='49916',
                    type='ibgp',
                ),
                BgpPeerEntry(
                    addr='10.79.7.34',
                    conn_attempts='1144',
                    conn_drop='4',
                    conn_est='4',
                    local_ip='0.0.0.0',
                    local_port='unspecified',
                    oper_st='idle',
                    remote_port='unspecified',
                    type='ebgp',
                ),
            ]
        ),
    ],
)
def test_parse_aci_bgp_peer_entry(string_table: List[List[str]], expected_section: List[BgpPeerEntry]) -> None:
    assert parse_aci_bgp_peer_entry(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            '',
            [],
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
        (
            '10.79.7.34',
            [
                BgpPeerEntry(
                    addr='10.79.7.34',
                    conn_attempts='1144',
                    conn_drop='4',
                    conn_est='4',
                    local_ip='0.0.0.0',
                    local_port='unspecified',
                    oper_st='idle',
                    remote_port='unspecified',
                    type='ebgp',
                ),
                BgpPeerEntry(
                    addr='10.77.128.64',
                    conn_attempts='na',
                    conn_drop='0',
                    conn_est='1',
                    local_ip='10.77.128.65',
                    local_port='179',
                    oper_st='established',
                    remote_port='49916',
                    type='ibgp',
                ),
            ],
            (
                Result(
                    state=State.OK,
                    summary=(
                        'state=idle type=ebgp'
                        'remote=10.79.7.34:unspecified '
                        'local=0.0.0.0:unspecified '
                        'connAttempts=1144 '
                        'connDrop=4 connEst=4'
                    )
                ),
            ),
        ),
    ],
)
def test_check_aci_bgp_peer_entry(item: str, section: List[BgpPeerEntry], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_bgp_peer_entry(item, section)) == expected_check_result
