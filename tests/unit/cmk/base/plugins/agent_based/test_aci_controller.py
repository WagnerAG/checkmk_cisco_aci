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
from cmk.base.plugins.agent_based.aci_controller import (
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
            [["controller", "1", "APIC1", "in-service", "FCH1835V2FM", "APIC-SERVER-M1", "0", "0", "0", "0", "APIC-SERVER-M1"]],
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="in-service",
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M1"
                )
            ]
        ),
        (
            [
                ["controller", "1", "APIC1", "degraded", "FCH1835V2FM", "APIC-SERVER-M1", "0", "0", "0", "0", "APIC-SERVER-M1"],
                ["controller", "2", "ACI01", "in-service", "FCH1935V1Z8", "APIC-SERVER-M2", "0", "0", "0", "0", "APIC-SERVER-M2"],
            ],
            [
                ACIController(
                    controller_id="1",
                    name="APIC1",
                    status="degraded",  # this might not be an official state
                    serial="FCH1835V2FM",
                    model="APIC-SERVER-M1",
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M1"
                ),
                ACIController(
                    controller_id="2",
                    name="ACI01",
                    status="in-service",
                    serial="FCH1935V1Z8",
                    model="APIC-SERVER-M2",
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M2"
                ),
            ]
        ),
    ],
)
def test_parse_aci_controller(string_table: List[List[str]], expected_section: Dict[str, ACIController]) -> None:
    assert parse_aci_controller(string_table) == expected_section


ACI_GROUP_WITH_CRIT_HOST: List[ACIController] = [
    ACIController(
        controller_id="1",
        name="ACI01",
        status="failied",  # this might not be an official state
        serial="FCH1935V1Z3",
        model="APIC-SERVER-M2",
        fault_crit="0",
        fault_maj="1",
        fault_minor="0",
        fault_warn="0",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="2",
        name="ACI02",
        status="in-service",
        serial="FCH1935V1Z8",
        model="APIC-SERVER-M2",
        fault_crit="1",
        fault_maj="1",
        fault_minor="0",
        fault_warn="0",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="3",
        name="ACI03",
        status="in-service",
        serial="FCH1935V1U7",
        model="APIC-SERVER-M2",
        fault_crit="0",
        fault_maj="0",
        fault_minor="0",
        fault_warn="0",
        descr="APIC-SERVER-M2"
    ),
]


ACI_GROUP_WITH_WARN_HOST: List[ACIController] = [
    ACIController(
        controller_id="1",
        name="ACI01",
        status="in-service",
        serial="FCH1935V1Z3",
        model="APIC-SERVER-M2",
        fault_crit="0",
        fault_maj="0",
        fault_minor="1",
        fault_warn="0",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="2",
        name="ACI02",
        status="in-service",
        serial="FCH1935V1Z8",
        model="APIC-SERVER-M2",
        fault_crit="0",
        fault_maj="0",
        fault_minor="1",
        fault_warn="1",
        descr="APIC-SERVER-M2"
    ),
    ACIController(
        controller_id="3",
        name="ACI03",
        status="in-service",
        serial="FCH1935V1U7",
        model="APIC-SERVER-M2",
        fault_crit="-1",
        fault_maj="0",
        fault_minor="0",
        fault_warn="0",
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
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M1"
                ),
            ],
            (
                Result(
                    state=State.OK,
                    summary='APIC1 is in-service, Unacknowledged Faults: 0, Model: APIC-SERVER-M1, Serial: FCH1835V2FM'
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
                    fault_crit="1",
                    fault_maj="1",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M1"
                ),
            ],
            (
                Result(
                    state=State.CRIT,
                    summary='APIC1 is degraed, Unacknowledged Faults: 2, Model: APIC-SERVER-M1, Serial: FCH1835V2FM',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: 1\n                    - Maj: 1\n                    - Minor: 0\n                    - Warning: 0\n                '
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
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M1"
                ),
                ACIController(
                    controller_id="2",
                    name="ACI01",
                    status="in-service",
                    serial="FCH1935V1Z8",
                    model="APIC-SERVER-M2",
                    fault_crit="0",
                    fault_maj="0",
                    fault_minor="0",
                    fault_warn="0",
                    descr="APIC-SERVER-M2"
                ),
            ],
            (
                Result(
                    state=State.OK,
                    summary='ACI01 is in-service, Unacknowledged Faults: 0, Model: APIC-SERVER-M2, Serial: FCH1935V1Z8'
                ),
            ),
        ),
        (
            "1",
            ACI_GROUP_WITH_CRIT_HOST,
            (
                Result(
                    state=State.CRIT,
                    summary='ACI01 is failied, Unacknowledged Faults: 1, Model: APIC-SERVER-M2, Serial: FCH1935V1Z3',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: 0\n                    - Maj: 1\n                    - Minor: 0\n                    - Warning: 0\n                '
                ),
            ),
        ),
        (
            "2",
            ACI_GROUP_WITH_CRIT_HOST,
            (
                Result(
                    state=State.CRIT,
                    summary='ACI02 is in-service, Unacknowledged Faults: 2, Model: APIC-SERVER-M2, Serial: FCH1935V1Z8',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: 1\n                    - Maj: 1\n                    - Minor: 0\n                    - Warning: 0\n                '
                ),
            ),
        ),
        (
            "3",
            ACI_GROUP_WITH_CRIT_HOST,
            (
                Result(
                    state=State.OK,
                    summary='ACI03 is in-service, Unacknowledged Faults: 0, Model: APIC-SERVER-M2, Serial: FCH1935V1U7',
                ),
            ),
        ),
        (
            "1",
            ACI_GROUP_WITH_WARN_HOST,
            (
                Result(
                    state=State.WARN,
                    summary='ACI01 is in-service, Unacknowledged Faults: 1, Model: APIC-SERVER-M2, Serial: FCH1935V1Z3',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: 0\n                    - Maj: 0\n                    - Minor: 1\n                    - Warning: 0\n                '
                ),
            ),
        ),
        (
            "2",
            ACI_GROUP_WITH_WARN_HOST,
            (
                Result(
                    state=State.WARN,
                    summary='ACI02 is in-service, Unacknowledged Faults: 2, Model: APIC-SERVER-M2, Serial: FCH1935V1Z8',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: 0\n                    - Maj: 0\n                    - Minor: 1\n                    - Warning: 1\n                '
                ),
            ),
        ),
        (
            "3",
            ACI_GROUP_WITH_WARN_HOST,
            (
                Result(
                    state=State.WARN,
                    summary='ACI03 is in-service, Unacknowledged Faults: got negative number, Model: APIC-SERVER-M2, Serial: FCH1935V1U7',
                    details='\n                    Unacknowledged APIC Faults:\n                    - Crit: -1\n                    - Maj: 0\n                    - Minor: 0\n                    - Warning: 0\n                \nThe difference between “faults - faultsAcknowledged” results in a negative number for one of the error categories crit/maj/minor/warn.\nThis means that there are probably "stale faults" on the APIC, which are output via the API but are not visible in the GUI.\nPlease investigate and correct the errors.'
                ),
            ),
        ),
    ],
)
def test_check_aci_controller_item(item: str, section: Dict[str, ACIController], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_controller(item, section)) == expected_check_result
