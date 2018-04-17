#!/usr/bin/env python

import pytest
from moss.framework.core import module

''' Success ModuleResult tests ''' 
@pytest.mark.parametrize('expected_result', [{"result": "success", "delay": 0}])
def test_module_success(expected_result):
    result = module.ModuleResult.success()
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [{"result": "success", "delay": 60}])
def test_module_success_with_delay(expected_result):
    result = module.ModuleResult.success(delay = 60)
    assert result == expected_result


''' Fail ModuleResult tests ''' 
@pytest.mark.parametrize('expected_result', [{"result": "fail"}])
def test_module_fail(expected_result):
    result = module.ModuleResult.fail()
    assert result == expected_result


''' Branch ModuleResult tests ''' 
@pytest.mark.parametrize('expected_result', [{"result": "branch", "delay": 0, "branching_module": "branching_module"}])
def test_module_branch(expected_result):
    result = module.ModuleResult.branch('branching_module')
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [{"result": "branch", "delay": 60, "branching_module": "branching_module"}])
def test_module_branch_with_delay(expected_result):
    result = module.ModuleResult.branch('branching_module', delay = 60)
    assert result == expected_result


''' Retry ModuleResult tests ''' 
@pytest.mark.parametrize('expected_result', [{"result": "retry", "delay": 5}])
def test_module_retry(expected_result):
    result = module.ModuleResult.retry()
    assert result == expected_result


@pytest.mark.parametrize('expected_result', [{"result": "retry", "delay": 60}])
def test_module_retry_with_delay(expected_result):
    result = module.ModuleResult.retry(delay = 60)
    assert result == expected_result


''' End ModuleResult tests ''' 
@pytest.mark.parametrize('expected_result', [{"result": "end"}])
def test_module_end(expected_result):
    result = module.ModuleResult.end()
    assert result == expected_result