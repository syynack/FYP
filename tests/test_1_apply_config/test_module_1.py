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
def test_module_1(connection, store):
    config_statements = [
        'router ospf 1',
        'router-id 1.1.1.1',
        'network 192.168.253.129 255.255.255.0 area 0'
    ]

    output = execute_device_operation(
        'cisco_ios_apply_configuration', 
        connection, 
        config_statements = config_statements,
        #write_config = True
    )
    
    return ModuleResult.success


