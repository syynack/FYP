#! /usr/bin/env python

import click

from moss.cli import crypt
from moss.cli import init
from moss.cli import ls
from moss.cli import new
from moss.cli import run


@click.group()
def main():
    pass


#main.add_command(crypt.crypt, name = 'crypt')
main.add_command(init.init, name = 'init')
main.add_command(ls.ls, name = 'list')
#main.add_command(new.new, name = 'new')
main.add_command(run.run, name = 'run')
