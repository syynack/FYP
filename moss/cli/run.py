#! /usr/bin/env python

import click

from moss.framework.core.task import task_control

@click.command(short_help = 'Run a task from predefined files')
@click.option('--targets', default='targets.yml', help='File containing target information (default: endpoints)')
@click.option('-o', '--output-file', default='', help='Write the output of the task to a file')
@click.option('-p', '--print-output', is_flag=True, help='Print the JSON output of the task to the screen')
@click.option('--task', default='task.yml', help='File containing task information (default: task)')
def run(targets, output_file, print_output, task):
    '''
    Summary.
    TFW there's more comments than code. This just initiates a task.
    '''

    task_control(targets, output_file, print_output, task)
