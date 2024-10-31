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
Check_MK agent based checks to be used with agent_cisco_aci Datasource

Authors:    Samuel Zehnder <zehnder@netcloud.ch>
            Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from cmk.agent_based.v2 import AgentSection, CheckPlugin
from .aci_node import (
    parse_aci_node,
    discover_aci_node,
    check_aci_node,
    DEFAULT_HEALTH_LEVELS,
)


agent_section_aci_spine = AgentSection(
    name="aci_spine",
    parse_function=parse_aci_node,
)


check_plugin_aci_spine = CheckPlugin(
    name="aci_spine",
    service_name="Spine %s",
    discovery_function=discover_aci_node,
    check_function=check_aci_node,
    check_ruleset_name="aci_node_levels",
    check_default_parameters=DEFAULT_HEALTH_LEVELS,
)