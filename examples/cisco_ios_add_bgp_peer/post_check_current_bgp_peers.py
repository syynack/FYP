#! /usr/bin/env python

# Created by mcli.
# This file should be used as a template for any user created modules.

from moss import ModuleResult, execute_device_operation, register

# ModuleResult can be used to influence the outcome of a task.
#    ModuleResult.end                Module will be marked as successful but task will not continue
#    ModuleResult.branch             Module will branch to another module
#    ModuleResult.fail               Module will be marked as a failure and task will not continue
#    ModuleResult.success            Module will be marked as a success and will continue (this is implicit)
#    ModuleResult.retry              Module will be retried
# It is not required that a module result must be returned, by default the module will
# be marked as a success if not specified otherwise.
#

VENDOR = 'cisco_ios'

@register(vendor = VENDOR)
def post_check_current_bgp_peers(connection, store):
    ''' Checks current BGP peers for updated entry '''

    current_bgp_peers = execute_device_operation('cisco_ios_get_bgp_summary', connection)

    if current_bgp_peers["result"] == "fail":
        return ModuleResult.fail

    for peer in current_bgp_peers["stdout"]["peers"]:
        if (store["arguments"]["peer_ip"] == peer["peer_ip"]) and (int(store["arguments"]["peer_as"]) == peer["as_number"]):
            return ModuleResult.success
        else:
            return ModuleResult.fail