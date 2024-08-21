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
Check_MK agent based checks to be used with agent_cisco_aci Datasource

Authors:    Roger Ellenberger <roger.ellenberger@wagner.ch>

"""

from __future__ import annotations
from typing import Dict, NamedTuple

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    check_levels,
    Result,
    Service,
    State,
)


DEFAULT_HEALTH_LEVELS: Dict = {"health_levels": (95, 85)}


class ACITenant(NamedTuple):
    name: str
    descr: str
    dn: str
    health_score: int

    @staticmethod
    def from_string_table_line(line) -> ACITenant:
        name, descr, dn, health_score = line

        return ACITenant(name, descr, dn, int(health_score))


def parse_aci_tenants(string_table) -> Dict[str, ACITenant]:
    """
    Example output:
        <<<aci_tenants:sep(124)>>>
        #name|descr|dn|health_score
        infra||uni/tn-infra|100
        mgmt||uni/tn-mgmt|100
        common||uni/tn-common|100
        LAB|Management Tenant|uni/tn-LAB|98
    """
    return {line[0]: ACITenant.from_string_table_line(line) for line in string_table if not line[0].startswith("#")}


register.agent_section(
    name="aci_tenants",
    parse_function=parse_aci_tenants,
)


def discover_aci_tenants(section: Dict[str, ACITenant]) -> DiscoveryResult:
    for tenant in section:
        yield Service(item=tenant)


def check_aci_tenants(item: str, params: Dict, section: Dict[str, ACITenant]) -> CheckResult:
    tenant = section.get(item)
    if not tenant:
        yield Result(state=State.UNKNOWN, summary="Sorry - item not found")
        return

    yield from check_levels(
        tenant.health_score,
        levels_lower=params.get("health_levels"),
        boundaries=(0, 100),
        metric_name="health",
        label="Health Score",
    )

    if tenant.descr:
        yield Result(state=State.OK, summary=f"Description: {tenant.descr}")


register.check_plugin(
    name="aci_tenants",
    service_name="Tenant %s",
    discovery_function=discover_aci_tenants,
    check_function=check_aci_tenants,
    check_ruleset_name="aci_tenant_health_levels",
    check_default_parameters=DEFAULT_HEALTH_LEVELS,
)
