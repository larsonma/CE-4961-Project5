#!/usr/bin/env python3

import threading
import identity
import socket
import time

class StatusThread(threading.Thread):
    
    def __init__(self, address, state):
        threading.Thread.__init__(self)
        self.state = state
        self.address = address

    def send_status(self):
        iden = identity.getIdentity()
        message = 'operation: status\r\n{0}state: {1}'.format(iden, self.state)

        self.sock.send(bytes(message, 'ascii'))

    def rec_ack(self):
        try:
            self.sock.settimeout(5)
            ack = self.sock.recv(1024)
            #verify ack
            return True
        except socket.timeout:
            return False

    def run(self):
        failed_attempts = 0
        send_immediate = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)

        while True:
            if not send_immediate:
                time.sleep(60)

            self.send_status()

            #wait for ack
            if not self.rec_ack():
                failed_attempts += 1
                send_immediate = True
            else:
                failed_attemps = 0
                send_immediate = False

            if failed_attempts == 2:
                self.sock.close()
                return 1
