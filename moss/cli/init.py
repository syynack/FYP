#! /usr/bin/env python

import click
import os

from moss.framework.utils import edit_file
from moss.framework.text import TARGETS_BASE_TEXT, TASK_BASE_TEXT


@click.command(short_help = 'Initialise a directory with base files')
def init():
    '''
    Summary:
    Initialises a moss working directory by creating standard files and folders.
    This function creates an endpoints and task file which must be used to define
    targets for the task and the task to be run, many of these can be created. The
    .moss directory is created to store output of task and in future possibly logging.
    '''

    files = ['targets.yml', 'task.yml']
    text_mapping = {
        'targets.yml': TARGETS_BASE_TEXT,
        'task.yml': TASK_BASE_TEXT
    }

    for filename in files:
        if not os.path.isfile(filename):
            with open(filename, 'w+') as template:
                template.write(text_mapping[filename])

            edit_file(filename)

    if not os.path.exists('output'):
        os.makedirs('output')
        log_file = open('output/messages.log', 'w')
        log_file.close()
