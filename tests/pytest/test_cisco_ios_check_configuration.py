#!/usr/bin/env python

import pytest

from mock_connection import Connection

MOCK_CONFIG_SUCCESS = '''!
router ospf 1
  router-id 1.1.1.1
  network 192.168.1.0 255.255.255.0 area 0
  network 192.168.2.0 255.255.255.0 area 1
!'''

MOCK_CONFIG_FAIL = '''Unknown'''


def cisco_ios_check_configuration_success(connection, config_statements, area = None):
    if not isinstance(config_statements, list):
        return {
            "result": "fail",
            "reason": "config_statements should be a list"
        }

    if not area:
        command = 'show running-config'
    else:
        command = 'show running-config | section {}'.format(area)

    output = MOCK_CONFIG_SUCCESS

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {"present_config_statements": [], "area": area}

    for line in output.splitlines():
        if line.strip() in config_statements:
            stdout["present_config_statements"].append(line.strip())

    return {
        "result": "success",
        "stdout": stdout
    }


def cisco_ios_check_configuration_fail(connection, config_statements, area = None):
    if not isinstance(config_statements, list):
        return {
            "result": "fail",
            "reason": "config_statements should be a list"
        }

    if not area:
        command = 'show running-config'
    else:
        command = 'show running-config | section {}'.format(area)

    output = MOCK_CONFIG_FAIL

    if output is None or 'Unknown' in output:
        return {
            "result": "fail",
            "reason": output
        }

    stdout = {"present_config_statements": [], "area": area}

    for line in output.splitlines():
        if line.strip() in config_statements:
            stdout["present_config_statements"].append(line.strip())

    return {
        "result": "success",
        "stdout": stdout
    }


@pytest.mark.parametrize('config_statements,expected_result', [(
    [
        'router-id 1.1.1.1'
    ],
    {
        "result": "success",
        "stdout": {"present_config_statements": ['router-id 1.1.1.1'], "area": None}
    }
)])
def test_cisco_ios_check_configuration_success(config_statements, expected_result):
    connection = Connection()
    result = cisco_ios_check_configuration_success(connection, config_statements)
    assert result == expected_result


@pytest.mark.parametrize('config_statements,expected_result', [(
    'router-id 1.1.1.1',
    {
        "result": "fail",
        "reason": "config_statements should be a list"
    }
)])
def test_cisco_ios_check_configuration_fail_not_list(config_statements, expected_result):
    connection = Connection()
    result = cisco_ios_check_configuration_fail(connection, config_statements)
    assert result == expected_result


@pytest.mark.parametrize('config_statements,expected_result', [(
    [
        'router-id 1.1.1.1'
    ],
    {
        "result": "fail",
        "reason": MOCK_CONFIG_FAIL
    }
)])
def test_cisco_ios_check_configuration_fail_returned_unknown(config_statements, expected_result):
    connection = Connection()
    result = cisco_ios_check_configuration_fail(connection, config_statements)
    assert result == expected_result
