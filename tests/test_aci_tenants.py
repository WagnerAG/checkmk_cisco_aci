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

from typing import Tuple, List, Dict

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from plugins.cisco_aci.agent_based.aci_tenants import (
    parse_aci_tenants,
    check_aci_tenants,
    ACITenant,
    DEFAULT_HEALTH_LEVELS,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                ['#name', 'descr', 'dn', 'health_score'],
                ['infra', '', 'uni/tn-infra', '100'],
            ],
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
            },
        ),
        (
            [
                ['infra', '', 'uni/tn-infra', '100'],
                ['mgmt', '', 'uni/tn-mgmt', '84'],
                ['common', '', 'uni/tn-common', '94'],
                ['LAB', 'Management Tenant', 'uni/tn-LAB', '96'],
            ],
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
                'mgmt': ACITenant('mgmt', '', 'uni/tn-mgmt', 84),
                'common': ACITenant('common', '', 'uni/tn-common', 94),
                'LAB': ACITenant('LAB', 'Management Tenant', 'uni/tn-LAB', 96),
            },
        ),
    ],
)
def test_parse_aci_tenants(string_table: List[List[str]], expected_section: Dict[str, ACITenant]) -> None:
    assert parse_aci_tenants(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            'foo',
            {},
            (
                Result(state=State.UNKNOWN, summary='Sorry - item not found'),
            ),
        ),
        (
            'infra',
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
                'mgmt': ACITenant('mgmt', '', 'uni/tn-mgmt', 84),
                'common': ACITenant('common', '', 'uni/tn-common', 94),
                'LAB': ACITenant('LAB', 'Management Tenant', 'uni/tn-LAB', 96),
            },
            (
                Result(state=State.OK, summary='Health Score: 100.00'),
                Metric('health', 100.0, boundaries=(0.0, 100.0)),
            ),
        ),
        (
            'mgmt',
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
                'mgmt': ACITenant('mgmt', '', 'uni/tn-mgmt', 84),
                'common': ACITenant('common', '', 'uni/tn-common', 94),
                'LAB': ACITenant('LAB', 'Management Tenant', 'uni/tn-LAB', 96),
            },
            (
                Result(state=State.CRIT, summary='Health Score: 84.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 84.0, boundaries=(0.0, 100.0)),
            ),
        ),
        (
            'common',
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
                'mgmt': ACITenant('mgmt', '', 'uni/tn-mgmt', 84),
                'common': ACITenant('common', '', 'uni/tn-common', 94),
                'LAB': ACITenant('LAB', 'Management Tenant', 'uni/tn-LAB', 96),
            },
            (
                Result(state=State.WARN, summary='Health Score: 94.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 94.0, boundaries=(0.0, 100.0)),
            ),
        ),
        (
            'cust1',
            {
                'cust1': ACITenant('cust1', '', 'uni/tn-cust1', 86),
            },
            (
                Result(state=State.WARN, summary='Health Score: 86.00 (warn/crit below 95.00/85.00)'),
                Metric('health', 86.0, boundaries=(0.0, 100.0)),
            ),
        ),
        (
            'LAB',
            {
                'infra': ACITenant('infra', '', 'uni/tn-infra', 100),
                'mgmt': ACITenant('mgmt', '', 'uni/tn-mgmt', 84),
                'common': ACITenant('common', '', 'uni/tn-common', 94),
                'LAB': ACITenant('LAB', 'Management Tenant', 'uni/tn-LAB', 96),
            },
            (
                Result(state=State.OK, summary='Health Score: 96.00'),
                Metric('health', 96.0, boundaries=(0.0, 100.0)),
                Result(state=State.OK, summary='Description: Management Tenant'),
            ),
        ),
    ],
)
def test_check_aci_tenants(item: str, section: Dict[str, ACITenant], expected_check_result: Tuple) -> None:
    assert tuple(check_aci_tenants(item, DEFAULT_HEALTH_LEVELS, section)) == expected_check_result
