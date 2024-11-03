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

from typing import Dict, Tuple, List
from unittest.mock import patch
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from plugins.cisco_aci.agent_based.aci_bgp_peer_entry import (
    parse_aci_bgp_peer_entry,
    check_aci_bgp_peer_entry,
    BgpPeerEntry,
)


DEFAULT_BGP_RATE_LEVELS: Dict = {
    'level_bgp_attempts': {'warn': 1.0, 'crit': 6.0},
    'level_bgp_drop': {'warn': 1.0, 'crit': 6.0},
    'level_bgp_est': {'warn': 1.0, 'crit': 6.0},
}


def mocked_value_store(addr: str, timestamp: int) -> Dict:
    return {
        f'cisco_aci.{addr}.bgp.conn_attempts': (timestamp, 0.0),
        f'cisco_aci.{addr}.bgp.conn_drop': (timestamp, 0.0),
        f'cisco_aci.{addr}.bgp.conn_est': (timestamp, 0.0),
    }


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


@freeze_time("1998-08-15 09:00:00")
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
            '10.77.128.64',
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
                Result(state=State.OK, summary='state: established'),
                Result(
                    state=State.OK,
                    summary='type: ibgp, remote: 10.77.128.64:49916, local: 10.77.128.65:179',
                    details=(
                        'type: ibgp\nremote: 10.77.128.64:49916\nlocal: 10.77.128.65:179\n'
                        'connAttempts: 0.0/min (Total: na)\nconnDrop: 0.0/min (Total: 0)\nconnEst: 0.5/min (Total: 1)'
                    )
                ),
                Result(state= State.OK, notice='BGP connection attempts value: 0.00/min'),
                Metric('bgp_conn_attempts', 0.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.OK, notice='BGP connection drop value: 0.00/min'),
                Metric('bgp_conn_drop', 0.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.OK, notice='BGP connection est value: 0.50/min'),
                Metric('bgp_conn_est', 0.5, levels=(1.0, 6.0), boundaries=(0.0, None)),
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
            ],
            (
                Result(state=State.WARN, summary='state: idle'),
                Result(
                    state=State.OK,
                    summary='type: ebgp, remote: 10.79.7.34:unspecified, local: 0.0.0.0:unspecified',
                    details=(
                        'type: ebgp\nremote: 10.79.7.34:unspecified\nlocal: 0.0.0.0:unspecified\n'
                        'connAttempts: 572.0/min (Total: 1144)\nconnDrop: 2.0/min (Total: 4)\nconnEst: 2.0/min (Total: 4)'
                    )
                ),
                Result(state=State.CRIT, summary='BGP connection attempts value: 572.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_attempts', 572.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.WARN, summary='BGP connection drop value: 2.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_drop', 2.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.WARN, summary='BGP connection est value: 2.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_est', 2.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
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
                    oper_st='invalid',
                    remote_port='unspecified',
                    type='ebgp',
                ),
            ],
            (
                Result(state=State.CRIT, summary='state: invalid'),
                Result(
                    state=State.OK,
                    summary='type: ebgp, remote: 10.79.7.34:unspecified, local: 0.0.0.0:unspecified',
                    details=(
                        'type: ebgp\nremote: 10.79.7.34:unspecified\nlocal: 0.0.0.0:unspecified\n'
                        'connAttempts: 572.0/min (Total: 1144)\nconnDrop: 2.0/min (Total: 4)\nconnEst: 2.0/min (Total: 4)'
                    )
                ),
                Result(state=State.CRIT, summary='BGP connection attempts value: 572.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_attempts', 572.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.WARN, summary='BGP connection drop value: 2.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_drop', 2.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
                Result(state= State.WARN, summary='BGP connection est value: 2.00/min (warn/crit at 1.00/min/6.00/min)'),
                Metric('bgp_conn_est', 2.0, levels=(1.0, 6.0), boundaries=(0.0, None)),
            ),
        ),
    ],
)
def test_check_aci_bgp_peer_entry(item: str, section: List[BgpPeerEntry], expected_check_result: Tuple) -> None:
    with patch('plugins.cisco_aci.agent_based.aci_bgp_peer_entry.get_value_store') as mock_get:
        if item:
            element = next(elem for elem in section if elem.addr == item)
            mock_get.return_value = mocked_value_store(
                addr=element.addr,
                timestamp=int((datetime.now() - timedelta(minutes=2)).timestamp())
            )
        assert tuple(check_aci_bgp_peer_entry(item, DEFAULT_BGP_RATE_LEVELS, section)) == expected_check_result
