#!/usr/bin/env python

import pytest
import re

from mock_connection import Connection

OUTPUT_SUCCESS = '''BGP router identifier 1.1.1.1, local AS number 65535
BGP table version is 1, main routing table version 1

Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
192.168.1.1     4 65534       0       0        0    0    0 never    Idle'''

def cisco_ios_get_bgp_summary_success(connection):
    command = 'show ip bgp ipv4 unicast summary'
    output = OUTPUT_SUCCESS

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

        neighbor_data = re.search(neighbor_regex, line)
        if neighbor_data is not None:
            stdout["neighbors"].append(neighbor_data.groupdict())

        neighbor_data = None

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

@pytest.mark.parametrize('expected_result', [
    {
        'result': 'success',
        'stdout': {
            'bgp_table_version': 1,
            'local_as': 65535,
            'neighbors': [
                {
                    'as_number': 65534,
                    'bgp_version': 4,
                    'in_q': 0,
                    'msg_recv': 0,
                    'msg_sent': 0,
                    'neighbor_ip': '192.168.1.1',
                    'out_q': 0,
                    'state_prefix_received': 'Idle',
                    'table_version': 0,
                    'up_down': 'never'
                }
            ],
            'router_id': '1.1.1.1',
            'routing_table_version': 1
        }
    }
])
def test_cisco_ios_get_bgp_summary(expected_result):
    connection = Connection()
    result = cisco_ios_get_bgp_summary_success(connection)
    assert result == expected_result