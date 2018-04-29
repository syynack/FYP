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
def compare_bgp_peer_states(connection, store):
    ''' Compares the current BGP peer state with that gathered in previous module '''

    current_bgp_peer_state = execute_device_operation('juniper_get_bgp_peers', connection)

    if current_bgp_peer_state["result"] == "fail":
        return ModuleResult.fail

    peers_with_changed_state = []

    for current_peer in current_bgp_peer_state["stdout"]["peers"]:
        for previous_peer in store["previous_bgp_peer_state"]:
            if current_peer["peer_ip"] == previous_peer["peer_ip"]:
                if all([current_peer["peering_state"] != previous_peer["peering_state"], 
                        current_peer["peering_state"] != "Established"]):
                    peers_with_changed_state.append(current_peer)

    if len(peers_with_changed_state) > 0:
        store["peers_with_changed_state"] = peers_with_changed_state
        return ModuleResult.branch("monitor_bgp_peer_state", delay = 20)

    store["previous_bgp_peer_state"] = current_bgp_peer_state["stdout"]["peers"]
    return ModuleResult.retry(delay = 10)