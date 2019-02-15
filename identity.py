#!/usr/bin/env python3

import socket

DEVICE_TYPE = 'lamp'
BUFFER_SIZE = 1024

'''
Purpose: get hostname of device
Inputs:  none
Outputs: none
'''
def getName():
    return socket.gethostname()

'''
Purpose: get the device type
Inputs:   none
Output:  none
'''
def getDeviceType():
    return DEVICE_TYPE

'''
Purpose: get the identity of the device as a string
Inputs:  none
Outputs: string representing device identity
'''
def getIdentity():
    return 'name: {0}\r\ntype: {1}\r\n'.format(getName(), getDeviceType())

'''
Purpose: establish identity of server, and send identity of this device, using UDP.
Inputs:  sock - UDP socket to watch for discovery.
Output:  address tuple (addr, port) of controller.
'''
def identify(sock):
    while True:
        message, address = sock.recvfrom(BUFFER_SIZE)
        message = message.decode('ascii')

        if message == 'operation: discover\r\n':
            dev_id = getIdentity().encode('ascii')
            sock.sendto(dev_id, address)

            return address
