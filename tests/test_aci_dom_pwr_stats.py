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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from plugins.cisco_aci.agent_based.aci_dom_pwr_stats import (
    parse_aci_dom_pwr_stats,
    check_aci_dom_pwr_stats,
    DomPowerStat,
    DomPowerStatValues,
    PowerStatType,
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
    "string_table, expected_section",
    [
        (
            [],
            []
        ),
        (
            [
                ['#iface_dn', 'rx_alert', 'rx_status', 'rx_hi_alarm', 'rx_hi_warn', 'rx_lo_alarm', 'rx_lo_warn', 'rx_value', 'tx_alert', 'tx_status', 'tx_hi_alarm', 'tx_hi_warn', 'tx_lo_alarm', 'tx_lo_warn', 'tx_value'],
                ['topology/pod-1/node-101/sys/phys-[eth1/3]/phys', 'none', 'none', '5.000031', '4.000023', '-13.695722', '-11.700533', '-1.726307', 'none', 'none', '5.000031', '4.000023', '-8.498579', '-7.500682', '1.162756'],
            ],
            SECTION_1,
        ),
        (
            [
                # shall also work without a header row
                ['topology/pod-1/node-112/sys/phys-[eth1/1]/phys', 'none', 'none', '0.999912', '0.000000', '-13.098040', '-12.097149', '-2.599533', 'none', 'none', '0.999912', '0.000000', '-9.299622', '-8.300319', '-2.731099'],
                ['topology/pod-1/node-112/sys/phys-[eth1/11]/phys', 'warn', 'bla', '0.999912', '0.000000', '-13.098040', '-12.097149', '0.910695', 'none', 'none', '0.999912', '0.000000', '-9.299622', '-8.300319', '0.668027'],
                ['topology/pod-1/node-112/sys/phys-[eth11/21/102]/phys', 'none', 'none', '5.000031', '4.000023', '-13.695722', '-11.700533', '-15.648960', 'none', 'none', '0.999912', '0.000000', '-9.299622', '-8.300319', '-11.031196'],
            ],
            SECTION_2,
        ),
    ],
)
def test_parse_aci_dom_pwr_stats(string_table: List[List[str]], expected_section: List[DomPowerStat]) -> None:
    assert parse_aci_dom_pwr_stats(string_table) == expected_section


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
                Result(state=State.OK, notice='RX alert: none, RX status: none',
                       details='RX alert: none\nRX status: none\nRX hi_alarm: 0.999912\nRX hi_warn: 0.0\nRX lo_alarm: -13.09804\nRX lo_warn: -12.097149\nRX value: -2.599533 (precise)'),
                Result(state=State.OK, summary='RX value: -2.60'),
                Metric('dom_rx_power', -2.599533, levels=(0.0, 0.999912)),
                Result(state=State.OK, notice='TX alert: none, TX status: none',
                       details='TX alert: none\nTX status: none\nTX hi_alarm: 0.999912\nTX hi_warn: 0.0\nTX lo_alarm: -9.299622\nTX lo_warn: -8.300319\nTX value: -2.731099 (precise)'),
                Result(state=State.OK, summary='TX value: -2.73'),
                Metric('dom_tx_power', -2.731099, levels=(0.0, 0.999912)),
            )
        ),
        (
            'eth1/11',
            SECTION_2,
            (
                Result(state=State.WARN, notice='RX alert: warn, RX status: bla',
                       details='RX alert: warn\nRX status: bla\nRX hi_alarm: 0.999912\nRX hi_warn: 0.0\nRX lo_alarm: -13.09804\nRX lo_warn: -12.097149\nRX value: 0.910695 (precise)'),
                Result(state=State.WARN, summary='RX value: 0.91 (warn/crit at 0.00/1.00)'),
                Metric('dom_rx_power', 0.910695, levels=(0.0, 0.999912)),
                Result(state=State.OK, notice='TX alert: none, TX status: none',
                       details='TX alert: none\nTX status: none\nTX hi_alarm: 0.999912\nTX hi_warn: 0.0\nTX lo_alarm: -9.299622\nTX lo_warn: -8.300319\nTX value: 0.668027 (precise)'),
                Result(state=State.WARN, summary='TX value: 0.67 (warn/crit at 0.00/1.00)'),
                Metric('dom_tx_power', 0.668027, levels=(0.0, 0.999912)),
            )
        ),
        (
            'eth11/21/102',
            SECTION_2,
            (
                Result(state= State.OK, notice='RX alert: none, RX status: none',
                       details='RX alert: none\nRX status: none\nRX hi_alarm: 5.000031\nRX hi_warn: 4.000023\nRX lo_alarm: -13.695722\nRX lo_warn: -11.700533\nRX value: -15.64896 (precise)'),
                Result(state=State.CRIT, summary='RX value: -15.65 (warn/crit below -11.70/-13.70)'),
                Metric('dom_rx_power', -15.64896, levels=(4.000023, 5.000031)),
                Result(state= State.OK, notice='RX alert: none, RX status: none',
                       details='TX alert: none\nTX status: none\nTX hi_alarm: 0.999912\nTX hi_warn: 0.0\nTX lo_alarm: -9.299622\nTX lo_warn: -8.300319\nTX value: -11.031196 (precise)'),
                Result(state=State.CRIT, summary='TX value: -11.03 (warn/crit below -8.30/-9.30)'),
                Metric('dom_tx_power', -11.031196, levels=(0.0, 0.999912)),
            )
        ),
        (
            'eth1/001',
            SECTION_2,
            (
                Result(state=State.OK, notice='RX alert: none, RX status: none',
                       details='RX alert: none\nRX status: none\nRX hi_alarm: 0.999912\nRX hi_warn: 0.0\nRX lo_alarm: -13.09804\nRX lo_warn: -12.097149\nRX value: -2.599533 (precise)'),
                Result(state=State.OK, summary='RX value: -2.60'),
                Metric('dom_rx_power', -2.599533, levels=(0.0, 0.999912)),
                Result(state=State.OK, notice='TX alert: none, TX status: none',
                       details='TX alert: none\nTX status: none\nTX hi_alarm: 0.999912\nTX hi_warn: 0.0\nTX lo_alarm: -9.299622\nTX lo_warn: -8.300319\nTX value: -2.731099 (precise)'),
                Result(state=State.OK, summary='TX value: -2.73'),
                Metric('dom_tx_power', -2.731099, levels=(0.0, 0.999912)),
            )
        ),
    ],
)
def test_check_aci_dom_pwr_stats(item: str, section: List[DomPowerStat], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_dom_pwr_stats(item, section)) == expected_check_result
