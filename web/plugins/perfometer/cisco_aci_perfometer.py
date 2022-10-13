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
