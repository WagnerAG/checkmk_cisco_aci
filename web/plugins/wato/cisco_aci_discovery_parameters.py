#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Dict, Union
from cmk.gui.exceptions import MKUserError
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
    RulespecGroupCheckParametersDiscovery,
)
from cmk.gui.valuespec import (
    CascadingDropdown,
    Dictionary,
    DropdownChoice,
    FixedValue,
    Labels,
    ListChoice,
)


def _vs_single_discovery():
    return CascadingDropdown(
        title=_("Configure discovery of single interfaces"),
        choices=[
            (
                True,
                _("Discover single interfaces"),
                Dictionary(
                    elements=[
                        (
                            "pad_portnumbers",
                            DropdownChoice(
                                choices=[
                                    (False, _("Do not pad")),
                                    (True, _("Pad port numbers with zeros")),
                                ],
                                title=_("Port numbers"),
                                help=_(
                                    "If this option is activated, checkmk will pad port numbers of "
                                    "network interfaces with zeroes so that the descriptions of all "
                                    "ports of a host or switch have the same length and thus are "
                                    "sorted correctly in the GUI."
                                ),
                            ),
                        ),
                        (
                            "long_if_name",
                            DropdownChoice(
                                choices=[
                                    (True, _("Use long interface name")),
                                    (False, _("Use short interface name")),
                                ],
                                title=_("Interface name"),
                                help=_(
                                    "If this option is activated, checkmk will reformat the "
                                    "network interface name from the short name 'eth' to a long "
                                    "representation 'Ethernet', so the sorting in the view with "
                                    "other checks like 'if64' (SNMP) or 'aci_l1_phys_if' is "
                                    "consistent."
                                ),
                            ),
                        ),
                        (
                            "labels",
                            Labels(
                                world=Labels.World.CONFIG,
                                label_source=Labels.Source.RULESET,
                                help=_("Create service labels that get discovered by this rule."),
                                title=_("Generate service labels for discovered interfaces"),
                            ),
                        ),
                    ],
                    optional_keys=["labels"],
                ),
            ),
            (
                False,
                _("Do not discover single interfaces"),
                FixedValue(
                    value={},
                    totext="",
                ),
            ),
        ],
        sorted=False,
    )


def _admin_states():
    """admin state according APIC docs:
    /doc/html/TYPE-l1-AdminSt.html
    """
    return {
        1: _("up"),
        2: _("down"),
    }


def _oper_states() -> Dict[Union[str, int], str]:
    """operational state according APIC docs:
    /doc/html/TYPE-l1-OperSt.html
    """
    return {
        0: _("unknown"),
        1: _("down"),
        2: _("up"),
        3: _("link-up"),
        4: _("channel-admin-down"),  # port channel admin down
    }


def _vs_matching_conditions():
    return CascadingDropdown(
        title=_("Conditions for this rule to apply"),
        help=_(
            "Here, you can define conditions for applying this rule. These conditions are evaluated "
            "on a per-interface basis. When discovering an interface, checkmk will first find all "
            "rules whose conditions match this interface. Then, these rules are merged together, "
            "whereby rules from subfolders overwrite rules from the main directory. Within a "
            "directory, the order of the rules matters, i.e., rules further below in the list are "
            "overwritten by rules further up."
        ),
        choices=[
            (
                True,
                _("Match all interfaces"),
                FixedValue(
                    value={},
                    totext="",
                ),
            ),
            (
                False,
                _("Specify matching conditions"),
                Dictionary(
                    elements=[
                        (
                            "port_oper_states",
                            ListChoice(
                                title=_("Match port states"),
                                help=_(
                                    "Apply this rule only to interfaces whose port state is listed "
                                    "below."
                                ),
                                choices=_oper_states(),
                                toggle_all=True,
                                default_value=["2"],
                            ),
                        ),
                        (
                            "port_admin_states",
                            ListChoice(
                                title=_("Match admin states"),
                                help=(
                                    "Apply this rule only to interfaces whose admin state "
                                    "(<tt>ifAdminStatus</tt>) is listed below."
                                ),
                                choices=_admin_states(),
                                toggle_all=True,
                                default_value=["1"],
                            ),
                        ),
                    ],
                ),
            ),
        ],
        sorted=False,
    )


def _validate_valuespec_inventory_if_rules(value, varprefix):
    if "grouping" not in value and "discovery_single" not in value:
        raise MKUserError(
            varprefix,
            _(
                "Please configure at least either the discovery of single interfaces or the grouping"
            ),
        )


def _valuespec_inventory_if_rules() -> Dictionary:
    return Dictionary(
        title=_("Cisco ACI interface and switch port discovery"),
        help=_(
            "Configure the discovery of services monitoring network interfaces and switch "
            "ports. Note that this rule is a somewhat special case compared to most other "
            "rules in checkmk. Usually, the conditions for applying a rule are configured "
            "exclusively below in the section 'Conditions'. However, here, you can define "
            "additional conditions using the options offered by 'Conditions for this rule to "
            "apply'. These conditions are evaluated on a per-interface basis and allow for "
            "configuring the discovery of the corresponding services very finely. For example, "
            "you can make checkmk discover only interfaces whose alias matches the regex 'eth' "
            "or exclude certain port types or states from being discoverd. Note that saving a "
            "rule which has only conditions specified is not allowed and will result in an "
            "error. The reason is that such a rule would have no effect."
        ),
        elements=[
            (
                "discovery_single",
                _vs_single_discovery(),
            ),
            (
                "matching_conditions",
                _vs_matching_conditions(),
            ),
        ],
        optional_keys=[],
        default_keys=[],
        validate=_validate_valuespec_inventory_if_rules,
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="all",
        name="cisco_aci_if_discovery",
        valuespec=_valuespec_inventory_if_rules,
    )
)
