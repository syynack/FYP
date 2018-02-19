#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(platform = 'cisco_ios', group = 'devops')
def cisco_ios_show_interfaces(connection):
    command = 'show interfaces'
    output = connection.send_command(command)

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {}
    first_regex = '(?P<name>.*)\sis\s(?P<operational_status>(up|down)),\sline\sprotocol\sis\s(?P<line_status>(up|down))\s+'
    regex_list = [
        'Hardware\sis\s(?P<hardware>[^,]+),\saddress\sis\s(?P<hardware_address>[^\s]+)',
        'Internet\saddress\sis\s(?P<address>[^\s]+)',
        'MTU\s(?P<mtu>[^,]+),\sBW\s(?P<bandwidth>[^,]+),\sDLY\s(?P<delay>[^,]+)',
        'reliability\s(?P<reliability>[^,]+),\stxload\s(?P<txload>[^,]+),\srxload\s(?P<rxload>[^\s]+)',
        '(?P<packets_input>[0-9]*)\spackets\sinput,\s(?P<packets_input_bytes>[0-9]*)\sbytes',
        'Encapsulation\s(?P<encapsulation>[^,]+),',
        'Received\s(?P<recv_brdcsts>[^\s]+)\sbroadcasts,\s(?P<recv_rnts>[^\s]+)\srunts,\s(?P<recv_gnts>[^\s]+)\sgiants,\s(?P<recv_thrttls>[^\s]+)\sthrottles',
        '(?P<input_errors>[0-9]*)\sinput\serrors,\s(?P<crc_errors>[0-9]*)\sCRC,\s(?P<frame_errors>[0-9]*)\sframe,\s(?P<overruns>[0-9]*)\soverrun,\s(?P<ignored>[0-9]*)\signored',
        '(?P<packets_output>[0-9]*)\spackets\soutput,\s(?P<packets_output_bytes>[0-9]*)\sbytes,\s(?P<underruns>[0-9]*)\sunderruns',
        'Queueing\sstrategy:\s(?P<queueing_strategy>[^\n]+)'
    ]

    for line in output.splitlines():
        if 'line protocol' in line:
            data = re.search(first_regex, line)
            if data is not None:
                data = data.groupdict()
                interface_name = data.get('name')
                stdout[interface_name] = {}
                stdout[interface_name].update(data)
        else:
            for regex in regex_list:
                data = re.search(regex, line)
                if data is not None:
                    data = data.groupdict()
                    stdout[interface_name].update(data)

    for stdout_key, stdout_value in stdout.iteritems():
        for interface_key, interface_value in stdout_value.iteritems():
            try:
                stdout[stdout_key][interface_key] = int(interface_value)
            except ValueError as e:
                pass

    return {
        "result": "success",
        "stdout": stdout
    }

