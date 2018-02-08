#! /usr/bin/env python

import os
import json
import uuid
import inspect

from moss.framework.core.log import log
from moss.framework.core.exceptions import RegisteredModuleError

registered_operations = {}

def registry(group, platform, func):
    '''
    Summary:
    Store functions from devops and user created module in the registry. That way
    only devops scripts and modules decorated with @register can be ran. Modules
    must be registered before they can be ran in a task

    Arguments:
    group           string, name of group script should be stored in
    platform        string, platform devop or module is written to run on
    func            string, name of function to be ran
    '''

    if group not in registered_operations:
        registered_operations[group] = {}

    if not registered_operations[group].get(platform):
        registered_operations[group][platform] = {}
    try:
        registered_operations[group][platform].update({func.__name__: func})
    except:
        pass


def _log_operation_to_file(platform, operation, module_result):
    curframe = inspect.currentframe()
    current_frame = inspect.getouterframes(curframe, 2)[3][3]

    file_data = {}
    file_data[operation] = {}
    file_data[operation].update(module_result)

    for key, index in registered_operations['modules'][platform].iteritems():
        if current_frame in key:
            with open('output/.links.json', 'r') as temp_links_file:
                links_data = json.load(temp_links_file)

            links_data['links'].update({current_frame: operation})

            with open('output/.links.json', 'w') as temp_links_file:
                json.dump(links_data, temp_links_file, indent = 4)

    with open('output/.stdout.json', 'r') as temp_module_output:
        module_data = json.load(temp_module_output)

    module_data['module_results'].update(file_data)

    with open('output/.stdout.json', 'w') as temp_module_output:
        json.dump(module_data, temp_module_output, indent = 4)


def _run_registered_device_operation(platform, operation, connection, **kwargs):
    '''
    Summary:
    Wrapper to be used internally to run device operations through the registry.

    Arguments:
    platform        string, platform the operation is categorised by
    operation       string, operation to be run
    connection      netmiko SSH obj, connection to used to run the operaiton
    **kwargs        optional arguments the operation needs to run
    '''

    log('Attempting to run device operation {}'.format(operation))
    device_operation_result = registered_operations['devops'][platform][operation](connection, **kwargs)
    log('Successfully ran device operation {}'.format(operation))

    if isinstance(device_operation_result, dict):
        device_operation_result.update({'uuid': str(uuid.uuid4())})

    _log_operation_to_file(platform, operation, device_operation_result)

    return device_operation_result


def _run_registered_module(platform, operation, connection, context):
    '''
    Summary:
    Wrapper to be used internally to run modules through the registry.

    Arguments:
    platform        string, platform the operation is categorised by
    operation       string, operation to be run
    connection      netmiko SSH obj, connection to used to run the operation
    context         dict, current context of the task
    '''

    log('Attempting to run module {}'.format(operation))

    try:
        module_result = registered_operations['modules'][platform][operation](connection, context)
    except KeyError as e:
        raise RegisteredModuleError, e

    frame = inspect.currentframe()
    context = frame.f_locals['context']

    if isinstance(module_result, dict):
        pass
    elif callable(module_result):
        module_result = module_result()
    else:
        module_result = {'result': 'success', 'delay': 0}

    log('Successfully ran module {}'.format(operation))
    module_result.update({'uuid': str(uuid.uuid4())})
    module_result.update({'context': context})

    _log_operation_to_file(platform, operation, module_result)

    return module_result
