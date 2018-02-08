
TARGETS_BASE_TEXT = '''# This file is used to define target information to be used when executing
# tasks. This information is what shall be used when attempting to connect
# to the targets.


# Authentication
# Define a global password to be used for all device connections
global_password: ''

# Define a global username to be used for all device connections
global_username: ''


# Endpoints
# Define a global vendor if all the targets run the same operating system
global_vendor: ''

# Define endpoint information
targets:

# Example
- vendor: 'cisco_ios'
  ip: '192.168.0.1'
  username: 'username'
  password: 'password'
'''

TASK_BASE_TEXT = '''# This file is used to define task stages to be executed within the task.

# Task
task:

# Example
- 'test_module_1'

'''

MODULE_BASE_TEXT = '''#! /usr/bin/env python

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

PLATFORM = ''

@register(platform = PLATFORM)
def module_name(connection, store):
    return ModuleResult.success


'''
