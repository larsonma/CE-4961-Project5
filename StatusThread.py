#!/usr/bin/env python3

import threading
import identity
import socket

class StatusThread(threading.Thread):
    
    def __init__(self, address, state):
        threading.Thread.__init__(self)
        self.state = state
        self.address = address

    def send_status(self):
        iden = identity.getIdentity()
        message = 'operation: acknowledge\r\n{0}state: {1}'.format(iden, self.state)

        self.sock.send(bytes(message, 'ascii'))

    def run(self):
        failed_attempts = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.address)

        while True:
            time.sleep(60)

            self.send_status()

            #wait for ack
            try:
                self.sock.settimeout(5)
                ack = sock.recv(1024)
                #verify ack
            except socket.timeout:
                #resent status and exit terminate thread if it fails again
                failed_attempts++

            if failed_attempts == 2:
                self.sock.close()
                return 1
