#! /usr/bin/env python

import os
import json
import uuid
import inspect
import sys

from moss.framework.core.log import log
from moss.framework.core.exceptions import RegisteredModuleError
from moss.framework.utils import module_not_found_error, module_doesnt_have_correct_parameters, device_operation_not_found_error, end_banner

registered_operations = {}

def registry(group, vendor, func):
    '''
    Summary:
    Store functions from devops and user created module in the registry. That way
    only devops scripts and modules decorated with @register can be ran. Modules
    must be registered before they can be ran in a task

    Arguments:
    group           string, name of group script should be stored in
    vendor        string, vendor devop or module is written to run on
    func            string, name of function to be ran
    '''

    if group not in registered_operations:
        registered_operations[group] = {}

    if not registered_operations[group].get(vendor):
        registered_operations[group][vendor] = {}
    try:
        registered_operations[group][vendor].update({func.__name__: func})
    except:
        pass


'''
def _find_valid_operation_name(operation_frame, links_data):
    if operation_frame != '_run_task' and operation_frame != 'task_control':
        if operation_frame not in links_data['links']:
            operation_frame = operation_frame + '_0'
            return operation_frame
        else:
            for key in reversed(list(links_data['links'].keys())):
                if operation_frame in key:
                    operation_frame = operation_frame + '_' + str(int(key[:-1]) + 1)
                    return operation_frame
'''


def _log_operation_to_file(vendor, operation, module_result):
    curframe = inspect.currentframe()
    operation_frame = inspect.getouterframes(curframe, 2)[3][3]

    if not os.path.exists('output'):
        os.makedirs('output')
    
    with open('output/.links.json', 'a') as f:
        pass

    with open('output/.stdout.json', 'a') as f:
        pass

    with open('output/.links.json', 'r') as temp_links_file:
        links_data = json.load(temp_links_file)

    with open('output/.stdout.json', 'r') as temp_module_output:
        module_data = json.load(temp_module_output)

    #operation_name = _find_valid_operation_name(operation_frame, links_data)
    #links_data.update({operation_name: []})

    #print operation_frame, operation

    previous_iteration = 0
    previous_iteration_sub_operation = 0
    previous_iteration_run_task = 0

    if (operation_frame is not '_run_task') and (operation_frame is not 'task_control'):
        for key in reversed(list(links_data['links'].keys())):
            if (operation_frame in key[:-2]):
                if previous_iteration <= int(key[-1:]):
                    previous_iteration = int(key[-1:]) + 1

        operation_frame = operation_frame + '_' + str(previous_iteration)

        if operation_frame not in links_data['links']:
            links_data['links'].update({operation_frame: []})

        for sub_operation in links_data['links'][operation_frame]:
            if (operation == sub_operation[:-2]) and (operation != sub_operation):
                if previous_iteration_sub_operation < int(sub_operation[-1:]):
                    previous_iteration_sub_operation = int(sub_operation[-1:])

        operation = operation + '_' + str(previous_iteration_sub_operation)
        operation = operation_frame + '_' + operation
        links_data['links'][operation_frame].append(operation)

    if operation_frame == '_run_task':
        for module in links_data["links"]["_run_task"]:
            if operation in module[:-2]:
                if previous_iteration_run_task <= int(module[-1:]):
                    previous_iteration_run_task = int(module[-1:]) + 1

        original_module = operation
        links_data["links"]["original_modules"].append(original_module)
        operation = operation + '_' + str(previous_iteration_run_task)
        links_data["links"]["_run_task"].append(operation)

    file_data = {}
    file_data[operation] = {}
    file_data[operation].update(module_result)

    module_data['module_results'].update(file_data)

    with open('output/.links.json', 'w') as temp_links_file:
        json.dump(links_data, temp_links_file, indent = 4)

    with open('output/.stdout.json', 'w') as temp_module_output:
        json.dump(module_data, temp_module_output, indent = 4)


    '''
    module_counter = 0

    if current_frame not in links_data['links']:
        if current_frame != "task_control":
            current_frame = current_frame + '_0'
            links_data['links'].update({current_frame: []})
        else:
            links_data['links'].update({current_frame: []})
    else:
        if current_frame != "task_control":
            current_frame = current_frame + '_' + str(module_counter = module_counter + 1)
            links_data['links'].update({current_frame, []})

    --------

    if current_frame != '_run_task' and current_frame != "task_control":
        operation = current_frame[:-2] + '_' + str(len(links_data['links'][current_frame[:-2] + '_' + str(module_counter)]))[:-2] + '_' + operation

    links_data['links'][current_frame].append(operation)


    with open('output/.links.json', 'w') as temp_links_file:
        json.dump(links_data, temp_links_file, indent = 4)

    file_data = {}
    file_data[operation] = {}
    file_data[operation].update(module_result)

    module_data['module_results'].update(file_data)

    with open('output/.stdout.json', 'w') as temp_module_output:
        json.dump(module_data, temp_module_output, indent = 4)

    '''


def _run_registered_device_operation(vendor, operation, connection, **kwargs):
    '''
    Summary:
    Wrapper to be used internally to run device operations through the registry.

    Arguments:
    vendor        string, vendor the operation is categorised by
    operation       string, operation to be run
    connection      netmiko SSH obj, connection to used to run the operaiton
    **kwargs        optional arguments the operation needs to run
    '''

    log('Attempting to run device operation {}'.format(operation))
    try:
        device_operation_result = registered_operations['devops'][vendor][operation](connection, **kwargs)
    except KeyError:
        if not 'facts' in operation:
            device_operation_not_found_error(operation, vendor)
            end_banner()
            sys.exit(1)
        else:
            device_operation_result = {}
            
    log('Successfully ran device operation {}'.format(operation))

    if isinstance(device_operation_result, dict):
        device_operation_result.update({'uuid': str(uuid.uuid4())})

    _log_operation_to_file(vendor, operation, device_operation_result)

    return device_operation_result


def _run_registered_module(vendor, operation, connection, store):
    '''
    Summary:
    Wrapper to be used internally to run modules through the registry.

    Arguments:
    vendor          string, vendor the operation is categorised by
    operation       string, operation to be run
    connection      netmiko SSH obj, connection to used to run the operation
    store           dict, current store of the task
    '''

    log('Attempting to run module {}'.format(operation))
    module_result = registered_operations['modules'][vendor][operation](connection, store)
    '''
    except KeyError:
        module_not_found_error(operation, vendor)
        end_banner()
        sys.exit(1)
    '''
    '''
    except TypeError:
        module_doesnt_have_correct_parameters(operation)
        end_banner()
        sys.exit(1)
    '''
        
    frame = inspect.currentframe()
    store = frame.f_locals['store']

    if isinstance(module_result, dict):
        pass
    elif callable(module_result):
        module_result = module_result()
    else:
        module_result = {'result': 'success', 'delay': 0}

    log('Successfully ran module {}'.format(operation))
    module_result.update({'uuid': str(uuid.uuid4())})
    module_result.update({'store': store})

    _log_operation_to_file(vendor, operation, module_result)

    return module_result
