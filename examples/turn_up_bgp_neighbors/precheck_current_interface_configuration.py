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
def precheck_current_interface_configuration(connection, store):
    current_interface_configuration = execute_device_operation('cisco_ios_show_interfaces', connection)
    
    if current_interface_configuration["result"] == "fail":
        return ModuleResult.fail

    current_hostname = store["hostname"]

    for index, interface in enumerate(current_interface_configuration["stdout"]):
        for key, value in interface.iteritems():
            if key == store["configuration_statements"][current_hostname]["interface"][0].split()[1]:
                current_address = current_interface_configuration["stdout"][index].get("address")

    if current_address == None:
        return ModuleResult.branch('continue') #Modify

    if current_address in store["configuration_statements"][current_hostname]["interface"][1]:
        del store["configuration_statements"][current_hostname]["interface"]

    return ModuleResult.success


