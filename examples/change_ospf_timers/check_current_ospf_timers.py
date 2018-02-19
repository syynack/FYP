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
def check_current_ospf_timers(connection, store):
    config_statements = [
        'ip ospf dead-interval 4',
        'ip ospf hello-interval 1'
    ]

    for operational_interface in store["operational_interfaces"]:
        current_ospf_timers_output = execute_device_operation(
            'cisco_ios_check_configuration',
            connection,
            config_statements = config_statements,
            area = 'interface {}'.format(operational_interface)
        )

        if current_ospf_timers_output["result"] == "fail":
            return ModuleResult.fail
        
        if not current_ospf_timers_output["stdout"]["present_config_statements"]:
            return ModuleResult.success

        store["operational_interfaces"].remove(operational_interface)
        return ModuleResult.success



    


