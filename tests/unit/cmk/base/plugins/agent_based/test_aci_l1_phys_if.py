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
from unittest.mock import patch
from datetime import datetime, timedelta

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from cmk.base.plugins.agent_based.aci_l1_phys_if import (
    parse_aci_l1_phys_if,
    check_aci_l1_phys_if,
    AciL1Interface,
)


L1_INTERFACES: List[AciL1Interface] = {
    'eth1/33': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/33]', id='eth1/33', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='10G',
    ),

    'eth1/34': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/34]', id='eth1/34', admin_state='up', layer='Layer2',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='10G',
    ),

    'eth1/1': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/1]', id='eth1/1', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='up', op_speed='40G',
    ),

    'eth1/2': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/2]', id='eth1/2', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='unknown',
    ),

    'eth1/3': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/3]', id='eth1/3', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='up', op_speed='40G',
    ),

    'eth1/4': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/4]', id='eth1/4', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=1, op_state='up', op_speed='100G',
    ),

    'eth1/5': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/5]', id='eth1/5', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='100G',
    ),

    'nsa1/1': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[nsa1/1]', id='nsa1/1', admin_state='up', layer='Layer9',
        crc_errors=0, fcs_errors=0, op_state='up', op_speed='10T',
    ),
}


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            {}
        ),
        (
            [
                ['#dn', 'id', 'admin_state', 'layer', 'crc_errors', 'fcs_errors', 'op_state', 'op_speed'],
                ['topology/pod-1/node-101/sys/phys-[eth1/20]', 'eth1/20', 'up', 'Layer3', '0', '0', 'down', '100G'],
            ],
            {
                'eth1/20': AciL1Interface(
                    dn='topology/pod-1/node-101/sys/phys-[eth1/20]', id='eth1/20', admin_state='up', layer='Layer3',
                    crc_errors=0, fcs_errors=0, op_state='down', op_speed='100G'
                ),
            }
        ),
        (
            [
                ['#dn', 'id', 'admin_state', 'layer', 'crc_errors', 'fcs_errors', 'op_state', 'op_speed'],
                ['topology/pod-1/node-101/sys/phys-[eth1/33]', 'eth1/33', 'up', 'Layer3', '0', '0', 'down', '10G'],
                ['topology/pod-1/node-101/sys/phys-[eth1/34]', 'eth1/34', 'up', 'Layer2', '0', '0', 'down', '10G'],
                ['topology/pod-1/node-101/sys/phys-[eth1/1]', 'eth1/1', 'up', 'Layer3', '0', '0', 'up', '40G'],
                ['topology/pod-1/node-101/sys/phys-[eth1/2]', 'eth1/2', 'up', 'Layer3', '0', '0', 'down', 'unknown'],
                ['topology/pod-1/node-101/sys/phys-[eth1/3]', 'eth1/3', 'up', 'Layer3', '0', '0', 'up', '40G'],
                ['topology/pod-1/node-101/sys/phys-[eth1/4]', 'eth1/4', 'up', 'Layer3', '0', '1', 'up', '100G'],
                ['topology/pod-1/node-101/sys/phys-[eth1/5]', 'eth1/5', 'up', 'Layer3', '0', '0', 'down', '100G'],
                ['topology/pod-1/node-101/sys/phys-[nsa1/1]', 'nsa1/1', 'up', 'Layer9', '0', '0', 'up', '10T'],
            ],
            L1_INTERFACES,
        ),
    ],
)
def test_parse_aci_l1_phys_if(string_table: List[List[str]], expected_section: Dict[str, AciL1Interface]) -> None:
    assert parse_aci_l1_phys_if(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            '',
            {},
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
        (
            'eth1/33',
            L1_INTERFACES,
            (
                Result(
                    state=State.WARN,
                    summary=('admin_state=up op_state=down layer=Layer3 op_speed=10G | errors: FCS=0.0 CRC=0.0 stomped_CRC=0.0')
                ),
                Metric('fcs_errors', 0.0, levels=(0.001, 0.001)),
                Metric('crc_errors', 0.0),
                Metric('stomped_crc_errors', 0.0, levels=(0.001, 100)),
            ),
        ),
    ],
)
def test_check_aci_l1_phys_if(item: str, section: Dict[str, AciL1Interface], expected_check_result: Tuple) -> None:
    with patch('cmk.base.plugins.agent_based.aci_l1_phys_if.get_value_store') as mock_get:
        if item:
            timestamp = int((datetime.now() - timedelta(minutes=10)).timestamp())
            dn = section.get(item).dn
            mock_get.return_value = {f'cisco_aci.{dn}.crc': (timestamp, 0.0), f'cisco_aci.{dn}.fcs': (timestamp, 0.0)}
        assert tuple(check_aci_l1_phys_if(item, section)) == expected_check_result
