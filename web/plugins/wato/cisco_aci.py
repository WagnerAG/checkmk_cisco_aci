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
Nagios CMK Datasource Programm to check Cisco ACI

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Password,
    TextAscii,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware
from cmk.gui.plugins.wato import rulespec_registry, HostRulespec


def _valuespec_special_agents_cisco_aci():
    return Dictionary(
        title=_("Cisco ACI checks"),
        elements=[
            ('host', TextAscii(title=_('APIC IP, multiple IPs (Ctrls) accepted'))),
            ('user', TextAscii(title=_('ACI Username'))),
            ('password', Password(title=_('Password')))
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name='special_agents:cisco_aci',
        valuespec=_valuespec_special_agents_cisco_aci,
    )
)
