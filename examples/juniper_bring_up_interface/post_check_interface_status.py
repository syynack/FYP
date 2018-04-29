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
def post_check_interface_status(connection, store):
    ''' Gets the output of show interfaces terse for an interface '''

    current_interface_status = execute_device_operation(
        'juniper_show_interfaces_terse', 
        connection,
        interface = store["arguments"]["interface"]
    )

    if current_interface_status["result"] == "fail":
        return ModuleResult.fail

    for interface in current_interface_status["stdout"]["interfaces"]:
        if interface["link_status"] != "up":
            return ModuleResult.fail

    return ModuleResult.success


