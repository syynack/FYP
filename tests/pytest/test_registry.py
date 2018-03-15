#! /usr/bin/env python

import pytest
import moss
from moss.framework.core.registry import registered_operations
from moss.framework.decorators import register

@register('pytest_vendor', group = 'devops')
def test_func_devops():
    pass


@register('pytest_vendor')
def test_func_modules():
    pass


@register('pytest_vendor', group = 'custom_group')
def test_func_custom_group():
    pass


@pytest.mark.parametrize('expected_result', [{"test_func_devops": test_func_devops}])
def test_register_devops(expected_result):
    ''' Test registry addition for device operations '''
    test_func_devops()
    result = registered_operations['devops']['pytest_vendor']
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [{"test_func_modules": test_func_modules}])
def test_register_modules(expected_result):
    ''' Test registry addition for modules '''
    test_func_modules()
    result = registered_operations['modules']['pytest_vendor']
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [{"test_func_custom_group": test_func_custom_group}])
def test_register_custom_group(expected_result):
    ''' Test registry addition for custom groups '''
    test_func_custom_group()
    result = registered_operations['custom_group']['pytest_vendor']
    assert result == expected_result