#!/usr/bin/env python

import re

from moss.framework.decorators import register

@register(vendor = 'juniper')
def juniper_get_bgp_peers(connection, peer = None):
    if not peer:
        command = 'show bgp neighbor'
    else:
        command = 'show bgp neighbor {}'.format(peer)

    connection.enter_cli_mode()
    
    if connection.check_config_mode():
        connection.exit_config_mode()

    output = connection.send_command_timing(command)

    if 'unknown command.' in output:
        return {
            "result": "fail",
            "reason": output
        }

    peer_regex = 'Peer:\s(?P<peer_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})((\+(?P<peer_port>\d+))|)\sAS\s(?P<peer_as>\d+)\s+Local:\s(((?P<local_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))\+(?P<local_port>\d+)|.*)\sAS\s(?P<local_as>\d+)'
    bgp_regexes = [
        'Type:\s(?P<peering_type>[^\s]+).*State:\s(?P<peering_state>[^\s]+).*Flags:\s(?P<peering_flags>[^\n]+)',
        'Last\sState:\s(?P<last_state>[^\s]+).*Last\sEvent:\s(?P<last_event>[^\n]+)',
        'Last\sError:\s(?P<last_error>[^\n]+)',
        'Options:\s\<(?P<options>[^\>]+)',
        'Holdtime:\s(?P<holdtime>\d+)\sPreference:\s(?P<route_preference>\d+)\sLocal\sAS:\s\d+\sLocal\sSystem\sAS:\s\d+',
        'Number\sof\sflaps:\s(?P<flaps>\d+)'
    ]

    stdout = {"peers": []}
    peer_dict = {}

    for line in output.splitlines():
        if 'Peer:' in line:
            peer_dict = {}
            data = re.search(peer_regex, line)
            if data is not None:
                peer_dict.update(data.groupdict())
        elif line == '':
            if peer_dict:
                stdout["peers"].append(peer_dict)
        else:
            for regex in bgp_regexes:
                data = re.search(regex, line)
                if data is not None:
                    peer_dict.update(data.groupdict())

    stdout["peers"].append(peer_dict)

    return {
        "result": "success",
        "stdout": stdout
    }