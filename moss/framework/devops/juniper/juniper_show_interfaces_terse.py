#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(vendor = 'juniper')
def juniper_show_interfaces_terse(connection, interface = None):
    if not interface:
        command = 'show interfaces terse'
    else:
        command = 'show interfaces terse {}'.format(interface)

    connection.enter_cli_mode()
    
    if connection.check_config_mode():
        connection.exit_config_mode()

    output = connection.send_command_timing(command)

    if 'unknown command.' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {"interfaces": []}

    for line in output.splitlines():
        if ("Interface" not in line) and (line != ''):
            line = line.split()
            if 'inet' not in line[0]:
                interface_dict = {}
                interface_dict.update({
                    "name": line[0],
                    "admin_status": line[1],
                    "link_status": line[2]
                })

                if len(line) == 4:
                    interface_dict.update({"proto": line[3]})
                elif len(line) == 5:
                    interface_dict.update({"local": line[4]})
                elif len(line) == 6:
                    interface_dict.update({"remote": line[5]})

                stdout["interfaces"].append(interface_dict)

    return {
        "result": "success",
        "stdout": stdout
    }