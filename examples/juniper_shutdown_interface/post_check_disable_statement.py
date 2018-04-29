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
def post_check_disable_statement(connection, store):
    ''' Checks configuration to make sure the deactivation config has been applied '''

    configuration_check_output = execute_device_operation(
        'juniper_check_configuration',
        connection,
        config_statements = ["disable"],
        area = 'interfaces {}'.format(store["arguments"]["interface"])
    )

    if configuration_check_output["result"] == "fail":
        return ModuleResult.fail

    for statement in configuration_check_output["stdout"]["present_config_statements"]:
        if "disable;" in statement:
            return ModuleResult.success

    return ModuleResult.fail