#!/usr/bin/env python

from moss.framework.decorators import register

@register(platform = 'cisco_ios', group = 'devops')
def cisco_ios_apply_configuration(connection, config_statements, write_config = False):
    if not isinstance(config_statements, list):
        return {
            'result': 'fail',
            'stdout': 'Configuration statements must be in a list.'
        }

    output = connection.send_config_set(config_statements)

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    write_config_output = None

    if write_config:
        write_config_output = connection.send_command_timing('copy running-configuration startup-configuration')
        if 'Destination filename' in write_config_output:
            write_config_output += connection.send_command_timing('\n')

    return {
        'result': 'success',
        'write_config': write_config,
        'write_config_output': None if write_config_output is None else write_config_output,
        'stdout': output.splitlines()
    }