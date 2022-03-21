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

from typing import Tuple, List, Optional

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.aci_health import (
    parse_aci_health,
    check_aci_health,
    ACIHealthValues,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [['health', '99', '3', '28', '34', '95']],
            ACIHealthValues(99, 3, 28, 34, 95),
        ),
    ],
)
def test_parse_aci_health(string_table: List[List[str]], expected_section: ACIHealthValues) -> None:
    assert parse_aci_health(string_table) == expected_section


@pytest.mark.parametrize(
    "string_table",
    [
        (
            [
                ['health', '98', '2', '26', '35', '96'],
                ['health', '99', '3', '28', '34', '95'],
            ]
        ),
    ],
)
def test_invalid_parse_aci_health(string_table: List[List[str]]) -> None:
    with pytest.raises(ValueError) as exec_info:
        parse_aci_health(string_table)

    assert isinstance(exec_info.type(), ValueError)
    assert str(exec_info.value) == 'section must <<<aci_health>>> be a single line but is 2 lines'


# @pytest.mark.parametrize(
#     "section, expected_check_result",
#     [
#         (
#             None,
#             (
#                 Result(state=State.UNKNOWN, summary='Sorry - item not found'),
#             ),
#         ),
#         (
#             ACIHealthValues(),
#             (
#                 Result(state=State.OK, summary='Everyone seems to be running 3.0(1k)'),
#             ),
#         ),
#         (
#             ACIHealthValues(),
#             (
#                 Result(state=State.OK, summary='Everyone seems to be running 4.2(5n)'),
#             ),
#         ),
#         (
#             ACIHealthValues(),
#             (
#                 Result(state=State.WARN, summary='Multiple Versions detected: 3.0(1k), 4.2(5n)'),
#             ),
#         ),
#     ],
# )
# def test_check_aci_version(section: Optional[ACIHealthValues], expected_check_result: Tuple) -> None:
#     assert tuple(check_aci_health(section)) == expected_check_result
