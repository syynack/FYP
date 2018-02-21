#! /usr/bin/env python

from moss.framework.core.registry import registry, _run_registered_device_operation

def register(vendor = None, group = 'modules'):
    '''
    Summary:
    Takes modules registered with the @register decorator. Aim is to only allow
    registered modules to be executed. The modules are appended to a list
    which is ordered by platform.

    Arguments:
    platform        string, platform module is intended to be used for
    group           string, group where the module should be stored in the registry

    Returns:
    func
    '''

    def decorator(func):
        if isinstance(vendor, str):
            if 'moss.framework.devops.' in str(func.__module__):
                registry('devops', vendor, func)
            else:
                registry(group, vendor, func)
        elif isinstance(vendor, list):
            for element in vendor:
                if 'moss.framework.devops.' in str(func.__module__):
                    registry('devops', element, func)
                else:
                    registry(group, element, func)
        return func
    return decorator


def run(device_operation, **kwargs):
    '''
    Summary:
    Allows modules to be run through the use of decorators. For example the user
    can write @moss.run('linux_get_system_uptime', connection) decorating a function
    to return the information.
    '''

    def _decorator(func):
        def wrapper(connection):
            return _run_registered_device_operation(connection.device_type, device_operation, connection, **kwargs)
        return wrapper
    return _decorator
