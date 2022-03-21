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
Check_MK Checks to use with aci-ds Datasource
Place into local check-mk checks directory, e.g ~/local/share/check_mk/checks in OMD

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""

from __future__ import annotations
from typing import List, NamedTuple

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
)


class ACINodeVersion(NamedTuple):
    name: str
    version: str


def parse_aci_version(string_table) -> List[ACINodeVersion]:
    """
    Example output:
        node-3 3.0(1k)
        node-104 n9000-13.0(1k)

        node-2 4.2(5n)
        node-101 n9000-14.2(5n)
    """
    return [ACINodeVersion(node_name, version) for node_name, version in string_table]


register.agent_section(
    name='aci_version',
    parse_function=parse_aci_version,
)


def discover_aci_version(section: List[ACINodeVersion]) -> DiscoveryResult:
    yield Service()


def check_aci_version(section: List[ACINodeVersion]) -> CheckResult:
    versions = set()

    for node in section:
        # get only last 7 characters of version number to compare vresions of controllers with leaf-switches
        versions.add(node.version[-7:])

    if not versions:
        yield Result(state=State.UNKNOWN, summary='Sorry - item not found')
    elif len(versions) == 1:
        yield Result(state=State.OK, summary=f'Everyone seems to be running {min(versions)}')
    else:
        yield Result(state=State.WARN, summary=f'Multiple Versions detected: {", ".join(sorted(versions))}')


register.check_plugin(
    name='aci_version',
    service_name='Fabric Versions',
    discovery_function=discover_aci_version,
    check_function=check_aci_version,
)
