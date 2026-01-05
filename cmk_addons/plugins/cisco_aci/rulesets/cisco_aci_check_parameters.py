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
    Integer,
    Float,
    DictElement,
    DefaultValue,
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
                                prefill=DefaultValue(0.01),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(1.0),
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
                                prefill=DefaultValue(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(12.0),
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
                                prefill=DefaultValue(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(12.0),
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


def _form_spec_aci_health_levels():
    return Dictionary(
        title=Title("Configure Cisco ACI health check parameters"),
        help_text=Help(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI".'
        ),
        elements={
            'health_levels': DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Tenant Health Levels"),
                    help_text=Help(
                        "An alert will be raised if the tenant health score is lower than "
                        "the configured level."
                    ),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Integer(
                                title=Title("Warning at"),
                                prefill=DefaultValue(95),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Integer(
                                title=Title("Critical at"),
                                prefill=DefaultValue(85),
                            ),
                        ),
                    },
                ),
            ),
        },
    )


rule_spec_aci_health_levels = CheckParameters(
    title=Title("Cisco ACI Health Levels"),
    name="aci_health_levels",
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(Title("Cisco ACI health parameters")),
    parameter_form=_form_spec_aci_health_levels,
)


rule_spec_aci_tenant_health_levels = CheckParameters(
    title=Title("Cisco ACI Tenant Health Levels"),
    name="aci_tenant_health_levels",
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(Title("Cisco ACI tenant health parameters")),
    parameter_form=_form_spec_aci_health_levels,
)


def _form_spec_aci_bgp_peer_entry_levels():
    return Dictionary(
        title=Title('Configure Cisco ACI BGP peer check parameters'),
        help_text=Help(
            'To obtain the data required for this check, please configure'
            ' the datasource program "Cisco ACI". By default we only alert'
            ' on BGP connection drops.'
        ),
        elements={
            'level_bgp_attempts': DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("BGP connection attempts per minute"),
                    help_text=Help(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection attempts per minute."
                    ),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=DefaultValue(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(6.0),
                            ),
                        ),
                    },
                ),
            ),
            'level_bgp_drop': DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("BGP connection drops per minute"),
                    help_text=Help(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection drops per minute."
                    ),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=DefaultValue(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(6.0),
                            ),
                        ),
                    },
                ),
            ),
            'level_bgp_est': DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("BGP connection establishments per minute"),
                    help_text=Help(
                        "An alert will be raised if there are more than the given "
                        "amount of BGP connection establishments per minute."
                    ),
                    elements={
                        "warn": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Warning at"),
                                prefill=DefaultValue(1.0),
                            ),
                        ),
                        "crit": DictElement(
                            required=True,
                            parameter_form=Float(
                                title=Title("Critical at"),
                                prefill=DefaultValue(6.0),
                            ),
                        ),
                    },
                ),
            ),
        },
    )


rule_spec_aci_bgp_peer_entry_levels = CheckParameters(
    title=Title("Cisco ACI BGP peer entry settings"),
    name="aci_bgp_peer_entry_levels",
    topic=Topic.NETWORKING,
    condition=HostAndItemCondition(Title("Cisco ACI BGP peer entry settings")),
    parameter_form=_form_spec_aci_bgp_peer_entry_levels,
)
