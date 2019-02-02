import socket
from identity import getIdentity

PORT = 4961
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', PORT))

while True:
    message, address = server_socket.recvfrom(BUFFER_SIZE)
    message = message.decode('ascii')


    if message == 'operation: discover\r\n':
        dev_id = getIdentity().encode('ascii')
        server_socket.sendto(dev_id, address)
