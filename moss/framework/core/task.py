#! /usr/bin/env python

import os
import sys
import socket
import click
import yaml
import getpass
import uuid
import json

from moss.framework.core.connection import Connection
from moss.framework.core.module import Module
from moss.framework.utils import start_banner, start_header, timer, end_banner, write_json_to_file, create_task_start_temp_file, create_task_links_temp_file, post_device
from datetime import datetime
from getpass import getuser

CONTEXT = {}


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
    Takes YAML data from endpoint and task files and returns as list of dicts

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


def _construct_endpoint(endpoint, endpoint_data):
    '''
    Summary:
    Parses dict from endpoints file to construct an endpoints obj with the correct information.

    Arguments:
    endpoint        dict, data from the endpoints file containing connection information
    endpoint_data   dict, entire endpoint data

    Return:
    moss Device object containing netmiko SSH object
    '''

    username_sources = [endpoint.get('username'), endpoint_data.get('global_username')]
    password_sources = [endpoint.get('password'), endpoint_data.get('global_password')]

    username = None
    password = None

    for element in username_sources:
        if element != None:
            username = element

    for element in password_sources:
        if element != None:
            password = element

    device = Connection(
        device_type = endpoint.get('os') if endpoint.get('os') else endpoint_data.get('global_os'),
        ip = endpoint.get('ip'),
        username = username,
        password = '' if endpoint_data.get('key_file') else password,
        port = 22 if endpoint.get('port') is None else endpoint['port'],
        timeout = 8 if endpoint.get('timeout') is None else endpoint['timeout'],
        session_timeout = 60 if endpoint.get('session_timeout') is None else endpoint['session_timeout']
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

    for module_key, module_value in stdout_data['module_results'].iteritems():
        if module_key in links_keys:
            for index, module in enumerate(start_data['results']['modules']):
                if module['module'] == module_key:
                    golden_key = links_data['links'][module_key]
                    start_data['results']['modules'][index][golden_key] = stdout_data['module_results'].get(golden_key)

    end_data = _task_end_signals(start_data)
    end_data.update({'uuid': str(uuid.uuid4())})
    title = 'output/{}-{}-{}-{}.json'.format(end_data['uuid'], end_data['start_date_time'], end_data['start_user'], end_data['endpoint']).replace(' ', '-')
    write_json_to_file(end_data, title)

    #log_operation_to_redis_database(end_data['uuid'], end_data)

    os.remove('output/.stdout.json')
    os.remove('output/.links.json')


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
    context = CONTEXT

    while next_module != '':
        module = Module(
            connection = connection,
            module = next_module['module'],
            next_module = next_module['next_module'],
            context = context
        )

        result = module.run()
        next_module = result['next_module']
        context = result['context']
        start_data['results']['modules'].append(result)
        start_data['endpoint'] = connection.ip

        if next_module != '':
            module_index = [index for index, module in enumerate(module_order) if next_module == module['module']]
            if not module_index:
                next_module = ''
            else:
                next_module = module_order[module_index[0]]

    _construct_stdout(start_data)


def task_control(endpoints, output_file, print_output, task):
    '''
    Summary:
    Controlling for the overall execution of the task, controls running each
    module for each endpoints

    Arguments:
    endpoints           file, containing endpoint information
    output_file         file, optional output file
    print_output        option, print the output in JSON
    task                file, containing task information

    Returns:
    file or JSON output
    '''

    endpoint_data, task_data = _parse_yaml_data(endpoints, task)
    module_order = _construct_task_order(task_data['task'])

    start_banner()
    start_header(module_order)

    for endpoint in endpoint_data['endpoints']:
        post_device(endpoint['ip'])
        endpoint_obj = _construct_endpoint(endpoint, endpoint_data)
        endpoint_connection = endpoint_obj.get_connection()
        result = _run_task(endpoint_connection, module_order)

        endpoint_obj.close(endpoint_connection)

        if print_output:
            print_data_in_json(result)

        if output_file:
            write_json_to_file(result, output_file)

    end_banner()
