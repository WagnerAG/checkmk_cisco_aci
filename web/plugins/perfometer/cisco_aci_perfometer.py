#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
Cisco ACI perfometer definitions
Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>
"""

from cmk.gui.plugins.metrics import perfometer_info

perfometer_info.append({
    "type": "linear",
    "segments": ["health"],
    "total": 100.0,
})

perfometer_info.append({
    "type": "logarithmic",
    "metric": "dom_rx_power",
    "half_value": 4,
    "exponent": 2,
})

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
