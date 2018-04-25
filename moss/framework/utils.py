#! /usr/bin/env python

import struct
import fcntl
import termios
import time
import json
import sys
import os
import subprocess
import moss

from netmiko.ssh_dispatcher import platforms


def colour(text, colour, bold=False):
    colours = {
        "white": '\033[0;97m',
        "green": '\033[0;92m',
        "red": '\033[0;31m',
        "magenta": '\033[0;35m',
        "reset": '\033[0;39m',
        "bold": '\033[0;1m',
        "blue": '\033[0;36m'
    }

    if bold:
        return colours['bold'] + colours[colour] + text + colours['reset']
    else:
        return colours[colour] + text + colours['reset']


def get_terminal_width():
    h, w, _, _ = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
    return int(w)


def start_banner():
    terminal_width = get_terminal_width()
    header = '[ Task Start ]'
    banner = '=' * ((terminal_width - len(header)) / 2) + header + '=' * ((terminal_width - len(header)) / 2)

    if moss.framework._global.WEB == True:
        print "<br/><p class='start-banner'>" + banner + "</p>"
    else:
        print colour(banner, 'white', bold=True)


def module_not_found_error(module, vendor):
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Module {} not found for vendor {}. Exiting.'.format(module, vendor)
    else:
        print colour(' Module {} not found for vendor {}. Exiting.'.format(module, vendor), 'red', bold=True)


def device_operation_not_found_error(operation, vendor):
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Device operation {} not found for vendor {}. Exiting.'.format(operation, vendor)
    else:
        print colour(' Device operation {} not found for vendor {}. Exiting.'.format(operation, vendor), 'red', bold=True)


def module_doesnt_have_correct_parameters(module):
    if moss.framework._global.WEB == True:
        print "<br/>" + ' {} takes connection and store as parameters. Exiting.'.format(module)
    else:
        print colour(' {} takes connection and store as parameters. Exiting.'.format(module), 'red', bold=True)


def username_or_password_not_found_error():
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Username or password for device not found. Exiting.'
    else:
        print colour(' Username or password for device not found. Exiting.', 'red', bold=True)


def vendor_not_found_error():
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Vendor for device not found. Exiting. Supported vendors are: {}'.format(', '.join(platforms))
    else:
        print colour(' Vendor for device not found. Exiting. Supported vendors are: {}'.format(', '.join(platforms)), 'red', bold=True)


def ip_not_found_error():
    if moss.framework._global.WEB == True:
        print "<br/>" + ' IP for device not found. Exiting.'
    else:
        print colour(' IP for device not found. Exiting.', 'red', bold=True)


def targets_list_not_found_error():
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Targets list not found. Exiting.'
    else:
        print colour(' Targets list not found. Exiting.', 'red', bold=True)


def task_list_not_found_error():
    if moss.framework._global.WEB == True:
        print "<br/>" + ' Task list not found. Exiting.'
    else:
        print colour(' Task list not found. Exiting.', 'red', bold=True)


def start_header(module_order):
    first_module = module_order[0]['module']
    if moss.framework._global.WEB == True:
        print "<br/><h6 class='start-header'>" + ' : : Modules to be executed:  </h6>'
    else:
        print colour(' :: Modules to be executed: ', 'white', bold=True)

    for module in module_order:
        if moss.framework._global.WEB == True:
            print "<br/><h6 class='start-header-names'>" + '\t{}</h6>'.format(module['module'])
        else:
            print colour('\t{}'.format(module['module']), 'white')

    if moss.framework._global.WEB == True:
        print "<br/><br/><h6 class='start-header'>" + '\n : : First module: {}</h6></br>'.format(first_module)
    else:
        print colour('\n :: First module: {}'.format(first_module), 'white', bold=True)


def put_output_file_location(output_file):
    if moss.framework._global.WEB == True:
        print "<br/><br/><h6 class='start-header'> : : Output file location: {}</h6><br/><br/>".format(output_file)
    else:
        print colour(' :: Output file location: {}'.format(output_file), 'white', bold=True)


def post_device(name, no_ssh=False):
    if no_ssh == True:
        if moss.framework._global.WEB == True:
            print "<br/><h6 class='start-header'>" + "\n : : Target: {} <h6 class='post-device'>(No SSH)</h6></h6>".format(name) 
        else:
            print colour('\n :: Target: {}'.format(name), 'white', bold=True) + colour(' (No SSH)', 'blue', bold=True)
    else:
        if moss.framework._global.WEB == True:
            print "<br/><h6 class='start-header'>" + '\n : : Target: {}</h6>'.format(name)
        else:
            print colour('\n :: Target: {}'.format(name), 'white', bold=True)


def module_start_header(task):
    if moss.framework._global.WEB == True:
        print "<br/><h6 class='module-start-header'>" + '\t : : {}</h6><b>'.format(task)
    else:
        print colour('\t :: {}'.format(task), 'white'),


def module_success(delay):
    if delay > 0:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='success'>success</h6>" + " <h6 class='delay'>(delay = {})</h6>".format(delay)
        else:
            print colour('success', 'green') + colour(' (delay = {})'.format(delay), 'white', bold=True)
        time.sleep(delay)
    else:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='success'>success</h6>"
        else:
            print colour('success', 'green')


def module_branch(next_module, delay):
    if delay > 0:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='branch'>branching to {}</h6>".format(next_module) + " <h6 class='delay'>(delay = {})</h6>".format(delay)
        else:
            print colour('branching to {}'.format(next_module), 'blue') + colour(' (delay = {})'.format(delay), 'white', bold=True)
    else:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='branch'>branching to {}</h6>".format(next_module)
        else:
            print colour('branching to {}'.format(next_module), 'blue')
    time.sleep(delay)


def module_end():
    if moss.framework._global.WEB == True:
        print "</b><h6 class='success'>end</h6>"
    else:
        print colour('end', 'green')


def module_fail():
    if moss.framework._global.WEB == True:
        print "</b><h6 class='fail'>fail</h6>"
    else:
        print colour('fail', 'red')


def module_retry(delay):
    if delay > 0:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='retry'>retry</h6> <h6 class='delay'>(delay = {})</h6>".format(delay)
        else:
            print colour('retry', 'magenta') + colour(' (delay = {})'.format(delay), 'white', bold=True)
    else:
        if moss.framework._global.WEB == True:
            print "</b><h6 class='retry'>retry</h6>"
        else:
            print colour('retry', 'magenta')
    time.sleep(delay)


def end_banner():
    terminal_width = get_terminal_width()
    header = '[ Task End ]'
    banner = '=' * ((terminal_width - len(header)) / 2) + header + '=' * ((terminal_width - len(header)) / 2)

    if moss.framework._global.WEB == True:
        print "<p class='start-banner'>" + banner + "</p>"
    else:
        print colour(banner, 'white')


def timer():
    return time.time()


def runtime(start, end):
    return end - start


def print_data_in_json(data):
    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


def write_json_to_file(data, filename):
    with open(filename, 'a+') as json_file:
        json_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))


def edit_file(filename):
    editor = os.environ.get('EDITOR', 'vim')

    with open(filename, 'a+') as edit_file:
        subprocess.call([editor, filename])


def create_task_start_temp_file():
    if not os.path.exists('output'):
        os.makedirs('output')

    with open('output/.stdout.json', 'w') as temp_output_file:
        start_skeleton = {"module_results": {}}
        temp_output_file.write(json.dumps(start_skeleton, indent = 4))


def create_task_links_temp_file():
    with open('output/.links.json', 'w') as temp_output_file:
        start_skeleton = {"links": {}}
        temp_output_file.write(json.dumps(start_skeleton, indent = 4))


def make_it_look_important():
    print('.'),
