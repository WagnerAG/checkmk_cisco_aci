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
from plugins.cisco_aci.agent_based.aci_node import (
    parse_aci_node,
    check_aci_node,
    ACINode,
    DEFAULT_HEALTH_LEVELS,
)


ACI_TEST_NODES: List[ACINode] = [
    ACINode(nnid='101', name='spine101', status='downgraded', health=84, serial='FEO33101F5G', model='N9K-C9336PQ'),
    ACINode(nnid='201', name='spine201', status='in-service', health=95, serial='FEO33101F5F', model='N9K-C9336PQ'),
    ACINode(nnid='202', name='spine202', status='in-service', health=94, serial='FEO33101F5E', model='N9K-C9336PQ'),
    ACINode(nnid='203', name='spine203', status='in-service', health=85, serial='FEO33101F5B', model='N9K-C9336PQ'),
]


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        # ACI spine
        (
            [
                ['spine', '201', 'spine201', 'in-service', '95', 'FEO33101F5G', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
            ],
            [
                ACINode(nnid='201', name='spine201', status='in-service', health=95,
                        serial='FEO33101F5G', model='N9K-C9336PQ'),
            ],
        ),
        (
            [
                ['spine', '101', 'spine101', 'downgraded', '84', 'FEO33101F5G', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
                ['spine', '201', 'spine201', 'in-service', '95', 'FEO33101F5F', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
                ['spine', '202', 'spine202', 'in-service', '94', 'FEO33101F5E', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
                ['spine', '203', 'spine203', 'in-service', '85', 'FEO33101F5B', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
            ],
            ACI_TEST_NODES,
        ),
        # ACI leaf
        (
            [
                ['leaf', '311', 'leaf311', 'in-service', '100', 'FCO140610VJ', 'N9K-C93180YC-EX',
                    'Nexus', 'C93180YC-EX', 'Chassis'],
            ],
            [
                ACINode(nnid='311', name='leaf311', status='in-service', health=100,
                        serial='FCO140610VJ', model='N9K-C93180YC-EX'),
            ],
        ),
    ],
)
def test_parse_aci_node(string_table: List[List[str]], expected_section: List[ACINode]) -> None:
    assert parse_aci_node(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "",
            [],
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
        (
            '201',
            ACI_TEST_NODES,
            (
                Result(state=State.OK, summary='Node Health Score: 95.00'),
                Metric('health', 95.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='spine201 is in-service, Model: N9K-C9336PQ, Serial: FEO33101F5F'),
            ),
        ),
        (
            '202',
            ACI_TEST_NODES,
            (
                Result(state=State.WARN, summary='Node Health Score: 94.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 94.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='spine202 is in-service, Model: N9K-C9336PQ, Serial: FEO33101F5E'),
            ),
        ),
        (
            '203',
            ACI_TEST_NODES,
            (
                Result(state=State.WARN, summary='Node Health Score: 85.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 85.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='spine203 is in-service, Model: N9K-C9336PQ, Serial: FEO33101F5B'),
            ),
        ),
        (
            '101',
            ACI_TEST_NODES,
            (
                Result(state=State.CRIT, summary='Node Health Score: 84.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 84.0, boundaries=(0.0, 100.0)),
                Result(state=State.CRIT, summary='spine101 is downgraded, Model: N9K-C9336PQ, Serial: FEO33101F5G'),
            ),
        ),
        (
            '999',
            ACI_TEST_NODES,
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
    ],
)
def test_check_aci_node(item: str, section: List[ACINode], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_node(item, DEFAULT_HEALTH_LEVELS, section)) == expected_check_result
