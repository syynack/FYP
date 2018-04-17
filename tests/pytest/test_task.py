#! /usr/bin/env python

import pytest
from moss.framework.core.task import _construct_task_order, _construct_target
from moss.framework.core.connection import Connection


@pytest.mark.parametrize('test_task_order,expected_result', [(
    ['module_1', 'module_2', 'module_3', 'module_4', 'module_5'],
    [
        {"module": "module_1", "next_module": "module_2"},
        {"module": "module_2", "next_module": "module_3"},
        {"module": "module_3", "next_module": "module_4"},
        {"module": "module_4", "next_module": "module_5"},
        {"module": "module_5", "next_module": ""},
    ]
)])
def test_construct_task_order(test_task_order, expected_result):
    result = _construct_task_order(test_task_order)
    assert result == expected_result


@pytest.mark.parametrize('test_target,test_target_data', [(
    {
        "vendor": "juniper",
        "ip": '8.8.8.8'
    },
    {
        "global_username": "username", 
        "global_password": "password"
    }
)])
def test_construct_target(test_target, test_target_data):
    result = _construct_target(test_target, test_target_data)
    assert isinstance(result, Connection)