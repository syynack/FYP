#! /usr/bin/env python

import struct
import fcntl
import termios
import time
import json
import sys
import os
import subprocess


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

    print colour(banner, 'white', bold=True)


def start_header(module_order):
    first_module = module_order[0]['module']
    print colour(' :: Modules to be executed: ', 'white', bold=True)

    for module in module_order:
        print colour('\t{}'.format(module['module']), 'white')

    print colour('\n :: First module: {}'.format(first_module), 'white', bold=True)


def post_device(name):
    print colour('\n :: Target: {}'.format(name), 'white', bold=True)


def module_start_header(task):
    print colour('\t :: {}'.format(task), 'white'),


def module_success(delay):
    print colour('success', 'green')
    time.sleep(delay)


def module_branch(next_module, delay):
    print colour('branching to {}'.format(next_module), 'blue')
    time.sleep(delay)


def module_end():
    print colour('end', 'green')


def module_fail():
    print colour('fail', 'red')


def module_retry(delay):
    print colour('retry', 'magenta')
    time.sleep(delay)


def end_banner():
    terminal_width = get_terminal_width()
    header = '[ Task End ]'
    banner = '=' * ((terminal_width - len(header)) / 2) + header + '=' * ((terminal_width - len(header)) / 2)
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
