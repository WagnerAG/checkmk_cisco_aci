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
Graph definitions for Cisco ACI
"""

from cmk.graphing.v1 import metrics, Title

COUNT = metrics.Unit(metrics.DecimalNotation(""))

metric_cisco_aci_health = metrics.Metric(
    name="health",
    title=Title("Health score"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.GREEN,
)

metric_cisco_aci_dom_rx_power = metrics.Metric(
    name="dom_rx_power",
    title=Title("DOM RX Power"),
    unit=metrics.Unit(metrics.DecimalNotation("dbm")),
    color=metrics.Color.DARK_YELLOW,
)

metric_cisco_aci_dom_tx_power = metrics.Metric(
    name="dom_tx_power",
    title=Title("DOM TX Power"),
    unit=metrics.Unit(metrics.DecimalNotation("dbm")),
    color=metrics.Color.LIGHT_YELLOW,
)

metric_cisco_aci_fcs_errors = metrics.Metric(
    name="fcs_errors",
    title=Title("FCS errors"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.RED,
)

metric_cisco_aci_crc_errors = metrics.Metric(
    name="crc_errors",
    title=Title("CRC errors"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.DARK_RED,
)

metric_cisco_aci_stomped_crc_errors = metrics.Metric(
    name="stomped_crc_errors",
    title=Title("Stomped CRC errors"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.LIGHT_RED,
)

metric_cisco_aci_bgp_conn_attempts = metrics.Metric(
    name="bgp_conn_attempts",
    title=Title("BGP connection attempts"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.PURPLE,
)

metric_cisco_aci_bgp_conn_drop = metrics.Metric(
    name="bgp_conn_drop",
    title=Title("BGP connection drops"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.DARK_BLUE,
)

metric_cisco_aci_bgp_conn_est = metrics.Metric(
    name="bgp_conn_est",
    title=Title("BGP connection establishments"),
    unit=metrics.Unit(COUNT),
    color=metrics.Color.BLUE,
)
