import socket

DEVICE_TYPE = 'lamp'
BUFFER_SIZE = 1024

def getName():
    return socket.gethostname()

def getDeviceType():
    return DEVICE_TYPE

def getIdentity():
    return 'name: {0}\r\ntype: {1}\r\n'.format(getName(), getDeviceType())

def identify(sock):
    while True:
        message, address = sock.recvfrom(BUFFER_SIZE)
        message = message.decode('ascii')

        if message == 'operation: discover\r\n':
            dev_id = getIdentity().encode('ascii')
            sock.sendto(dev_id, address)

            return address
