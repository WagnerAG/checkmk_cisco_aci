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
Check_MK metric definitions for Cisco ACI checks

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info

metric_info["health"] = {
    "title": _("Health score"),
    "unit": "count",
    "color": "34/a",
}

metric_info["dom_rx_power"] = {
    "title": _("DOM RX Power"),
    "unit": "dbm",
    "color": "31/a",
}

metric_info["dom_tx_power"] = {
    "title": _("DOM TX Power"),
    "unit": "dbm",
    "color": "26/a",
}

metric_info["fcs_errors"] = {
    "title": _("FCS errors"),
    "unit": "count",
    "color": "14/a",
}

metric_info["crc_errors"] = {
    "title": _("CRC errors"),
    "unit": "count",
    "color": "16/a",
}

metric_info["stomped_crc_errors"] = {
    "title": _("stomped CRC errors"),
    "unit": "count",
    "color": "21/a",
}

metric_info["bgp_conn_attempts"] = {
    "title": _("BGP connection attempts"),
    "unit": "count",
    "color": "46/a",
}

metric_info["bgp_conn_drop"] = {
    "title": _("BGP connection drops"),
    "unit": "count",
    "color": "45/a",
}

metric_info["bgp_conn_est"] = {
    "title": _("BGP connection establishments"),
    "unit": "count",
    "color": "44/a",
}
