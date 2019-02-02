import socket

DEVICE_TYPE = 'lamp'

def getName():
    return socket.gethostname()

def getDeviceType():
    return DEVICE_TYPE

def getIdentity():
    return 'name: {0}\r\ntype: {1}\r\n'.format(getName(), getDeviceType())
