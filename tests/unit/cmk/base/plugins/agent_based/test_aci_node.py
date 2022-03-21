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
from cmk.base.plugins.agent_based.aci_node import (
    parse_aci_node,
    check_aci_node,
    ACINode,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            # ACI spine
            [
                ['spine', '201', 'spine201', 'in-service', '95', 'FEO33101F5G', 'N9K-C9336PQ',
                 'Nexus9000', '1-Slot', 'Spine Chassis'],
            ],
            [
                ACINode(nnid='201', name='spine201', status='in-service', health=95,
                        serial='FEO33101F5G', model='N9K-C9336PQ'),
            ],
        ),
    ],
)
def test_parse_aci_node(string_table: List[List[str]], expected_section: List[ACINode]) -> None:
    assert parse_aci_node(string_table) == expected_section


ACI_TEST_NODES: List[ACINode] = [
    ACINode(nnid='101', name='spine101', status='in-service', health=84, serial='FEO33101F5G', model='N9K-C9336PQ'),
    ACINode(nnid='201', name='spine201', status='in-service', health=95, serial='FEO33101F5F', model='N9K-C9336PQ'),
    ACINode(nnid='202', name='spine202', status='in-service', health=94, serial='FEO33101F5E', model='N9K-C9336PQ'),
    ACINode(nnid='203', name='spine203', status='in-service', health=85, serial='FEO33101F5B', model='N9K-C9336PQ'),
]


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
                Result(state=State.OK, summary='spine201 is in-service, Health:95, Model: N9K-C9336PQ, Serial FEO33101F5F'),
                Metric("health", 95.0, levels=(95.0, 85.0), boundaries=(0.0, 100.0)),
            ),
        ),
        (
            '202',
            ACI_TEST_NODES,
            (
                Result(state=State.WARN, summary='spine202 is in-service, Health:94, Model: N9K-C9336PQ, Serial FEO33101F5E'),
                Metric("health", 94.0, levels=(95.0, 85.0), boundaries=(0.0, 100.0)),
            ),
        ),
        (
            '203',
            ACI_TEST_NODES,
            (
                Result(state=State.WARN, summary='spine203 is in-service, Health:85, Model: N9K-C9336PQ, Serial FEO33101F5B'),
                Metric("health", 85.0, levels=(95.0, 85.0), boundaries=(0.0, 100.0)),
            ),
        ),
        (
            '101',
            ACI_TEST_NODES,
            (
                Result(state=State.CRIT, summary='spine101 is in-service, Health:84, Model: N9K-C9336PQ, Serial FEO33101F5G'),
                Metric("health", 84.0, levels=(95.0, 85.0), boundaries=(0.0, 100.0)),
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
    assert tuple(check_aci_node(item, section)) == expected_check_result
