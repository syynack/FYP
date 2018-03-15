#!/usr/bin/env python

from moss.framework.decorators import register

import re

@register(vendor = 'cisco_ios')
def cisco_ios_get_bgp_summary(connection):
    command = 'show ip bgp ipv4 unicast summary'
    output = connection.send_command(command)

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    bgp_regexes = [
        'BGP\srouter\sidentifier\s(?P<router_id>[^,]+),\slocal\sAS\snumber\s(?P<local_as>[^\n]+)',
        'BGP\stable\sversion\sis\s(?P<bgp_table_version>[^,]),\smain\srouting\stable\sversion\s(?P<routing_table_version>[^\n]+)'
    ]

    neighbor_regex = '(?P<neighbor_ip>[^\s]+)\s+(?P<bgp_version>\d)\s+(?P<as_number>[0-9]+)\s+(?P<msg_recv>[0-9]+)\s+(?P<msg_sent>[0-9]+)\s+(?P<table_version>[0-9]+)\s+(?P<in_q>[0-9]+)\s+(?P<out_q>[0-9]+)\s+(?P<up_down>(never|[0-9]+:[0-9]+:[0-9]+))\s+(?P<state_prefix_received>[^\n]+)'

    stdout = {"neighbors": []}

    for line in output.splitlines():
        if 'BGP' in line:
            for regex in bgp_regexes:
                data = re.search(regex, line)
                if data is not None:
                    stdout.update(data.groupdict())
        else:
            data = re.search(neighbor_regex, line)
            if data is not None:
                stdout["neighbors"].append(data.groupdict())

    for key, value in stdout.iteritems():
        try:
            stdout[key] = int(value)
        except (ValueError, TypeError) as e:
            pass

    for index, item in enumerate(stdout["neighbors"]):
        for key, value in item.iteritems():
            try:
               stdout["neighbors"][index][key] = int(value) 
            except (ValueError, TypeError) as e:
                pass

    return {
        "result": "success",
        "stdout": stdout
    }

