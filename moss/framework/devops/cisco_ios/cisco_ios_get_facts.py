#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(vendor = 'cisco_ios')
def cisco_ios_get_facts(connection):
    if connection.check_enable_mode() == False:
        connection.enable()

    command = 'show version'
    output = connection.send_command(command)

    if output is None or 'failed' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    stdout = {}
    uptime = {"uptime": {}}
    interfaces = {"interfaces":[]}

    uptime_regexes = [
        '(?P<minutes>[0-9]{2})\sminutes',
        '(?P<hours>[0-9]{2})\shours',
        '(?P<days>[0-9]{2})\sdays',
        '(?P<years>[0-9]{2})\syears'
    ]

    interface_regex = '(?P<count>[^\s]+)\s(?P<interface_type>[^\s]+)\sinterfaces'

    regexes = [
        'Cisco\sIOS\sSoftware,\s(?P<software>[^\s]+)\sSoftware\s\((?P<software_package>[^\)]+)\),\sVersion\s(?P<software_version>[^,]+),\sRELEASE\sSOFTWARE\s\((?P<release_software>.*)\)',
        'Compiled\s(?P<compiled>.*)\sby',
        '(?P<model>.*)\s\((?P<cpu>.*)\)\sprocessor.*with\s(?P<bytes_of_memory>.*)\sbytes\sof\smemory.',
        'Processor\sboard\sID\s(?P<processor_board_id>[^\s]+)',
        'CPU\sat\s(?P<cpu_clock>[^,]+),',
        'DRAM\sconfiguration\sis\s(?P<dram_configuration>.*)\swide\swith\sparity\s(?P<parity>[^.]+)',
        '(?P<nvram>.*)\sbytes\sof\sNVRAM.',
        '(?P<hostname>.*)\suptime'
    ]

    for line in output.splitlines():
        for regex in regexes:
            data = re.search(regex, line)
            if data is not None:
                data = data.groupdict()
                stdout.update(data)
        for uptime_regex in uptime_regexes:
            uptime_data = re.search(uptime_regex, line)
            if uptime_data is not None:
                uptime_data = uptime_data.groupdict()
                uptime["uptime"].update(uptime_data)
        for int_regex in interface_regex:
            int_data = re.search(interface_regex, line)
            if int_data is not None:
                int_data = int_data.groupdict()
                try:
                    if int_data["interface_type"] != interfaces["interfaces"][-1].get("interface_type"):
                        interfaces["interfaces"].append(int_data)
                except IndexError:
                    interfaces["interfaces"].append(int_data)

    stdout.update(uptime)
    stdout.update(interfaces)

    return {
        "result": "success",
        "stdout": stdout
    }
