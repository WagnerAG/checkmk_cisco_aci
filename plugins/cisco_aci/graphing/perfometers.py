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

"""
Perfometer definitions for Cisco ACI
"""

from cmk.graphing.v1.perfometers import (
    Perfometer,
    Bidirectional,
    Stacked,
    FocusRange,
    Closed,
    Open,
)


perfometer_cisco_aci_health = Perfometer(
    name="health",
    focus_range=FocusRange(lower=Closed(0), upper=Closed(100)),
    segments=["health"],
)


perfometer_cisco_aci_dom_power = Stacked(
    name="dom_power",
    lower=Perfometer(
        name="dom_rx_power",
        focus_range=FocusRange(lower=Open(-4), upper=Open(0)),
        segments=["dom_rx_power"],
    ),
    upper=Perfometer(
        name="dom_tx_power",
        focus_range=FocusRange(lower=Open(-4), upper=Open(0)),
        segments=["dom_tx_power"],
    ),
)


perfometer_cisco_aci_l1_errors = Bidirectional(
    name="l1_errors",
    left=Perfometer(
        name='fcs_errors',
        focus_range=FocusRange(lower=Closed(0), upper=Open(+10)),
        segments=['fcs_errors'],
    ),
    right=Perfometer(
        name='stomped_crc_errors',
        focus_range=FocusRange(lower=Closed(0), upper=Open(+10)),
        segments=['stomped_crc_errors'],
    ),
)

