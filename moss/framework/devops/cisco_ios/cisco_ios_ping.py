#!/usr/bin/env python

from moss.framework.decorators import register

import re

@register(platform = 'cisco_ios', group = 'devops')
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

    output = connection.send_command_expect(command)
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
            



