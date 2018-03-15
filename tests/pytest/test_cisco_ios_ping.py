#!/usr/bin/env python

import pytest
import re

from mock_connection import Connection

MOCK_OUTPUT = '''
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 8.8.8.8, timeout is 2 seconds:
.....
Success rate is 100 percent (5/5)'''


def cisco_ios_ping(connection, destination = None, source = None, df = False):
    if destination is None:
        return {
            "result": "fail",
            "reason": "A destination must be specified."
        }

    command = 'ping {} repeat 3'.format(destination)

    if source is not None:
        command = command + ' source {}'.format(source)
    
    if df:
        command = command + ' df-bit'

    output = MOCK_OUTPUT
    stdout = {}
    regex = 'Success\srate\sis\s(?P<success_rate>[^\s]+)\spercent\s\((?P<echo_replies>\d)\/(?P<echo_requests>\d)\)'

    for line in output.splitlines():
        data = re.search(regex, line)
        if data is not None:
            stdout.update(data.groupdict())

    for key, value in stdout.iteritems():
        try:
            stdout[key] = int(value)
        except ValueError as e:
            pass

    return {
        "result": "success",
        "stdout": stdout
    }
            

@pytest.mark.parametrize('expected_result', [
    {
        "result": "success",
        "stdout": {
            "echo_replies": 5,
            "echo_requests": 5,
            "success_rate": 100
        }
    }
])
def test_cisco_ios_ping_success(expected_result):
    connection = Connection()
    result = cisco_ios_ping(connection, destination = '8.8.8.8')
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [
    {
        "result": "fail",
        "reason": "A destination must be specified."
    }
])
def test_cisco_ios_ping_fail(expected_result):
    connection = Connection()
    result = cisco_ios_ping(connection)
    assert result == expected_result