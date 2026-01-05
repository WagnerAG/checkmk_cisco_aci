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
CMK Datasource Programm to check Cisco ACI

Authors:    Samuel Zehnder <zehnder@netcloud.ch>
            Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from collections.abc import Iterable

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)

"""
Validator class to validate all the params
"""


class ACIParams(BaseModel):
    host: str
    user: str
    password: Secret
    dns_domain: str | None = None
    only_iface_admin_up: bool | None = None
    skip_sections: list | None = None


# def _parse_secret(secret: Object) -> Secret:
#    if not isinstance(secret, Secret):
#        raise TypeError()
#    return secret
#


def generate_cisco_aci_command(params: ACIParams, host_config: HostConfig) -> Iterable[SpecialAgentCommand]:
    """function to build command line arguments that will be used to
    invoke the special agent.
    """

    args: list[str | Secret] = []
    args.append("--user")
    args.append(params.user)
    args.append("--password")
    args.append(params.password.unsafe())

    if params.dns_domain is not None:
        args.append("--dns-domain")
        args.append(params.dns_domain)

    if params.only_iface_admin_up:
        args.append("--only-iface-admin-up")

    if params.skip_sections:
        if "aci_bgp_peer_entry" in params.skip_sections:
            args.append("--skip-bgp-peer-entry")
        if "aci_fault_inst" in params.skip_sections:
            args.append("--skip-fault-inst")
        if "aci_l1_phys_if" in params.skip_sections:
            args.append("--skip-l1-phys-if")
        if "aci_dom_pwr_stats" in params.skip_sections:
            args.append("--skip-dom-pwr-stats")

    args.append("--host")
    args.append(params.host)

    yield SpecialAgentCommand(command_arguments=args)


special_agent_cisco_aci = SpecialAgentConfig(
    name="cisco_aci",
    parameter_parser=ACIParams.model_validate,
    commands_function=generate_cisco_aci_command,
)
