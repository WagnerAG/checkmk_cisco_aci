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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Service
from cmk.base.plugins.agent_based.aci_l1_phys_if import (
    discover_aci_l1_phys_if,
    AciL1Interface,
    pad_interface_id,
    unpad_interface_id,
)


L1_INTERFACES: List[AciL1Interface] = {
    'eth1/33': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/33]', id='eth1/33', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='10G', rates=None,
    ),

    'eth1/34': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/34]', id='eth1/34', admin_state='down', layer='Layer2',
        crc_errors=0, fcs_errors=0, op_state='down', op_speed='10G', rates=None,
    ),

    'eth1/1': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/1]', id='eth1/1', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='up', op_speed='40G', rates=None,
    ),

    'eth1/2': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/2]', id='eth1/2', admin_state='up', layer='Layer3',
        crc_errors=0, fcs_errors=0, op_state='unknown', op_speed='unknown', rates=None,
    ),

    'eth1/3': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/3]', id='eth1/3', admin_state='up', layer='Layer3',
        crc_errors=131, fcs_errors=0, op_state='link-up', op_speed='40G', rates=None,
    ),

    'eth1/4': AciL1Interface(
        dn='topology/pod-1/node-101/sys/phys-[eth1/4]', id='eth1/4', admin_state='up', layer='Layer3',
        crc_errors=289, fcs_errors=217, op_state='channel-admin-down', op_speed='100G', rates=None,
    ),
}


@pytest.mark.parametrize(
    "params, section, expected_services",
    [
        (
            {},
            L1_INTERFACES,
            (
                Service(item='eth1/33'),
                Service(item='eth1/34'),
                Service(item='eth1/1'),
                Service(item='eth1/2'),
                Service(item='eth1/3'),
                Service(item='eth1/4'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': True}),
                'matching_conditions': (True, {})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/033'),
                Service(item='eth1/034'),
                Service(item='eth1/001'),
                Service(item='eth1/002'),
                Service(item='eth1/003'),
                Service(item='eth1/004'),
            ),
        ),
        (
            {
                'discovery_single': (False, {}),
                'matching_conditions': (True, {})
            },
            L1_INTERFACES,
            tuple(),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_admin_states': ['2']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/34'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_admin_states': ['1']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/33'),
                Service(item='eth1/1'),
                Service(item='eth1/2'),
                Service(item='eth1/3'),
                Service(item='eth1/4'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_admin_states': ['2'], 'port_oper_states': ['2']})
            },
            L1_INTERFACES,
            tuple(),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_oper_states': ['1']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/33'),
                Service(item='eth1/34'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_oper_states': ['2']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/1'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_oper_states': ['0']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/2'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_oper_states': ['3']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/3'),
            ),
        ),
        (
            {
                'discovery_single': (True, {'pad_portnumbers': False}),
                'matching_conditions': (False, {'port_oper_states': ['4']})
            },
            L1_INTERFACES,
            (
                Service(item='eth1/4'),
            ),
        ),
    ],
)
def test_discover_aci_l1_phys_if(params: Dict, section: Dict[str, AciL1Interface], expected_services: Tuple) -> None:
    assert tuple(discover_aci_l1_phys_if(params, section)) == expected_services


@pytest.mark.parametrize(
    "item, result",
    [
        ('eth1/111', 'eth1/111'),
        ('eth1/107', 'eth1/107'),
        ('eth1/1', 'eth1/001'),
        ('eth1/10', 'eth1/010'),
        ('eth1/100', 'eth1/100'),
        ('eth1/3/67', 'eth1/3/067'),
        ('eth4/3/34/023/324/67', 'eth4/3/34/023/324/067'),
        ('eth0/0', 'eth0/000'),
        ('Ethernet3/100', 'Ethernet3/100'),
    ],
)
def test_interface_padding(item: str, result: str) -> None:
    assert pad_interface_id(item) == result
    assert unpad_interface_id(pad_interface_id(item)) == item
