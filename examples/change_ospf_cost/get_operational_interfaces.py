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

PLATFORM = 'cisco_ios'

@register(platform = PLATFORM)
def get_operational_interfaces(connection, store):
    ''' Finds currently up/up interfaces on the target device and stores interface names. '''

    current_interfaces = execute_device_operation('cisco_ios_show_interfaces', connection)

    if current_interfaces["result"] == "fail":
        return ModuleResult.fail

    operational_interfaces = []

    for interface in current_interfaces["stdout"]:
        if interface["operational_status"] == "up" and interface["line_status"] == "up":
            operational_interfaces.append(interface["name"])

    if len(operational_interfaces) == 0:
        return ModuleResult.end

    store["operational_interfaces"] = operational_interfaces
    return ModuleResult.success
            


