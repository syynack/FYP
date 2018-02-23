#! /usr/bin/env python

import sys

from moss.framework.utils import colour
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException

class Connection():
    '''
    Summary:
    Returns netmiko SSH connection to device using variables as defined
    Paramater defaults set as per http://netmiko.readthedocs.io/en/latest/classes/base_connection.html

    Takes:
    vendor:             string, running OS on the device e.g. linux, cisco_ios, juniper
    ip:                 string, IPv4/v6 address of target device
    username:           string, username to authenticate against
    password:           string, password to authenticate with
    port:               int, port to connect to
    timeout:            int, global connection timeout
    session_timeout:    int, timeout for parallel requests

    Returns:
    Connection object

    '''

    def __init__(self, vendor='', ip='', username='', password='', port=22, timeout=20, session_timeout=60):
        self.vendor = vendor
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.session_timeout = session_timeout
        self.facts = {}


    def get_connection(self):
        '''
        Summary:
        Creates a netmiko SSH object from self data

        Returns:
        netmiko SSH object
        '''

        try:
            connection = ConnectHandler(
                device_type = self.vendor,
                ip = self.ip,
                username = self.username,
                password = self.password,
                port = self.port,
                timeout = self.timeout,
                session_timeout = self.session_timeout
            )
        except NetMikoTimeoutException as e:
            print str(e)
            sys.exit(1)

        return connection


    def close(self, connection):
        '''
        Summary:
        Function to close connection due to root connections to linux boxes not closing correctly

        '''

        if connection.username == 'root' and connection.device_type == 'linux':
            # Disconnecting from a Linux box with user root is currently not supported, see https://github.com/ktbyers/netmiko/issues/492
            # if the issue is closed, matt was lazy. Please update this.
            return

        try:
            connection.disconnect()
        except:
            raise
