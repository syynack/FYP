#! /usr/bin/env python

import os
import sys
import socket
import click
import yaml
import getpass
import uuid
import json

from moss.framework.core.connection import Connection, NoSSHMockObject
from moss.framework.core.registry import _run_registered_device_operation
from moss.framework.core.module import Module
from moss.framework.utils import start_banner, start_header, timer, end_banner, write_json_to_file, \
                                 create_task_start_temp_file, create_task_links_temp_file, post_device, \
                                 print_data_in_json, put_output_file_location, username_or_password_not_found_error, \
                                 vendor_not_found_error, ip_not_found_error, targets_list_not_found_error, \
                                 task_list_not_found_error
from datetime import datetime
from getpass import getuser

STORE = {}


def _task_start_signals(module_order):
    create_task_start_temp_file()
    create_task_links_temp_file()

    return {
        'results': {
            'modules': []
        },
        'start_time': timer(),
        'start_date_time': str(datetime.now()),
        'start_user': getpass.getuser(),
        'start_hostname': socket.gethostname()
    }


def _task_end_signals(start_data):
    end_data = {
        'end_time': timer(),
        'end_date_time': str(datetime.now()),
        'run_time': timer() - start_data['start_time']
    }
    end_data.update(start_data)
    return end_data


def _parse_yaml_data(*args):
    '''
    Summary:
    Takes YAML data from target and task files and returns as list of dicts

    Arguments:
    *args           filenames to be parsed

    Returns:
    list
    '''

    yaml_data = []

    for target_file in args:
        try:
            with open(target_file, 'r') as yaml_file:
                try:
                    yaml_data.append(yaml.load(yaml_file))
                except yaml.YAMLError as e:
                    print e
        except IOError as e:
            error = str(e)
            print 'Cannot find file {}'.format(str(error.split('directory')[1][4:-1]))
            sys.exit(1)

    return yaml_data


def _construct_task_order(task_data):
    '''
    Summary:
    Constructs the correct task order for the task with default outcomes.

    Arguments:
    task_data           list, task_data['task'] returned from parse_yaml_data

    Returns:
    list
    '''

    module_order = []

    for module in task_data:
        module_order.append({'module': module})

    for index, module in enumerate(module_order[:-1]):
        module['next_module'] = module_order[index + 1]['module']

    module_order[-1]['next_module'] = ''
    return module_order


def _construct_target(target, target_data, no_ssh=False):
    '''
    Summary:
    Parses dict from targets file to construct an targets obj with the correct information.

    Arguments:
    target        dict, data from the targets file containing connection information
    target_data   dict, entire target data

    Return:
    moss Device object containing netmiko SSH object
    '''

    username_sources = [target.get('username'), target_data.get('global_username')]
    password_sources = [target.get('password'), target_data.get('global_password')]

    username = None
    password = None

    for element in username_sources:
        if element != '':
            username = element

    for element in password_sources:
        if element != '':
            password = element

    if username is None or password is None:
        username_or_password_not_found_error()
        end_banner()
        sys.exit(1)

    if target.get('vendor') == '' and target.get('global_vendor') is None:
        vendor_not_found_error()
        end_banner()
        sys.exit(1)

    if target.get('ip') == '':
        ip_not_found_error()
        end_banner()
        sys.exit(1)

    if no_ssh:
        device = NoSSHMockObject(
            vendor = target.get('vendor') if target.get('vendor') else target_data.get('global_vendor')
        )

        return device

    device = Connection(
        vendor = target.get('vendor') if target.get('vendor') else target_data.get('global_vendor'),
        ip = target.get('ip'),
        username = username,
        password = '' if target_data.get('key_file') else password,
        port = 22 if target.get('port') is None else target['port'],
        timeout = 8 if target.get('timeout') is None else target['timeout'],
        session_timeout = 60 if target.get('session_timeout') is None else target['session_timeout']
    )

    return device


def _construct_stdout(start_data):
    with open('output/.stdout.json', 'r') as stdout:
        stdout_data = json.load(stdout)

    with open('output/.links.json', 'r') as links:
        links_data = json.load(links)

    links_keys = []

    for item in links_data['links']:
        links_keys.append(item)

    for link_key in links_keys:
        per_module_stdout = {"operations": []}
        for item in links_data['links'][link_key]:
            stdout_data["module_results"][item].update({"name": item})
            per_module_stdout["operations"].append(stdout_data["module_results"][item])

        for index, module in enumerate(start_data["results"]["modules"]):
            if module["module"] == link_key:
                for key, value in stdout_data['module_results'].iteritems():
                    if key == link_key:
                        per_module_stdout.update(value)

                start_data['results']['modules'][index].update(per_module_stdout)

    end_data = _task_end_signals(start_data)
    end_data.update({'uuid': str(uuid.uuid4())})
    title = 'output/{}-{}-{}-{}.json'.format(end_data['uuid'], end_data['start_date_time'], end_data['start_user'], end_data['target']).replace(' ', '-')
    write_json_to_file(end_data, title)

    os.remove('output/.stdout.json')
    os.remove('output/.links.json')

    with open(title, 'r') as output_file:
        return os.path.abspath(output_file.name)


def _run_task(connection, module_order):
    '''
    Summary:
    Function to run the actual task defined in the task file. Works by running modules
    defined in the task file through the registry. Their outcome is then returned which,
    as defined in moss.framework.core.module, will be either quit, branch, fail, or success.
    moss.framework.core.module will parse that information, and return it to _run_task.
    _run_task then decides if we need to continue with the task or fail out.
    '''

    next_module = module_order[0]
    start_data = _task_start_signals(module_order)
    store = STORE
    if not isinstance(connection, Connection):
        device_facts = _run_registered_device_operation(connection.device_type, connection.device_type + '_get_facts', connection)
    else:
        device_facts = {}

    start_data.update({
        "device_facts": device_facts
    })

    while next_module != '':
        module = Module(
            connection = connection,
            module = next_module['module'],
            next_module = next_module['next_module'],
            store = store
        )

        result = module.run()
        next_module = result['next_module']
        store = result['store']
        start_data['results']['modules'].append(result)
        start_data['target'] = connection.ip

        if next_module != '':
            module_index = [index for index, module in enumerate(module_order) if next_module == module['module']]
            if not module_index:
                next_module = ''
            else:
                next_module = module_order[module_index[0]]

    start_data["result"] = start_data["results"]["modules"][-1]["result"]
    output_file = _construct_stdout(start_data)
    start_data.update({"output_file": output_file})
    put_output_file_location(output_file)
    return start_data


def task_control(targets, output_file, print_output, task):
    '''
    Summary:
    Controlling for the overall execution of the task, controls running each
    module for each targets

    Arguments:
    targets             file, containing target information
    output_file         file, optional output file
    print_output        option, print the output in JSON
    task                file, containing task information

    Returns:
    file or JSON output
    '''

    target_data, task_data = _parse_yaml_data(targets, task)

    if task_data.get('task') is None:
        task_list_not_found_error()
        sys.exit(1)

    module_order = _construct_task_order(task_data['task'])

    start_banner()
    start_header(module_order)

    if target_data.get('targets') is None:
        targets_list_not_found_error()
        end_banner()
        sys.exit(1)

    try:
        for target in target_data['targets']:
            if task_data.get('no_ssh') == True:
                post_device(target['ip'], no_ssh=True)
                target_connection = _construct_target(target, target_data)
            else:
                post_device(target['ip'])
                target_obj = _construct_target(target, target_data)
                target_connection = target_obj.get_connection()

            result = _run_task(target_connection, module_order)

            if not task_data.get('no_ssh'):
                target_obj.close(target_connection)

            if print_output:
                print_data_in_json(result)

            if output_file:
                write_json_to_file(result, output_file)
    except KeyboardInterrupt:
        end_banner()
        sys.exit(1)

    end_banner()
