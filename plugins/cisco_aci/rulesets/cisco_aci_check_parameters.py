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
Check_MK WATO rule spec for Cisco ACI checks

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    Float,
    DictElement,
    InputHint,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostAndItemCondition


def _form_spec_aci_l1_phys_if_levels():
    return Dictionary(
        title=Title("Configure Cisco ACI interface check parameters"),
        help_text=Help("To obtain the data required for this check, please configure" ' the datasource program "Cisco ACI".'),
        elements={
            "level_fcs_errors": DictElement(
                required=True,
                parameter_form=Dictionary(
                    title=Title("FCS error levels"),
                    help_text=Help("An alert will be raised if the error rate per minute " "exceeds the configured level."),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=InputHint(0.01),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=InputHint(1.0),
                            ),
                        ),
                    },
                ),
            ),
            "level_crc_errors": DictElement(
                required=True,
                parameter_form=Dictionary(
                    title=Title("CRC Errors levels"),
                    help_text=Help("An alert will be raised if the error rate per minute " "exceeds the configured level."),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=InputHint(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=InputHint(12.0),
                            ),
                        ),
                    },
                ),
            ),
            "level_stomped_crc_errors": DictElement(
                required=True,
                parameter_form=Dictionary(
                    title=Title("stomped CRC Errors levels"),
                    help_text=Help("An alert will be raised if the error rate per minute " "exceeds the configured level."),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=InputHint(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=InputHint(12.0),
                            ),
                        ),
                    },
                ),
            ),
        },
    )


rule_spec_aci_l1_phys_if_levels = CheckParameters(
    title=Title("Cisco ACI interface parameters"),
    name="aci_l1_phys_if_levels",
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(Title("Cisco ACI interface parameters")),
    parameter_form=_form_spec_aci_l1_phys_if_levels,
)


# def _parameter_valuespec_aci_health_levels():
#     return Dictionary(
#         help=_(
#             'To obtain the data required for this check, please configure'
#             ' the datasource program "Cisco ACI".'
#         ),
#         elements=[
#             (
#                 'health_levels',
#                 Tuple(
#                     title=_("Fabric Health Levels"),
#                     help=_(
#                         "An alert will be raised if the fabric health is lower than "
#                         "the configured level."
#                     ),
#                     elements=[
#                         Integer(
#                             title=_("Warning at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=95,
#                         ),
#                         Integer(
#                             title=_("Critical at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=85,
#                         ),
#                     ],
#                 ),
#             ),
#         ],
#     )


# rulespec_registry.register(
#     CheckParameterRulespecWithoutItem(
#         check_group_name="aci_health_levels",
#         group=RulespecGroupCheckParametersNetworking,
#         match_type="dict",
#         parameter_valuespec=_parameter_valuespec_aci_health_levels,
#         title=lambda: _("Cisco ACI Fabric Health Levels"),
#     )
# )


# def _parameter_valuespec_aci_health_levels():
#     return Dictionary(
#         help=_(
#             'To obtain the data required for this check, please configure'
#             ' the datasource program "Cisco ACI".'
#         ),
#         elements=[
#             (
#                 'health_levels',
#                 Tuple(
#                     title=_("Tenant Health Levels"),
#                     help=_(
#                         "An alert will be raised if the tenant health score is lower than "
#                         "the configured level."
#                     ),
#                     elements=[
#                         Integer(
#                             title=_("Warning at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=95,
#                         ),
#                         Integer(
#                             title=_("Critical at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=85,
#                         ),
#                     ],
#                 ),
#             ),
#         ],
#     )


# rulespec_registry.register(
#     CheckParameterRulespecWithItem(
#         check_group_name="aci_tenant_health_levels",
#         group=RulespecGroupCheckParametersNetworking,
#         item_spec=lambda: TextInput(title=_("Cisco ACI Tenant Health Levels")),
#         match_type="dict",
#         parameter_valuespec=_parameter_valuespec_aci_health_levels,
#         title=lambda: _("Cisco ACI Tenant Health Levels"),
#     )
# )


# def _parameter_valuespec_aci_node_levels():
#     return Dictionary(
#         help=_(
#             'To obtain the data required for this check, please configure'
#             ' the datasource program "Cisco ACI".'
#         ),
#         elements=[
#             (
#                 'health_levels',
#                 Tuple(
#                     title=_("Node Health Levels"),
#                     help=_(
#                         "An alert will be raised if the node health is lower than "
#                         "the configured level."
#                     ),
#                     elements=[
#                         Integer(
#                             title=_("Warning at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=95,
#                         ),
#                         Integer(
#                             title=_("Critical at"),
#                             minvalue=0,
#                             maxvalue=100,
#                             default_value=85,
#                         ),
#                     ],
#                 ),
#             ),
#         ],
#     )


# rulespec_registry.register(
#     CheckParameterRulespecWithItem(
#         check_group_name="aci_node_levels",
#         group=RulespecGroupCheckParametersNetworking,
#         item_spec=lambda: TextInput(title=_("Cisco ACI Node Health Levels")),
#         match_type="dict",
#         parameter_valuespec=_parameter_valuespec_aci_node_levels,
#         title=lambda: _("Cisco ACI Node Health Levels"),
#     )
# )


# def _parameter_valuespec_aci_bgp_peer_entry_levels():
#     return Dictionary(
#         help=_(
#             'To obtain the data required for this check, please configure'
#             ' the datasource program "Cisco ACI". By default we only alert'
#             ' on BGP connection drops.'
#         ),
#         elements=[
#             (
#                 'level_bgp_attempts',
#                 Tuple(
#                     title=_("BGP connection attempts per minute"),
#                     help=_(
#                         "An alert will be raised if there are more than the given "
#                         "amount of BGP connection attempts per minute."
#                     ),
#                     elements=[
#                         Float(
#                             title=_("Warning at"),
#                             minvalue=0.0,
#                             default_value=1.0,
#                         ),
#                         Float(
#                             title=_("Critical at"),
#                             minvalue=0.0,
#                             default_value=6.0,
#                         ),
#                     ],
#                 ),
#             ),
#             (
#                 'level_bgp_drop',
#                 Tuple(
#                     title=_("BGP connection drops per minute"),
#                     help=_(
#                         "An alert will be raised if there are more than the given "
#                         "amount of BGP connection drops per minute."
#                     ),
#                     elements=[
#                         Float(
#                             title=_("Warning at"),
#                             minvalue=0.0,
#                             default_value=1.0,
#                         ),
#                         Float(
#                             title=_("Critical at"),
#                             minvalue=0.0,
#                             default_value=6.0,
#                         ),
#                     ],
#                 ),
#             ),
#             (
#                 'level_bgp_est',
#                 Tuple(
#                     title=_("BGP connection establishments per minute"),
#                     help=_(
#                         "An alert will be raised if there are more than the given "
#                         "amount of BGP connection establishments per minute."
#                     ),
#                     elements=[
#                         Float(
#                             title=_("Warning at"),
#                             minvalue=0.0,
#                             default_value=1.0,
#                         ),
#                         Float(
#                             title=_("Critical at"),
#                             minvalue=0.0,
#                             default_value=6.0,
#                         ),
#                     ],
#                 ),
#             ),
#         ],
#     )


# rulespec_registry.register(
#     CheckParameterRulespecWithItem(
#         check_group_name="aci_bgp_peer_entry_levels",
#         group=RulespecGroupCheckParametersNetworking,
#         item_spec=lambda: TextInput(title=_("Cisco ACI BGP peer entry settings")),
#         match_type="dict",
#         parameter_valuespec=_parameter_valuespec_aci_bgp_peer_entry_levels,
#         title=lambda: _("Cisco ACI BGP peer entry settings"),
#     )
# )
