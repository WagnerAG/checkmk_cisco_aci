# Checkmk extension for Cisco ACI

![build](https://github.com/ellr/checkmk_cisco_aci/workflows/build/badge.svg)
![flake8](https://github.com/ellr/checkmk_cisco_aci/workflows/Lint/badge.svg)
![pytest](https://github.com/ellr/checkmk_cisco_aci/workflows/pytest/badge.svg)

## Description

Check MK special agent for monitoring Cisco ACI.


## Authors

Brought to you as open source with ❤️ by WAGNER AG.

Thanks to all the contributors:

- Samuel Zehnder (Netcloud) - developping the much loved original version of this plugin 🚀
- Fabian Binder (comNET) - developping aci_fault_inst and wrote most of the checkman pages
- Simon Meister (WAGNER AG) - having the lead on bringing this project to the next level + testing/bugfixing
- Roland Wyss (WAGNER AG) - Added apic health feature
- Roger Ellenberger (WAGNER AG) - migrating the plugin to CheckMK 2.0 and extended it


This is a joint work between Netcloud, comNET and WAGNER AG.


## Development

For Developing this plugin, the excellent [boilerplate](https://github.com/jiuka/checkmk_template) by [jjuka](https://github.com/jiuka) was used.

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

Directories are mapped into the Checkmk site using symlinks.


### Continuous integration - GitHub Actions

There is GitHub workflows to test, lint and build source code in this repository.
