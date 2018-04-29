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
def post_check_bgp_peer_config(connection, store):
    ''' Post checks that BGP neighbour config has been applied '''

    config_statements = ['neighbor {} remote-as {}'.format(store["arguments"]["peer_ip"], store["arguments"]["peer_as"])]

    current_config = execute_device_operation(
        'cisco_ios_check_configuration',
        connection,
        config_statements = config_statements,
        area = 'router bgp {}'.format(store["arguments"]["local_as"])
    )

    if current_config["result"] == "fail":
        return ModuleResult.fail

    if current_config["stdout"]["present_config_statements"]:
        return ModuleResult.success