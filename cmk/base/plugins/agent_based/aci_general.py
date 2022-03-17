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

from enum import Enum, unique

aci_health_default_values = (95, 85)


@unique
class ACIHealthLevels(Enum):
    WARN: int = 95
    CRIT: int = 85


def inventory_aci_node(info):
    # controller 1 APIC1 in-service  FCH1835V2FM APIC-SERVER-M1 APIC-SERVER-M1
    for line in info:
        nnid = line[1]
        yield nnid, "aci_health_default_values"


def check_aci_switch(item, params, info):
    # spine 201 ACI-SPINE-201 in-service 100 SAL18391DWK N9K-C9336PQ Nexus9000 C9336PQ Chassis

    state = 3
    msg = 'Sorry - item not found'
    perfdata = []

    for line in info:
        if line[1] == item:
            break
    else:
        return state, msg

    check, nnid, name, status, health, serial, model = line[:7]
    state = 0

    warn, crit = params
    if int(health) < crit:
        state = 2
        msg += "(!!)"
    elif int(health) < warn:
        msg += "(!)"
        state = 1

    msg = '{0} is {1}, Health:{2}, Model: {3}, Serial {4}'.format(name, status, health, model, serial)

    return state, msg, [("health", health, warn, crit, None, 100)]
