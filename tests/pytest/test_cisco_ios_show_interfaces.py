#!/usr/bin/env python

import pytest
import re

from mock_connection import Connection

MOCK_OUTPUT = '''

FastEthernet0/0 is up, line protocol is up
  Hardware is Gt96k FE, address is c401.0706.0000 (bia c401.0706.0000)
  Internet address is 192.168.253.130/24
  MTU 1500 bytes, BW 10000 Kbit/sec, DLY 1000 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Half-duplex, 10Mb/s, 100BaseTX/FX
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:00, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes
     Received 0 broadcasts, 0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog
     0 input packets with dribble condition detected
     0 packets output, 0 bytes, 0 underruns
     0 output errors, 0 collisions, 1 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier
     0 output buffer failures, 0 output buffers swapped out
     
'''

def cisco_ios_show_interfaces(connection):
    command = 'show interfaces'
    output = MOCK_OUTPUT

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


@pytest.mark.parametrize('expected_result', [
    {
        "result": "success",
        "stdout": [
            {
                "address": "192.168.253.130/24",
                "bandwidth": "10000 Kbit/sec",
                "crc_errors": 0,
                "delay": "1000 usec",
                "encapsulation": "ARPA",
                "frame_errors": 0,
                "hardware": "Gt96k FE",
                "hardware_address": "c401.0706.0000",
                "ignored": 0,
                "input_errors": 0,
                "line_status": "up",
                "mtu": "1500 bytes",
                "name": "FastEthernet0/0",
                "operational_status": "up",
                "overruns": 0,
                "packets_input": 0,
                "packets_input_bytes": 0,
                "packets_output": 0,
                "packets_output_bytes": 0,
                "queueing_strategy": "fifo",
                "recv_brdcsts": 0,
                "recv_gnts": 0,
                "recv_rnts": 0,
                "recv_thrttls": 0,
                "reliability": "255/255",
                "rxload": "1/255",
                "txload": "1/255",
                "underruns": 0
            }
        ]
    }
])
def test_cisco_ios_show_interfaces_success(expected_result):
    connection = Connection()
    result = cisco_ios_show_interfaces(connection)
    assert result == expected_result