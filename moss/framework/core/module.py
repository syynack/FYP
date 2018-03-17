#!/usr/bin/env python

import uuid
import sys
import socket
import os
import getpass
import inspect
import time
import moss.framework.devops

from datetime import datetime
from moss.framework.core.registry import registered_operations, _run_registered_module, _run_registered_device_operation
from moss.framework.core.exceptions import ModuleResultError
from moss.framework.utils import timer, module_start_header, module_success, module_branch, module_end, module_fail, module_retry


def execute_device_operation(operation, connection, **kwargs):
    '''
    Summary:
    Allows modules to run registeredd devops scripts from the module.

    Arguments:
    operation           string, name of the devops function
    connection          netmiko SSH object, endpoint connection
    **kwargs            dict, keyword arguments taken by the devops script

    Returns:
    dict
    '''

    return _run_registered_device_operation(connection.device_type, operation, connection, **kwargs)


class ModuleResult():
    '''
    Summary:
    Return dict representing the outcome of the module.

    ModuleResult.end                Module will be marked as successful but task will not continue
    ModuleResult.branch             Module will branch to another module
    ModuleResult.fail               Module will be marked as a failure and task will not continue
    ModuleResult.success            Module will be marked as a success and will continue (this is implicit)
    ModuleResult.retry              Module will be retried
    '''

    @staticmethod
    def end():
        return {
            'result': 'end'
        }

    @staticmethod
    def branch(module, delay = 0):
        return {
            'result': 'branch',
            'branching_module': module,
            'delay': delay
        }

    @staticmethod
    def fail():
        return {
            'result': 'fail'
        }

    @staticmethod
    def success(delay = 0):
        return {
            'result': 'success',
            'delay': delay
        }

    @staticmethod
    def retry(delay = 5):
        return {
            'result': 'retry',
            'delay': delay
        }


class Module():
    '''
    Summary:
    Module object to be created when running a task. This class creates an object for a module
    with the ability to run the module through the registry, and print information.
    '''

    def __init__(self, connection = None, module = '', next_module = '', store = {}):
        self.connection = connection
        self.module = module
        self.next_module = next_module
        self.store = store


    def run(self):
        '''
        Summary:
        Runs self.module through the registry. Run initiates the start signals which essentially
        prints the running module name to the screen and collects data such as the start date time,
        the initiating user, and the hostname of the device the module was run from.
        '''

        self.module_start_data = self._module_start_signals(self.module)
        module_result = _run_registered_module(self.connection.device_type, self.module, self.connection, self.store)
        return self._module_result(module_result)


    def _module_start_signals(self, module):
        module_start_header(module)

        return {
            'start_time': timer(),
            'start_date_time': str(datetime.now())
        }


    def _module_result(self, module_result):
        result = module_result['result']
        store = module_result['store']

        result_dict = {
            'result': result,
            'store': store,
            'end_time': timer(),
            'run_time': timer() - self.module_start_data['start_time'],
            'end_date_time': str(datetime.now())
        }

        result_dict.update(self.module_start_data)
        result_dict.update({'module': self.module})
        result_dict.update({'uuid': str(uuid.uuid4())})
        
        if result == 'success':
            result_dict.update({'next_module': self.next_module})
            module_success(module_result['delay'])
        elif result == 'branch':
            result_dict.update({'next_module': module_result['branching_module']})
            module_branch(module_result['branching_module'], module_result['delay'])
        elif result == 'end':
            result_dict.update({'next_module': ''})
            module_end()
        elif result == 'fail':
            module_fail()
            result_dict.update({'next_module': ''})
        elif result == 'retry':
            module_retry(module_result['delay'])
            result_dict.update({'next_module': self.module})

        return result_dict
