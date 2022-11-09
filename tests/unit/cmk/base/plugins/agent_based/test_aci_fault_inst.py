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
from cmk.base.plugins.agent_based.aci_fault_inst import (
    parse_aci_fault_inst,
    check_aci_fault_inst,
    ACIFaultInst,
)


SECTION_1 = [
    ACIFaultInst('major', 'F0103', 'Physical Interface eth1/2 on Node 1 of fabric LAB-1 with hostname lab-aci-1 is now down', 'topology/pod-1/node-1/sys/cphys-[eth1/2]/fault-F0103', 'no'),
]
SECTION_2 = [
    ACIFaultInst('major', 'F0103', 'Physical Interface eth1/2 on Node 1 of fabric LAB-1 with hostname lab-aci-1 is now down', 'topology/pod-1/node-1/sys/cphys-[eth1/2]/fault-F0103', 'no'),
    ACIFaultInst('minor', 'F1298', 'For tenant mgmt, management profile default, deployment of in-band EPG INB failed on node 999. Reason Node Cannot Deploy EPG', 'foo/epp/inb-[foo/tn-mgmt/mgmtp-default/inb-INB]/node-999/polDelSt/fault-F1298', 'no'),
    ACIFaultInst('warning', 'F0299', 'BGP peer is not established, current state Idle', 'topology/pod-1/node-111/sys/bgp/inst/dom-FOO:DMZ/peer-[10.79.7.40/32]/ent-[10.79.7.40]/fault-F0299', 'yes'),
    ACIFaultInst('critical', 'F0532', 'Port is down, reason being sfpAbsent(connected), used by EPG on node 111 of fabric LAB-1 with hostname lab-aci-1', 'topology/pod-1/node-111/sys/phys-[eth1/7]/phys/fault-F0532', 'no'),
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
                ['#severity', 'code', 'descr', 'dn', 'ack'],
                ['major', 'F0103', 'Physical Interface eth1/2 on Node 1 of fabric LAB-1 with hostname lab-aci-1 is now down', 'topology/pod-1/node-1/sys/cphys-[eth1/2]/fault-F0103', 'no'],
            ],
            SECTION_1,
        ),
        (
            [
                # shall also work without a header row
                ['major', 'F0103', 'Physical Interface eth1/2 on Node 1 of fabric LAB-1 with hostname lab-aci-1 is now down', 'topology/pod-1/node-1/sys/cphys-[eth1/2]/fault-F0103', 'no'],
                ['minor', 'F1298', 'For tenant mgmt, management profile default, deployment of in-band EPG INB failed on node 999. Reason Node Cannot Deploy EPG', 'foo/epp/inb-[foo/tn-mgmt/mgmtp-default/inb-INB]/node-999/polDelSt/fault-F1298', 'no'],
                ['warning', 'F0299', 'BGP peer is not established, current state Idle', 'topology/pod-1/node-111/sys/bgp/inst/dom-FOO:DMZ/peer-[10.79.7.40/32]/ent-[10.79.7.40]/fault-F0299', 'yes'],
                ['critical', 'F0532', 'Port is down, reason being sfpAbsent(connected), used by EPG on node 111 of fabric LAB-1 with hostname lab-aci-1', 'topology/pod-1/node-111/sys/phys-[eth1/7]/phys/fault-F0532', 'no'],
            ],
            SECTION_2,
        ),
    ],
)
def test_parse_aci_fault_inst(string_table: List[List[str]], expected_section: List[ACIFaultInst]) -> None:
    assert parse_aci_fault_inst(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            [],
            (
                Result(state=State.OK, summary="0 major alarms, 0 minor alarms, 0 warnings, 0 cleared alarms"),
            ),
        ),
        (
            SECTION_1,
            (
                Result(state=State.OK, summary="1 major alarms, 0 minor alarms, 0 warnings, 0 cleared alarms"),
            )
        ),
        (
            SECTION_2,
            (
                Result(state=State.CRIT, summary='Critical unacknowledged error: Port is down, reason being sfpAbsent(connected), used by EPG on node 111 of fabric LAB-1 with hostname lab-aci-1'),
                Result(state=State.OK, summary="1 major alarms, 1 minor alarms, 1 warnings, 0 cleared alarms"),
            )
        ),
    ],
)
def test_check_aci_fault_inst(section: List[ACIFaultInst], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_fault_inst(section)) == expected_check_result
