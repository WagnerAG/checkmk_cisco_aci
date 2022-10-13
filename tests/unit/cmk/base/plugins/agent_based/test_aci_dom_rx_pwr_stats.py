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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Service, Metric
from cmk.base.plugins.agent_based.aci_dom_rx_pwr_stats import (
    parse_aci_dom_rx_pwr_stats,
    discover_aci_dom_rx_pwr_stats,
    check_aci_dom_rx_pwr_stats,
    DomPowerStat,
)


SECTION_1: List = [
    DomPowerStat(
        dn='topology/pod-1/node-101/sys/phys-[eth1/3]/phys/domstats/rxpwer',
        alert='none',
        status='none',
        hi_alarm=5.000031,
        hi_warn=4.000023,
        lo_alarm=-13.695722,
        lo_warn=-11.700533,
        value=-1.674911,
    ),
]

SECTION_2: List = [
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth1/1]/phys/domstats/rxpower',
        alert='none',
        status='none',
        hi_alarm=0.999912,
        hi_warn=0.000000,
        lo_alarm=-13.098040,
        lo_warn=-12.097149,
        value=-2.599533,
    ),
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth1/11]/phys/domstats/rxpower',
        alert='warn',
        status='bla',
        hi_alarm=0.999912,
        hi_warn=0.000000,
        lo_alarm=-13.098040,
        lo_warn=-12.097149,
        value=0.910695,
    ),
    DomPowerStat(
        dn='topology/pod-1/node-112/sys/phys-[eth11/21/102]/phys/domstats/rxpower',
        alert='none',
        status='none',
        hi_alarm=5.000031,
        hi_warn=4.000023,
        lo_alarm=-13.695722,
        lo_warn=-11.700533,
        value=-15.648960,
    ),
]


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            []
        ),
        (
            [
                ['#dn', 'alert', 'status', 'hi_alarm', 'hi_warn', 'lo_alarm', 'lo_warn', 'value'],
                ['topology/pod-1/node-101/sys/phys-[eth1/3]/phys/domstats/rxpwer', 'none', 'none', '5.000031', '4.000023', '-13.695722', '-11.700533', '-1.674911'],
            ],
            SECTION_1,
        ),
        (
            [
                # shall also work without a header row
                ['topology/pod-1/node-112/sys/phys-[eth1/1]/phys/domstats/rxpower', 'none', 'none', '0.999912', '0.000000', '-13.098040', '-12.097149', '-2.599533'],
                ['topology/pod-1/node-112/sys/phys-[eth1/11]/phys/domstats/rxpower', 'warn', 'bla', '0.999912', '0.000000', '-13.098040', '-12.097149', '0.910695'],
                ['topology/pod-1/node-112/sys/phys-[eth11/21/102]/phys/domstats/rxpower', 'none', 'none', '5.000031', '4.000023', '-13.695722', '-11.700533', '-15.648960'],
            ],
            SECTION_2,
        ),
    ],
)
def test_parse_aci_dom_rx_pwr_stats(string_table: List[List[str]], expected_section: List[DomPowerStat]) -> None:
    assert parse_aci_dom_rx_pwr_stats(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_discovery_result",
    [
        (
            SECTION_1,
            (
                Service(item='eth1/3'),
            ),
        ),
        (
            SECTION_2,
            (
                Service(item='eth1/1'),
                Service(item='eth1/11'),
                Service(item='eth11/21/102'),
            ),
        ),
    ],
)
def test_discover_aci_dom_rx_pwr_stats(section: List[DomPowerStat], expected_discovery_result: Tuple) -> None:
    assert tuple(discover_aci_dom_rx_pwr_stats(section)) == expected_discovery_result


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
            'eth1/1',
            SECTION_2,
            (
                Result(state=State.OK, notice='alert: none, status: none',
                       details='alert: none\nstatus: none\nhi_alarm: 0.999912\nhi_warn: 0.0\nlo_alarm: -13.09804\nlo_warn: -12.097149\nvalue: -2.599533 (precise)'),
                Result(state=State.OK, summary='value: -2.60'),
                Metric('dom_rx_power', -2.599533, levels=(0.0, 0.999912))
            )
        ),
        (
            'eth1/11',
            SECTION_2,
            (
                Result(state=State.WARN, notice='alert: warn, status: bla',
                       details='alert: warn\nstatus: bla\nhi_alarm: 0.999912\nhi_warn: 0.0\nlo_alarm: -13.09804\nlo_warn: -12.097149\nvalue: 0.910695 (precise)'),
                Result(state=State.WARN, summary='value: 0.91 (warn/crit at 0.00/1.00)'),
                Metric('dom_rx_power', 0.910695, levels=(0.0, 0.999912))
            )
        ),
        (
            'eth11/21/102',
            SECTION_2,
            (
                Result(state=State.OK, notice='alert: none, status: none',
                       details='alert: none\nstatus: none\nhi_alarm: 5.000031\nhi_warn: 4.000023\nlo_alarm: -13.695722\nlo_warn: -11.700533\nvalue: -15.64896 (precise)'),
                Result(state=State.CRIT, summary='value: -15.65 (warn/crit below -11.70/-13.70)'),
                Metric('dom_rx_power', -15.64896, levels=(4.000023, 5.000031)),
            )
        ),
    ],
)
def test_check_aci_dom_rx_pwr_stats(item: str, section: List[DomPowerStat], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_dom_rx_pwr_stats(item, section)) == expected_check_result
