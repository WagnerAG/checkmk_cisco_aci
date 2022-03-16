#!/bin/bash

for DIR in 'agents' 'checkman' 'checks' 'doc' 'inventory' 'notifications' 'pnp-templates' 'web'; do
    rm -rfv $OMD_ROOT/local/share/check_mk/$DIR
    ln -sv $WORKSPACE/$DIR $OMD_ROOT/local/share/check_mk/$DIR
done;

rm -rfv $OMD_ROOT/local/lib/check_mk/notification_plugins
ln -sv $WORKSPACE/notification_plugins $OMD_ROOT/local/lib/check_mk/notification_plugins

rm -rfv $OMD_ROOT/local/lib/check_mk/base/plugins/agent_based
ln -sv $WORKSPACE/agent_based $OMD_ROOT/local/lib/check_mk/base/plugins/agent_based

rm -rfv $OMD_ROOT/local/lib/nagios/plugins
ln -sv $WORKSPACE/nagios_plugins $OMD_ROOT/local/lib/nagios/plugins

ln -sv $WORKSPACE/temp $OMD_ROOT/local/tmp

rm -rfv $OMD_ROOT/local/lib/check_mk/base/cee/plugins/bakery
mkdir -p $OMD_ROOT/local/lib/check_mk/base/cee/plugins
ln -sv $WORKSPACE/bakery $OMD_ROOT/local/lib/check_mk/base/cee/plugins/bakery

htpasswd -b $OMD_ROOT/etc/htpasswd cmkadmin cmkadmin