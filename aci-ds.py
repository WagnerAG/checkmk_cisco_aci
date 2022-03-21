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
Nagios CMK Datasource Programm to check Cisco ACI

Authors:    Samuel Zehnder, zehnder@netcloud.ch
            Roger Ellenberger, roger.ellenberger@wagner.ch
Version:    0.6

"""
from typing import Dict, Optional

import time
import json
import requests
import argparse

requests.packages.urllib3.disable_warnings()

MAX_RETRIES = 3
SLEEP_SECONDS = 3

VERSION=0.6
NAME="aci-ds"


def get_args():
    """Args Parsing..."""

    parser = argparse.ArgumentParser(description='Nagios ACI Check Scripts',
                                     epilog='Example: python %(prog)s -H apic-1 apic-2 -u admin -p password')

    parser.add_argument('-v', '--debug', action='store_true', help='Set Logging to Debug')
    parser.add_argument('-H', '--host', nargs='+', required=True, help='APIC IP, multiple IPs (Ctrls) accepted')
    parser.add_argument('-u', '--user', required=True, help='ACI Username')
    parser.add_argument('-p', '--password', required=True, help='ACI Password')

    try:
        return parser.parse_args()
    except (argparse.ArgumentError, argparse.ArgumentTypeError):
        parser.print_help()
        exit(1)


def _login(url, user, pwd) -> requests.Session:
    """APIC Login"""

    creds = {"aaaUser": {"attributes": {"name": user, "pwd": pwd}}}

    counter = 1
    s = requests.Session()
    response = s.post(url + "aaaLogin.json", data=json.dumps(creds), verify=False, timeout=2.000)

    while response.status_code == requests.codes.unauthorized:
        if counter > MAX_RETRIES:
            raise requests.HTTPError(json.loads(response.text)["imdata"][0]["error"]["attributes"]["text"])
        time.sleep(SLEEP_SECONDS)
        response = s.post(url + "aaaLogin.json", data=json.dumps(creds), verify=False, timeout=2.000)
        counter += 1

    response.raise_for_status()

    return s


def _get_if_name_from_dn(dn):
    name = dn.split('[')[1]
    name = name.split(']')[0]
    return name


def get_aci_health(session, url):
    """Get Fabric Health Score"""

    url += "node/mo/topology/health.json"
    response = session.get(url)
    health_data = json.loads(response.text)
    response.raise_for_status()

    health_score = health_data["imdata"][0]["fabricHealthTotal"]["attributes"]["cur"]

    return int(health_score)


def get_nodes(session, url) -> Dict:
    response = session.get(url + 'node/class/topSystem.json?query-target=self&rsp-subtree=children&rsp-subtree-class=eqptCh&rsp-subtree-include=health')
    response.raise_for_status()
    nodes = response.json()['imdata']
    nodelist = dict(spine=[], leaf=[], controller=[])

    for node in nodes:
        health = ""
        model = "unknown"
        descr = ""
        name = node['topSystem']['attributes']['name']
        role = node['topSystem']['attributes']['role']
        state = node['topSystem']['attributes']['state']
        serial = node['topSystem']['attributes']['serial']
        node_id = node['topSystem']['attributes']['id']

        for child in node['topSystem']['children']:
            if 'healthInst' in child:
                health = child['healthInst']['attributes']['cur']
            if 'eqptCh' in child:
                descr = child['eqptCh']['attributes']['descr']
                model = child['eqptCh']['attributes']['model']

        nodelist[role].append((role, node_id, name, state, health, serial, model, descr))

    return nodelist


def get_faults(session, url):
    response = session.get(url + 'node/mo/fltCnts.json')
    response.raise_for_status()
    faults = response.json()['imdata'][0]['faultCountsWithDetails']['attributes']
    return faults['crit'], faults['warn'], faults['maj'], faults['minor']


def get_versions(session, url):
    response = session.get(url + 'node/class/firmwareCtrlrRunning.json')
    response.raise_for_status()
    versions = response.json()['imdata']

    running = []
    for version in versions:
        ctrl_id = version['firmwareCtrlrRunning']['attributes']['dn'].split('/')[2]
        version = version['firmwareCtrlrRunning']['attributes']['version']
        running.append((ctrl_id, version))

    response = session.get(url + 'node/class/firmwareRunning.json')
    response.raise_for_status()
    versions = response.json()['imdata']
    for version in versions:
        node_id = version['firmwareRunning']['attributes']['dn'].split('/')[2]
        version = version['firmwareRunning']['attributes']['version']
        running.append((node_id, version))

    return running



def print_agent_output(url, session):
    print('<<<check_mk>>>')
    print(f'Version: {NAME}-{VERSION}')
    print('AgentOS: Cisco ACI')

    print('<<<aci_version>>>')
    versions = get_versions(session, url)
    for node, version in versions:
        print(f'{node}, {version}')

    print('<<<aci_health>>>')
    health_score = get_aci_health(session, url)
    print(f'health {health_score} {" ".join(get_faults(session, url))}')

    all_nodes = get_nodes(session, url)
    for ntype, nodes in all_nodes.items():
        print('<<<aci_{0}>>>'.format(ntype))
        for node in nodes:
            print(' '.join(node))


def handle_error(current_host: int, num_hosts: int, desc: str, exit_code: int, error: Optional[Exception]):
    if (current_host >= num_hosts):
        print(desc)
        if error :
            print(error)
        exit(exit_code)


def main():
    args = get_args()
    num_hosts = len(args.host)

    for i, host in enumerate(args.host, start=1):
        url = f'https://{host}/api/'
        try:
            session = _login(url, args.user, args.password)
            break
        except requests.exceptions.ConnectionError as e:
            handle_error(current_host=i, num_hosts=num_hosts, desc='Could not reach APIC (!!)', error=e, exit_code=2)

        except requests.HTTPError as e:
            handle_error(current_host=i, num_hosts=num_hosts, desc=f'Could not login to ACI, Error: {e.message}', exit_code=3)
            
        except Exception as e:
            handle_error(current_host=i, num_hosts=num_hosts, desc=f'Error occurred!', exit_code=3, error=e)

    print_agent_output(url, session)


if __name__ == "__main__":
    main()
