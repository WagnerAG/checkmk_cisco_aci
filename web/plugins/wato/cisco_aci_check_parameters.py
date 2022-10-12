#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
WATO Rulespec for check parameters for Cisco ACI checks
Author:     Roger Ellenberger <roger.ellenberger@wagner.ch>
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)
from cmk.gui.valuespec import (
    Dictionary,
    Float,
    TextInput,
    Tuple,
)


def _parameter_valuespec_nc_coriant_psus():
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
        parameter_valuespec=_parameter_valuespec_nc_coriant_psus,
        title=lambda: _("Cisco ACI interface parameters"),
    )
)
