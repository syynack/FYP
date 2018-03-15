#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(vendor = 'cisco_ios')
def cisco_ios_show_interfaces(connection):
    command = 'show interfaces'
    output = connection.send_command(command)

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = []
    interface_dict = {}
    regex_list = [
        '(?P<name>.*)\sis\s(?P<operational_status>[^,]+),\sline\sprotocol\sis\s(?P<line_status>[^\n]+)',
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

    for index, line in enumerate(output.splitlines()):
        if 'line protocol' in line:
            if interface_dict:
                stdout.append(interface_dict)
            interface_dict = {}
        for regex in regex_list:
            data = re.search(regex, line)
            if data is not None:
                interface_dict.update(data.groupdict())
        if index + 1 == len(output.splitlines()):
            stdout.append(interface_dict)

    for interface in stdout:
        for key, value in interface.iteritems():
            try:
                interface[key] = int(value)
            except ValueError as e:
                pass

    return {
        "result": "success",
        "stdout": stdout
    }