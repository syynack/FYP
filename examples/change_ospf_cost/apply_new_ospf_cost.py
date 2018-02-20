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
def apply_new_ospf_cost(connection, store):
    ''' Applies new cost configuration to interfaces. '''

    for operational_interface in store["operational_interfaces"]:
        config_statements = ['interface {}'.format(operational_interface)] + store["config_statements"]

        apply_config_output = execute_device_operation(
            'cisco_ios_apply_configuration', 
            connection,
            config_statements = config_statements
        )

        if apply_config_output["result"] == "fail":
            return ModuleResult.fail

    return ModuleResult.success

        


