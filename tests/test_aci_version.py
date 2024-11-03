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
from plugins.cisco_aci.agent_based.aci_version import (
    parse_aci_version,
    check_aci_version,
    ACINodeVersion,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [["node-2", "4.2(5n)"]],
            [ACINodeVersion(name="node-2", version="4.2(5n)")]
        ),
        (
            [
                ['node-1', '4.2(5n)'],
                ['node-3', '4.2(5n)'],
                ['node-2', '4.2(5n)'],
                ['node-101', 'n9000-14.2(5n)'],
                ['node-113', 'n9000-14.2(5n)'],
                ['node-102', 'n9000-14.2(5n)'],
                ['node-201', 'n9000-14.2(5n)'],
                ['node-211', 'n9000-14.2(5n)'],
                ['node-213', 'n9000-14.2(5n)'],
                ['node-202', 'n9000-14.2(5n)'],
                ['node-212', 'n9000-14.2(5n)'],
                ['node-214', 'n9000-14.2(5n)'],
                ['node-111', 'n9000-14.2(5n)'],
                ['node-112', 'n9000-14.2(5n)'],
                ['node-114', 'n9000-14.2(5n)'],
            ],
            [
                ACINodeVersion(name='node-1', version='4.2(5n)'),
                ACINodeVersion(name='node-3', version='4.2(5n)'),
                ACINodeVersion(name='node-2', version='4.2(5n)'),
                ACINodeVersion(name='node-101', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-113', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-102', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-201', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-211', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-213', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-202', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-212', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-214', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-111', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-112', version='n9000-14.2(5n)'),
                ACINodeVersion(name='node-114', version='n9000-14.2(5n)'),
            ]
        ),
    ],
)
def test_parse_aci_version(string_table: List[List[str]], expected_section: List[ACINodeVersion]) -> None:
    assert parse_aci_version(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            [],
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
        (
            [
                ACINodeVersion(name="node-3", version="3.0(1k)"),
            ],
            (
                Result(state=State.OK, summary='Everyone seems to be running 3.0(1k)'),
            ),
        ),
        (
            [
                ACINodeVersion(name='node-2', version='4.2(5n)'),
                ACINodeVersion(name='node-101', version='n9000-14.2(5n)'),
            ],
            (
                Result(state=State.OK, summary='Everyone seems to be running 4.2(5n)'),
            ),
        ),
        (
            [
                ACINodeVersion(name='node-2', version='4.2(5n)'),
                ACINodeVersion(name="node-3", version="3.0(1k)"),
            ],
            (
                Result(state=State.WARN, summary='Multiple Versions detected: 3.0(1k), 4.2(5n)'),
            ),
        ),
    ],
)
def test_check_aci_version(section: List[ACINodeVersion], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_version(section)) == expected_check_result
