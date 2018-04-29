#!/usr/bin/env python

from moss.framework.decorators import register

@register(vendor = 'juniper')
def juniper_apply_configuration(connection, config_statements):
    if not isinstance(config_statements, list):
        return {
            'result': 'fail',
            'stdout': 'Configuration statements must be in a list.'
        }

    if not connection.check_config_mode():
        connection.config_mode()

    output = connection.send_config_set(config_statements)

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }
    
    committed = connection.commit(comment = 'Configuration committed by MOSS, applying {}'.format(config_statements), and_quit = True)
    committed = True if committed else False

    return {
        'result': 'success',
        'stdout': output.splitlines(),
        'committed': committed
    }