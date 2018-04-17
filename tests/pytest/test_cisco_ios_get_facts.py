#!/usr/bin/env python

import pytest
import re

from mock_connection import Connection

MOCK_OUTPUT = '''Cisco IOS Software, 3700 Software (C3745-ADVIPSERVICESK9-M), Version 12.4(25d), RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2010 by Cisco Systems, Inc.
Compiled Wed 18-Aug-10 08:18 by prod_rel_team

ROM: ROMMON Emulation Microcode
ROM: 3700 Software (C3745-ADVIPSERVICESK9-M), Version 12.4(25d), RELEASE SOFTWARE (fc1)

R1 uptime is 18 minutes
System returned to ROM by unknown reload cause - suspect boot_data[BOOT_COUNT] 0x0, BOOT_COUNT 0, BOOTDATA 19
System image file is "tftp://255.255.255.255/unknown"


This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

Cisco 3745 (R7000) processor (revision 2.0) with 249856K/12288K bytes of memory.
Processor board ID FTX0945W0MY
R7000 CPU at 350MHz, Implementation 39, Rev 2.1, 256KB L2, 512KB L3 Cache
18 FastEthernet interfaces
4 Serial interfaces
DRAM configuration is 64 bits wide with parity enabled.
151K bytes of NVRAM.

Configuration register is 0x2102'''


def cisco_ios_get_facts_success(connection):
    if connection.check_enable_mode() == False:
        connection.enable()

    command = 'show version'
    output = MOCK_OUTPUT

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


@pytest.mark.parametrize('expected_result', [{
    "result": "success",
        "stdout": {
            "bytes_of_memory": "249856K/12288K",
            "compiled": "Wed 18-Aug-10 08:18",
            "cpu": "R7000",
            "cpu_clock": "350MHz",
            "dram_configuration": "64 bits",
            "hostname": "R1",
            "interfaces": [
                {
                    "count": "18",
                    "interface_type": "FastEthernet"
                },
                {
                    "count": "4",
                    "interface_type": "Serial"
                }
            ],
            "model": "Cisco 3745",
            "nvram": "151K",
            "parity": "enabled",
            "processor_board_id": "FTX0945W0MY",
            "release_software": "fc1",
            "software": "3700",
            "software_package": "C3745-ADVIPSERVICESK9-M",
            "software_version": "12.4(25d)",
            "uptime": {
                "minutes": "18"
            }
        }
    }
])
def test_cisco_ios_get_facts(expected_result):
    connection = Connection()
    result = cisco_ios_get_facts_success(connection)
    assert result == expected_result