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

VENDOR = 'juniper'

@register(vendor = VENDOR)
def get_bgp_peer_states(connection, store):
    ''' Gathers the current status of all BGP peers '''

    current_bgp_peer_state = execute_device_operation('juniper_get_bgp_peers', connection)

    if current_bgp_peer_state["result"] == "fail":
        return ModuleResult.fail

    store["previous_bgp_peer_state"] = current_bgp_peer_state["stdout"]["peers"]
    return ModuleResult.success(delay = 10)