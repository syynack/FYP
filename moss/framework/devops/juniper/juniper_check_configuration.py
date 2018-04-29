#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(vendor = 'juniper')
def juniper_check_configuration(connection, config_statements, area = None):
    if not isinstance(config_statements, list):
        return {
            "result": "fail",
            "reason": "config_statements should be a list"
        }

    if not area:
        command = 'show configuration'
    else:
        command = 'show configuration {}'.format(area)

    if connection.check_config_mode():
        connection.exit_config_mode()

    output = connection.send_command(command)

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {"present_config_statements": [], "area": area, "output": output}

    for line in output.splitlines():
        for statement in config_statements:
            if statement in line.strip():
                stdout["present_config_statements"].append(line.strip())

    return {
        "result": "success",
        "stdout": stdout
    }