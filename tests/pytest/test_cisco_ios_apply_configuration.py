#!/usr/bin/env python

import pytest

from mock_connection import Connection

OUTPUT_SUCCESS = '''config term
Enter configuration commands, one per line.  End with CNTL/Z.
R1(config)#router ospf 1
R1(config-router)#network 192.168.1.0 255.255.255.0 area 0
R1(config-router)#end
R1#'''

OUTPUT_FAIL = '''Invalid input detected ^'''

def cisco_ios_apply_configuration_success(connection, config_statements):
    if not isinstance(config_statements, list):
        return {
            'result': 'fail',
            'stdout': 'Configuration statements must be in a list.'
        }

    output = OUTPUT_SUCCESS

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    return {
        'result': 'success',
        'stdout': output.splitlines()
    }


def cisco_ios_apply_configuration_fail(connection, config_statements):
    if not isinstance(config_statements, list):
        return {
            'result': 'fail',
            'stdout': 'Configuration statements must be in a list.'
        }

    output = OUTPUT_FAIL

    if 'Invalid input detected' in output:
        return {
            'result': 'fail',
            'stdout': output
        }

    return {
        'result': 'success',
        'stdout': output.splitlines()
    }

@pytest.mark.parametrize('config_commands,expected_result', [(
    [
        'router ospf 1',
        'router-id 1.1.1.1',
        'network 192.168.1.0 255.255.255.0 area 0'
    ],
    {
        "result": "success",
        "stdout": [
            "config term",
            "Enter configuration commands, one per line.  End with CNTL/Z.",
            "R1(config)#router ospf 1",
            "R1(config-router)#network 192.168.1.0 255.255.255.0 area 0",
            "R1(config-router)#end",
            "R1#"
        ]
    }
)])
def test_cisco_ios_apply_configuration_success(config_commands, expected_result):
    connection = Connection()
    result = cisco_ios_apply_configuration_success(connection, config_commands)
    assert result == expected_result


@pytest.mark.parametrize('config_commands,expected_result', [(
    'router ospf 1',
    {
        "result": "fail",
        'stdout': 'Configuration statements must be in a list.'
    }
)])
def test_cisco_ios_apply_configuration_fail_not_list(config_commands, expected_result):
    connection = Connection()
    result = cisco_ios_apply_configuration_fail(connection, config_commands)
    assert result == expected_result


@pytest.mark.parametrize('config_commands,expected_result', [(
    [
        'outer ospf 1',
        'router-id 1.1.1.1',
        'network 192.168.1.0 255.255.255.0 area 0'
    ],
    {
        "result": "fail",
        'stdout': 'Invalid input detected ^'
    }
)])
def test_cisco_ios_apply_configuration_fail_command_not_recognised(config_commands, expected_result):
    connection = Connection()
    result = cisco_ios_apply_configuration_fail(connection, config_commands)
    assert result == expected_result