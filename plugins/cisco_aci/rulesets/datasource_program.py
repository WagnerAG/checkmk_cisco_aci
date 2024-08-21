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
Check_MK WATO rule spec for Cisco ACI special agent

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from typing import Final

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    Dictionary,
    MultipleChoiceElement,
    MultipleChoice,
    Password,
    String,
    DictElement,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


RAW_ACI_Features: Final = [
    MultipleChoiceElement(name="aci_bgp_peer_entry", title=Title("ACI BGP Peer entry")),
    MultipleChoiceElement(name="aci_fault_inst", title=Title("ACI Fault instance")),
    MultipleChoiceElement(name="aci_l1_phys_if", title=Title("ACI Layer 1 Physical Interfaces")),
    MultipleChoiceElement(name="aci_dom_pwr_stats", title=Title("ACI DOM Power Stats")),
]


def _valuespec_special_agent_cisco_aci() -> Dictionary:
    return Dictionary(
        title=Title("Cisco ACI"),
        help_text=Help("Checking Cisco ACI"),
        elements={
            "host": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("APIC IP address(es)"),
                    help_text=Help("Multiple Controller IPs are accepted"),
                    #custom_validate=(validators.MatchRegex('\b(?:\d{1,3}\.){3}\d{1,3}\b')),
                ),
            ),
            "user": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("ACI Username"),
                    help_text=Help("Use the Cisco local user noation in following format. apic#LOCAL\\cmk"),
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Password"),
                    #migrate=migrate_to_password,
                ),
            ),
            "dns_domain": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("DNS domain (for piggyback)"),
                    help_text=Help("If you set this setting only ports with adminstate up are getting discovered."),
                ),
            ),
            "only_iface_admin_up": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    title=Title("Discover only interfaces with admin up state"),
                    help_text=Help("Discovers only Interfaces who are not admin down."),
                ),
            ),
            "skip_sections": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Agent sections to be skipped"),
                    elements=RAW_ACI_Features,
                ),
            ),
        },
    )


rule_spec_cisco_aci = SpecialAgent(
    name="cisco_aci",
    title=Title("Cisco ACI"),
    help_text=Help("This rule selects the Agent Cisco ACI instead of the normal Check_MK Agent "
                   "which collects the data through the Cisco ACI REST API"
                   "The Cisco ACI special agent needs a local user in form (local\checkmk_monitoring)"),
    topic=Topic.NETWORKING,
    parameter_form=_valuespec_special_agent_cisco_aci,
)
