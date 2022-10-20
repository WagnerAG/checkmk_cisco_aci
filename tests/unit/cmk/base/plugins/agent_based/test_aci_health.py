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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from cmk.base.plugins.agent_based.aci_health import (
    parse_aci_health,
    check_aci_health,
    ACIHealthValues,
    DEFAULT_HEALTH_LEVELS,
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


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            ACIHealthValues(99, 3, 28, 34, 95),
            (
                Result(state=State.OK, summary='Fabric Health Score: 99.00'),
                Metric('health', 99.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 3/28/34/95'),
                Metric("fcrit", 3.0),
                Metric("fwarn", 28.0),
                Metric("fmaj", 34.0),
                Metric("fmin", 95.0),
            ),
        ),
        (
            ACIHealthValues(95, 5, 40, 28, 101),
            (
                Result(state=State.OK, summary='Fabric Health Score: 95.00'),
                Metric('health', 95.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 5/40/28/101'),
                Metric("fcrit", 5.0),
                Metric("fwarn", 40.0),
                Metric("fmaj", 28.0),
                Metric("fmin", 101.0),
            ),
        ),
        (
            ACIHealthValues(94, 5, 40, 28, 101),
            (
                Result(state=State.WARN, summary='Fabric Health Score: 94.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 94.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 5/40/28/101'),
                Metric("fcrit", 5.0),
                Metric("fwarn", 40.0),
                Metric("fmaj", 28.0),
                Metric("fmin", 101.0),
            ),
        ),
        (
            ACIHealthValues(85, 7, 45, 28, 101),
            (
                Result(state=State.WARN, summary='Fabric Health Score: 85.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 85.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 7/45/28/101'),
                Metric("fcrit", 7.0),
                Metric("fwarn", 45.0),
                Metric("fmaj", 28.0),
                Metric("fmin", 101.0),
            ),
        ),
        (
            ACIHealthValues(84, 7, 45, 28, 204),
            (
                Result(state=State.CRIT, summary='Fabric Health Score: 84.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 84.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 7/45/28/204'),
                Metric("fcrit", 7.0),
                Metric("fwarn", 45.0),
                Metric("fmaj", 28.0),
                Metric("fmin", 204.0),
            ),
        ),
        (
            ACIHealthValues(63, 12, 61, 39, 1008),
            (
                Result(state=State.CRIT, summary='Fabric Health Score: 63.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 63.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Fabric-wide Faults (crit/warn/maj/min): 12/61/39/1008'),
                Metric("fcrit", 12.0),
                Metric("fwarn", 61.0),
                Metric("fmaj", 39.0),
                Metric("fmin", 1008.0),
            ),
        ),
    ],
)
def test_check_aci_health(section: Optional[ACIHealthValues], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_health(DEFAULT_HEALTH_LEVELS, section)) == expected_check_result
