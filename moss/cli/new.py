#! /usr/bin/env python

import click
import sys
import os

from moss.framework.utils import edit_file
from moss.framework.text import TASK_BASE_TEXT, TARGETS_BASE_TEXT, MODULE_BASE_TEXT

def _create_file(name, contents):
    '''
    Summary:
    Simply creates a file and populates the contents. Will check if
    file already exists.
    '''

    if not os.path.isfile(name):
        with open(name, 'w+') as template:
            template.write(contents)


def _edit_file(name, contents):
    '''
    Summary:
    Opens vim on a file, will also check if that file already exists.
    '''

    if not os.path.isfile(name):
        with open(name, 'w+') as template:
            template.write(contents)
            edit_file(template)
            sys.exit(0)

    print '{} already exists.'.format(name)


@click.command(short_help = 'Create new targets template')
@click.option('-e', '--edit', is_flag=True, help = 'Edit the template now')
@click.option('-o', '--output', default='targets', help = 'Filename for output file')
def targets(edit, output):
    '''
    Summary:
    Creates a new targets file and populates it.
    '''

    if edit:
        _edit_file(output, TARGETS_BASE_TEXT)

    _create_file(output, TARGETS_BASE_TEXT)


@click.command(short_help = 'Create new module template')
@click.option('-e', '--edit', is_flag=True, help = 'Edit the template now')
@click.option('-o', '--output', default='module.py', help = 'Filename for output file')
def module(edit, output):
    '''
    Summary:
    Creates a new module file and populates it.
    '''

    if edit:
        _edit_file(output, MODULE_BASE_TEXT)

    _create_file(output, MODULE_BASE_TEXT)


@click.command(short_help = 'Create new task template')
@click.option('-e', '--edit', is_flag=True, help = 'Edit the template now')
@click.option('-o', '--output', default='task', help = 'Filename for output file')
def task(edit, output):
    '''
    Summary:
    Creates a new task file and populates it.
    '''

    if edit:
        _edit_file(output, TASK_BASE_TEXT)

    _create_file(output, TASK_BASE_TEXT)


@click.group(short_help = 'Create new templates for endpoints, tasks, or custom modules')
def new():
    pass


new.add_command(targets)
new.add_command(module)
new.add_command(task)
