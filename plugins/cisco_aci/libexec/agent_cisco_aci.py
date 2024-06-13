#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
'''call for special agent function'''

# License: GNU General Public License v2

import sys
from special_agents.agent_cisco_aci import agent_cisco_aci_main

if __name__ == "__main__":
    sys.exit(agent_cisco_aci_main())