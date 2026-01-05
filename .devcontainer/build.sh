#!/bin/bash

set -euo pipefail

NAME=$(python3 -c 'print(eval(open("package").read())["name"])')
VERSION=$(python3 -c 'print(eval(open("package").read())["version"])')
WORKSPACE=$(pwd)

rm /omd/sites/cmk/var/check_mk/packages/* ||:
ln -s $WORKSPACE/package /omd/sites/cmk/var/check_mk/packages/$NAME


mkp -v package package 2>&1 | sed '/Installing$/Q' ||:

rm $NAME-$VERSION.mkp ||:
cp /omd/sites/cmk/var/check_mk/packages_local/$NAME-$VERSION.mkp .

mkp inspect $NAME-$VERSION.mkp

# Set Outputs for GitHub Workflow steps (using environment files)
if [ -n "${GITHUB_OUTPUT:-}" ]; then
    {
        echo "pkgfile=$(ls *.mkp)"
        echo "pkgname=${NAME}"
        echo "pkgversion=${VERSION}"
    } >> "$GITHUB_OUTPUT"
fi