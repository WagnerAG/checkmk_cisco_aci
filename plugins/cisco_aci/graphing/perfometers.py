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

from cmk.graphing.v1 import perfometers


#
perfometer_cisco_aci_health = perfometers.Perfometer(
    name="health",
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed(100)),
    segments=("health",)
)

#
perfometer_cisco_aci_dom_power = perfometers.Bidirectional(
    name="dom_power",
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed(100)),
    segments=("dom_rx_power", "dom_tx_power")
)

#
perfometer_cisco_aci_fcs_errors = perfometers.Stacked(
    name="fcs_errors",
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed(100)),
    segments=("dom_rx_power", "dom_tx_power")
)


#perfometer_info.append(
#    {
#        "type": "dual",
#        "perfometers": [
#            {
#                "type": "logarithmic",
#                "metric": "dom_rx_power",
#                "half_value": 4,
#                "exponent": 2,
#            },
#            {
#                "type": "logarithmic",
#                "metric": "dom_tx_power",
#                "half_value": 4,
#                "exponent": 2,
#            },
#        ],
#    }
#)
#
#perfometer_info.append(
#    {
#        "type": "stacked",
#        "perfometers": [
#            {
#                "type": "logarithmic",
#                "metric": "fcs_errors",
#                "half_value": 10,
#                "exponent": 2,
#            },
#            {
#                "type": "logarithmic",
#                "metric": "stomped_crc_errors",
#                "half_value": 10,
#                "exponent": 2,
#            },
#        ],
#    }
#)
#