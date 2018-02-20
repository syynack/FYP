#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(platform = 'cisco_ios', group = 'devops')
def cisco_ios_check_configuration(connection, config_statements, area = None):
    if not isinstance(config_statements, list):
        return {
            "result": "fail",
            "reason": "config_statements should be a list"
        }

    if not area:
        command = 'show running-config'
    else:
        command = 'show running-config | section {}'.format(area)

    output = connection.send_command(command)

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {"present_config_statements": [], "area": area}

    for line in output.splitlines():
        if line.strip() in config_statements:
            stdout["present_config_statements"].append(line.strip())

    return {
        "result": "success",
        "stdout": stdout
    }
            

