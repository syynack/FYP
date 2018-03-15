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
def precheck_store_configuration(connection, store):
    configuration_statements = {
        "R1": {
            "interface": [
                'interface FastEthernet1/5',
                'ip add 10.0.0.0 255.255.255.254',
                'no shut'
            ],
            "bgp": [
                'router bgp 1',
                'neighbor 10.0.0.1 remote-as 2'           
            ]
        },
        "R2": {
            "interface": [
                'interface FastEthernet1/2',
                'ip add 10.0.0.1 255.255.255.254',
                'no shut'
            ],
            "bgp": [
                'router bgp 2',
                'neighbor 10.0.0.0 remote-as 1'
            ]
        }
    }

    store["configuration_statements"] = configuration_statements
    return ModuleResult.success


