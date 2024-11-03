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

from typing import Tuple, List, Dict

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Service, ServiceLabel
from plugins.cisco_aci.agent_based.aci_dom_pwr_stats import (
    discover_aci_dom_pwr_stats,
    DomPowerStat,
    DomPowerStatValues,
    PowerStatType,
    DEFAULT_DISCOVERY_PARAMS,
)


SECTION_1: List = [
    DomPowerStat(
        dn='topology/pod-1/node-101/sys/phys-[eth1/3]/phys',
        rx=DomPowerStatValues(
            PowerStatType.RX, 'none', 'none', 5.000031, 4.000023, -13.695722, -11.700533, -1.726307,
        ),
        tx=DomPowerStatValues(
            PowerStatType.TX, 'none', 'none', 5.000031, 4.000023, -8.498579, -7.500682, 1.162756,
        )
    ),
]

SECTION_2: List = [
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth1/1]/phys',
        rx=DomPowerStatValues(
            PowerStatType.RX, 'none', 'none', 0.999912, 0.000000, -13.098040, -12.097149, -2.599533,
        ),
        tx=DomPowerStatValues(
            PowerStatType.TX, 'none', 'none', 0.999912, 0.000000, -9.299622, -8.300319, -2.731099
        )
    ),
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth1/11]/phys',
        rx=DomPowerStatValues(
            PowerStatType.RX, 'warn', 'bla', 0.999912, 0.000000, -13.098040, -12.097149, 0.910695,
        ),
        tx=DomPowerStatValues(
            PowerStatType.TX, 'none', 'none', 0.999912, 0.000000, -9.299622, -8.300319, 0.668027,
        )
    ),
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth11/21/102]/phys',
        rx=DomPowerStatValues(
            PowerStatType.RX, 'none', 'none', 5.000031, 4.000023, -13.695722, -11.700533, -15.648960,
        ),
        tx=DomPowerStatValues(
            PowerStatType.TX, 'none', 'none', 0.999912, 0.000000, -9.299622, -8.300319, -11.031196,
        )
    ),
]


@pytest.mark.parametrize(
    "params, section, expected_discovery_result",
    [
        (
            DEFAULT_DISCOVERY_PARAMS,
            SECTION_1,
            (
                Service(item='Ethernet1/3'),
            ),
        ),
        (
            DEFAULT_DISCOVERY_PARAMS,
            SECTION_2,
            (
                Service(item='Ethernet1/1'),
                Service(item='Ethernet1/11'),
                Service(item='Ethernet11/21/102'),
            ),
        ),
        (
            {
                'discovery_single': (False, {}),
                'matching_conditions': (True, {})
            },
            SECTION_2,
            tuple(),
        ),
        (
            {
                'discovery_single': (True, {
                    'long_if_name': False,
                    'pad_portnumbers': False,
                    'labels': {'os': 'aci_büchse'},
                }),
                'matching_conditions': (False, {'port_admin_states': ['2']})  # no effect for this check
            },
            SECTION_2,
            (
                Service(item='eth1/1', labels=[ServiceLabel('os', 'aci_büchse')]),
                Service(item='eth1/11', labels=[ServiceLabel('os', 'aci_büchse')]),
                Service(item='eth11/21/102', labels=[ServiceLabel('os', 'aci_büchse')]),
            ),
        ),
        (
            {
                'discovery_single': (True, {'long_if_name': False, 'pad_portnumbers': True}),
                'matching_conditions': (False, {'port_admin_states': ['1']})  # no effect for this check
            },
            SECTION_2,
            (
                Service(item='eth1/001'),
                Service(item='eth1/011'),
                Service(item='eth11/21/102'),
            ),
        ),
    ],
)
def test_discover_aci_dom_pwr_stats(params: Dict, section: List[DomPowerStat], expected_discovery_result: Tuple) -> None:
    assert tuple(discover_aci_dom_pwr_stats(params, section)) == expected_discovery_result
