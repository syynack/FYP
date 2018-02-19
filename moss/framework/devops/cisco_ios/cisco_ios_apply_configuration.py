#!/usr/bin/env python

from moss.framework.decorators import register

@register(platform = 'cisco_ios', group = 'devops')
def cisco_ios_apply_configuration(connection, configuration_statements):
    if not isinstance(configuration_statements, list):
        return {
            'result': 'fail',
            'stdout': 'Configuration statements must be in a list.'
        }

    output = connection.send_config_set(configuration_statements)

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    return {
        'result': 'success',
        'stdout': output.splitlines()
    }