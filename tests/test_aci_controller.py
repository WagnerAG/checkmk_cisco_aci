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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from plugins.cisco_aci.agent_based.aci_controller import (
    parse_aci_controller,
    check_aci_controller,
    ACIController,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            []
        ),
        (
            [["controller", "1", "APIC1", "in-service", "FCH1835V2FM", "APIC-SERVER-M1", "APIC-SERVER-M1"]],
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="in-service",
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    descr="APIC-SERVER-M1"
                )
            ]
        ),
        (
            [
                ["controller", "1", "APIC1", "degraded", "FCH1835V2FM", "APIC-SERVER-M1", "APIC-SERVER-M1"],
                ["controller", "2", "ACI01", "in-service", "FCH1935V1Z8", "APIC-SERVER-M2", "APIC-SERVER-M2"],
            ],
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="degraded",  # this might not be an official state
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    descr="APIC-SERVER-M1"
                ),
                ACIController(
                    controller_id="2",
                    name="ACI01",
                    status="in-service",
                    serial="FCH1935V1Z8",
                    model="APIC-SERVER-M2",
                    descr="APIC-SERVER-M2"
                ),
            ]
        ),
    ],
)
def test_parse_aci_controller(string_table: List[List[str]], expected_section: Dict[str, ACIController]) -> None:
    assert parse_aci_controller(string_table) == expected_section


ACI_GROUP_WITH_FAILED_HOST: List[ACIController] = [
    ACIController(
        controller_id="1",
        name="ACI01",
        status="failied",  # this might not be an official state
        serial="FCH1935V1Z3",
        model="APIC-SERVER-M2",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="2",
        name="ACI02",
        status="in-service",
        serial="FCH1935V1Z8",
        model="APIC-SERVER-M2",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="3",
        name="ACI03",
        status="in-service",
        serial="FCH1935V1U7",
        model="APIC-SERVER-M2",
        descr="APIC-SERVER-M2"
    ),
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
            "1",
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="in-service",
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    descr="APIC-SERVER-M1"
                ),
            ],
            (
                Result(
                    state=State.OK,
                    summary='APIC1 is in-service, Model: APIC-SERVER-M1, Serial: FCH1835V2FM'
                ),
            ),
        ),
        (
            "1",
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="degraed",  # this might not be an official state
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    descr="APIC-SERVER-M1"
                ),
            ],
            (
                Result(
                    state=State.CRIT,
                    summary='APIC1 is degraed, Model: APIC-SERVER-M1, Serial: FCH1835V2FM'
                ),
            ),
        ),
        (
            "2",
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="in-service",
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    descr="APIC-SERVER-M1"
                ),
                ACIController(
                    controller_id="2",
                    name="ACI01",
                    status="in-service",
                    serial="FCH1935V1Z8",
                    model="APIC-SERVER-M2",
                    descr="APIC-SERVER-M2"
                ),
            ],
            (
                Result(
                    state=State.OK,
                    summary='ACI01 is in-service, Model: APIC-SERVER-M2, Serial: FCH1935V1Z8'
                ),
            ),
        ),
        (
            "1",
            ACI_GROUP_WITH_FAILED_HOST,
            (
                Result(
                    state=State.CRIT,
                    summary='ACI01 is failied, Model: APIC-SERVER-M2, Serial: FCH1935V1Z3'
                ),
            ),
        ),
        (
            "3",
            ACI_GROUP_WITH_FAILED_HOST,
            (
                Result(
                    state=State.OK,
                    summary='ACI03 is in-service, Model: APIC-SERVER-M2, Serial: FCH1935V1U7'
                ),
            ),
        ),
    ],
)
def test_check_aci_controller_item(item: str, section: Dict[str, ACIController], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_controller(item, section)) == expected_check_result
