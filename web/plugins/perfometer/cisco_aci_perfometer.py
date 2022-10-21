#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

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
Check_MK perfometer definitions for Cisco ACI checks

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from cmk.gui.plugins.metrics import perfometer_info

perfometer_info.append({
    "type": "linear",
    "segments": ["health"],
    "total": 100.0,
})

perfometer_info.append(
    {
        "type": "dual",
        "perfometers": [
            {
                "type": "logarithmic",
                "metric": "dom_rx_power",
                "half_value": 4,
                "exponent": 2,
            },
            {
                "type": "logarithmic",
                "metric": "dom_tx_power",
                "half_value": 4,
                "exponent": 2,
            },
        ],
    }
)

perfometer_info.append(
    {
        "type": "stacked",
        "perfometers": [
            {
                "type": "logarithmic",
                "metric": "fcs_errors",
                "half_value": 10,
                "exponent": 2,
            },
            {
                "type": "logarithmic",
                "metric": "stomped_crc_errors",
                "half_value": 10,
                "exponent": 2,
            },
        ],
    }
)
