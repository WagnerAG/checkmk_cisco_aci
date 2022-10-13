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
Version:    0.7

"""

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    ListOfStrings,
    Checkbox,  # this may be renamed to Boolean in the future accordinig a comment in source code
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware


def _valuespec_special_agents_cisco_aci():
    return Dictionary(
        title=_("Cisco ACI"),
        elements=[
            (
                'host',
                ListOfStrings(
                    title=_('APIC IP address(es)'),
                    orientation="vertical",
                    help=_('multiple Controller IPs are accepted'),
                    allow_empty=False,
                )
            ),
            (
                'dns-domain',
                TextInput(
                    title=_('DNS domain (for piggyback)'),
                    help=_('This value is appended to each piggyback host. Use it in case hosts in Check MK use fqdn'),
                    allow_empty=True,
                )
            ),
            (
                'user',
                TextInput(
                    title=_('ACI Username'),
                    allow_empty=False,
                )
            ),
            (
                'password',
                IndividualOrStoredPassword(
                    title=_('Password'),
                    allow_empty=False,
                )
            ),
            (
                'only-iface-admin-up',
                Checkbox(
                    title=_('Monitor only interfaces with adminState "up"'),
                    default_value=True,
                )
            ),
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
