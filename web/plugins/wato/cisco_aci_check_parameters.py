#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
WATO Rulespec for check parameters for Cisco ACI checks
Author:     Roger Ellenberger <roger.ellenberger@wagner.ch>
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)
from cmk.gui.valuespec import (
    Dictionary,
    Float,
    Integer,
    TextInput,
    Tuple,
)


def _parameter_valuespec_aci_l1_phys_if_levels():
    return Dictionary(
        help=_(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI".'
        ),
        elements=[
            (
                "level_fcs_errors",
                Tuple(
                    title=_("Alert Levels for FCS Errors"),
                    help=_(
                        "An alert will be raised if the error rate per minute "
                        "exceeds the configured level."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            default_value=0.01,
                        ),
                        Float(
                            title=_("Critical at"),
                            default_value=1.0,
                        ),
                    ],
                ),
            ),
            (
                "level_crc_errors",
                Tuple(
                    title=_("Alert Levels for CRC Errors"),
                    help=_(
                        "An alert will be raised if the error rate per minute "
                        "exceeds the configured level."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            default_value=1.0,
                        ),
                        Float(
                            title=_("Critical at"),
                            default_value=12.0,
                        ),
                    ],
                ),
            ),
            (
                "level_stomped_crc_errors",
                Tuple(
                    title=_("Alert Levels for stomped CRC Errors"),
                    help=_(
                        "An alert will be raised if the error rate per minute "
                        "exceeds the configured level."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            default_value=1.0,
                        ),
                        Float(
                            title=_("Critical at"),
                            default_value=12.0,
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="aci_l1_phys_if_levels",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("Cisco ACI interface parameters")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_aci_l1_phys_if_levels,
        title=lambda: _("Cisco ACI interface parameters"),
    )
)


def _parameter_valuespec_aci_health_levels():
    return Dictionary(
        help=_(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI".'
        ),
        elements=[
            (
                'health_levels',
                Tuple(
                    title=_("Fabric Health Levels"),
                    help=_(
                        "An alert will be raised if the fabric health is lower than "
                        "the configured level."
                    ),
                    elements=[
                        Integer(
                            title=_("Warning at"),
                            minvalue=0,
                            maxvalue=100,
                            default_value=95,
                        ),
                        Integer(
                            title=_("Critical at"),
                            minvalue=0,
                            maxvalue=100,
                            default_value=85,
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="aci_health_levels",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_aci_health_levels,
        title=lambda: _("Cisco ACI Fabric Health Levels"),
    )
)


def _parameter_valuespec_aci_node_levels():
    return Dictionary(
        help=_(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI".'
        ),
        elements=[
            (
                'health_levels',
                Tuple(
                    title=_("Node Health Levels"),
                    help=_(
                        "An alert will be raised if the node health is lower than "
                        "the configured level."
                    ),
                    elements=[
                        Integer(
                            title=_("Warning at"),
                            minvalue=0,
                            maxvalue=100,
                            default_value=95,
                        ),
                        Integer(
                            title=_("Critical at"),
                            minvalue=0,
                            maxvalue=100,
                            default_value=85,
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="aci_node_levels",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("Cisco ACI Node Health Levels")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_aci_node_levels,
        title=lambda: _("Cisco ACI Node Health Levels"),
    )
)


def _parameter_valuespec_aci_bgp_peer_entry_levels():
    return Dictionary(
        help=_(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI". By default we only alert'
            ' on BGP connection drops.'
        ),
        elements=[
            (
                'level_bgp_attempts',
                Tuple(
                    title=_("BGP connection attempts per minute"),
                    help=_(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection attempts per minute."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            minvalue=0.0,
                            default_value=1.0,
                        ),
                        Float(
                            title=_("Critical at"),
                            minvalue=0.0,
                            default_value=6.0,
                        ),
                    ],
                ),
            ),
            (
                'level_bgp_drop',
                Tuple(
                    title=_("BGP connection drops per minute"),
                    help=_(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection drops per minute."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            minvalue=0.0,
                            default_value=1.0,
                        ),
                        Float(
                            title=_("Critical at"),
                            minvalue=0.0,
                            default_value=6.0,
                        ),
                    ],
                ),
            ),
            (
                'level_bgp_est',
                Tuple(
                    title=_("BGP connection establishments per minute"),
                    help=_(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection establishments per minute."
                    ),
                    elements=[
                        Float(
                            title=_("Warning at"),
                            minvalue=0.0,
                            default_value=1.0,
                        ),
                        Float(
                            title=_("Critical at"),
                            minvalue=0.0,
                            default_value=6.0,
                        ),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="aci_bgp_peer_entry_levels",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("Cisco ACI BGP peer entry settings")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_aci_bgp_peer_entry_levels,
        title=lambda: _("Cisco ACI BGP peer entry settings"),
    )
)
