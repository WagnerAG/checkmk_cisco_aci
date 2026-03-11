#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import CascadingSingleChoice, CascadingSingleChoiceElement, DefaultValue, DictElement, Dictionary, FixedValue, MultipleChoice, MultipleChoiceElement, SingleChoice, SingleChoiceElement
from cmk.rulesets.v1.form_specs.validators import ValidationError
from cmk.rulesets.v1.rule_specs import DiscoveryParameters, Topic


def _vs_single_discovery() -> CascadingSingleChoice:
    return CascadingSingleChoice(
        title=Title("Configure discovery of single interfaces"),
        elements=[
            CascadingSingleChoiceElement(
                name="enabled",
                title=Title("Discover single interfaces"),
                parameter_form=Dictionary(
                    elements={
                        "pad_portnumbers": DictElement(
                            parameter_form=SingleChoice(
                                elements=[
                                    SingleChoiceElement(name="no", title=Title("Do not pad")),
                                    SingleChoiceElement(name="yes", title=Title("Pad port numbers with zeros")),
                                ],
                                title=Title("Port numbers"),
                                help_text=Help(
                                    "If this option is activated, checkmk will pad port numbers of network "
                                    "interfaces with zeroes so that the descriptions of all ports of a host "
                                    "or switch have the same length and thus are sorted correctly in the GUI."
                                ),
                                prefill=DefaultValue("no"),
                            ),
                        ),
                        "long_if_name": DictElement(
                            parameter_form=SingleChoice(
                                elements=[
                                    SingleChoiceElement(name="yes", title=Title("Use long interface name")),
                                    SingleChoiceElement(name="no", title=Title("Use short interface name")),
                                ],
                                title=Title("Interface name"),
                                help_text=Help(
                                    "If this option is activated, checkmk will reformat the network interface "
                                    "name from the short name 'eth' to a long representation 'Ethernet', so the "
                                    "sorting in the view with other checks like 'if64' (SNMP) or 'aci_l1_phys_if' "
                                    "is consistent."
                                ),
                                prefill=DefaultValue("no"),
                            ),
                        ),
                        "labels": DictElement(
                            required=False,
                            parameter_form=Dictionary(
                                title=Title("Generate service labels for discovered interfaces"),
                                help_text=Help("Create service labels that get discovered by this rule. Add key-value pairs as dictionary elements."),
                                elements={},
                            ),
                        ),
                    },
                ),
            ),
            CascadingSingleChoiceElement(
                name="disabled",
                title=Title("Do not discover single interfaces"),
                parameter_form=FixedValue(value=None),
            ),
        ],
        prefill=DefaultValue("enabled"),
    )


def _admin_states() -> list[MultipleChoiceElement]:
    """admin state according APIC docs:
    /doc/html/TYPE-l1-AdminSt.html
    """
    return [
        MultipleChoiceElement(name="admin_up", title=Title("up")),
        MultipleChoiceElement(name="admin_down", title=Title("down")),
    ]


def _oper_states() -> list[MultipleChoiceElement]:
    """operational state according APIC docs:
    /doc/html/TYPE-l1-OperSt.html
    """
    return [
        MultipleChoiceElement(name="oper_unknown", title=Title("unknown")),
        MultipleChoiceElement(name="oper_down", title=Title("down")),
        MultipleChoiceElement(name="oper_up", title=Title("up")),
        MultipleChoiceElement(name="oper_link_up", title=Title("link-up")),
        MultipleChoiceElement(name="oper_channel_admin_down", title=Title("channel-admin-down")),  # port channel admin down
    ]


def _vs_matching_conditions() -> CascadingSingleChoice:
    return CascadingSingleChoice(
        title=Title("Conditions for this rule to apply"),
        help_text=Help(
            "Here, you can define conditions for applying this rule. These conditions are evaluated "
            "on a per-interface basis. When discovering an interface, checkmk will first find all "
            "rules whose conditions match this interface. Then, these rules are merged together, "
            "whereby rules from subfolders overwrite rules from the main directory. Within a "
            "directory, the order of the rules matters, i.e., rules further below in the list are "
            "overwritten by rules further up."
        ),
        elements=[
            CascadingSingleChoiceElement(
                name="match_all",
                title=Title("Match all interfaces"),
                parameter_form=FixedValue(value=None),
            ),
            CascadingSingleChoiceElement(
                name="match_conditions",
                title=Title("Specify matching conditions"),
                parameter_form=Dictionary(
                    elements={
                        "port_oper_states": DictElement(
                            required=False,
                            parameter_form=MultipleChoice(
                                elements=_oper_states(),
                                title=Title("Match port states"),
                                help_text=Help("Apply this rule only to interfaces whose port state is listed below."),
                                prefill=DefaultValue(["oper_up"]),
                            ),
                        ),
                        "port_admin_states": DictElement(
                            required=False,
                            parameter_form=MultipleChoice(
                                elements=_admin_states(),
                                title=Title("Match admin states"),
                                help_text=Help("Apply this rule only to interfaces whose admin state (<tt>ifAdminStatus</tt>) is listed below."),
                                prefill=DefaultValue(["admin_up"]),
                            ),
                        ),
                    },
                ),
            ),
        ],
        prefill=DefaultValue("match_all"),
    )


def _validate_inventory_if_rules(value: Mapping[str, object]) -> None:
    """Validate that at least one discovery option is configured."""
    if "discovery_single" not in value and "grouping" not in value:
        raise ValidationError(
            "Please configure at least either the discovery of single interfaces or the grouping"
        )


def _valuespec_inventory_if_rules() -> Dictionary:
    return Dictionary(
        title=Title("Cisco ACI interface and switch port discovery"),
        help_text=Help(
            "Configure the discovery of services monitoring network interfaces and switch "
            "ports. Note that this rule is a somewhat special case compared to most other "
            "rules in checkmk. Usually, the conditions for applying a rule are configured "
            "exclusively below in the section 'Conditions'. However, here, you can define "
            "additional conditions using the options offered by 'Conditions for this rule to "
            "apply'. These conditions are evaluated on a per-interface basis and allow for "
            "configuring the discovery of the corresponding services very finely. For example, "
            "you can make checkmk discover only interfaces whose alias matches the regex 'eth' "
            "or exclude certain port types or states from being discovered. Note that saving a "
            "rule which has only conditions specified is not allowed and will result in an "
            "error. The reason is that such a rule would have no effect."
        ),
        elements={
            "discovery_single": DictElement(
                required=False,
                parameter_form=_vs_single_discovery(),
            ),
            "matching_conditions": DictElement(
                required=False,
                parameter_form=_vs_matching_conditions(),
            ),
        },
        custom_validate=(_validate_inventory_if_rules,),
    )


rule_spec_discovery_aci_if = DiscoveryParameters(
    title=Title("Cisco ACI interface and switch port discovery"),
    topic=Topic.NETWORKING,
    name="cisco_aci_if_discovery",
    parameter_form=_valuespec_inventory_if_rules,
)
