#! /usr/bin/env python

import click

from moss.framework.core.task import task_control

@click.command(context_settings = dict(ignore_unknown_options=True, allow_extra_args=True), short_help = 'Run a task from predefined files')
@click.option('--targets', default='targets.yml', help='File containing target information (default: endpoints)')
@click.option('-o', '--output-file', default='', help='Write the output of the task to a file')
@click.option('-p', '--print-output', is_flag=True, help='Print the JSON output of the task to the screen')
@click.option('--task', default='task.yml', help='File containing task information (default: task)')
@click.option('--web', is_flag=True, help='Change to printing for web interface output.')
@click.pass_context
def run(ctx, targets, output_file, print_output, task, web):
    '''
    Summary.
    Pass additional arguments in the form of kwargs to be added to the store when the task is started e.g.
    neighbor='192.168.1.1'
    '''

    arguments = {}

    for argument in ctx.args:
        arguments.update([argument.split('=')])

    task_control(targets, output_file, print_output, task, web, arguments)
