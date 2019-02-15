#!/usr/bin/env python3

import socket
import identity
import time
import threading
import RPi.GPIO as GPIO
import led
import button

PORT = 4961

'''
Purpose: Initialize LEDs and button objects and run initialization flash for LEDs
Inputs:  None
Outputs: array of button objects and LED objects
'''
def init_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    leds = [led.LED(6),led.LED(13),led.LED(12),led.LED(26),led.LED(20),led.LED(21),led.LED(4)]
    buttons = [button.Button(16), button.Button(19)]

    # momentarily flash LEDs to indicate initalization
    [x.on() for x in leds]
    time.sleep(1)
    [x.off() for x in leds]

    return (buttons, leds)

'''
Purpose: Acknowledge the main controller
Inputs:  sock - socket object for communication with controller
Outputs: none
'''
def acknowledge(sock):
    message = 'operation: acknowledge\r\nname: {0}'.format(identity.getName())

    sock.send(bytes(message, 'ascii'))

'''
Purpose: Using UDP, wait for discovery broadcast to determine identity of controller. This
         should block until discovery is successful.
Input:   LED - LED object to use for discovery state
Outputs: address tuple (addr, port) of controller
'''
def discover(LED):
    # Block until the identity of the controller is determined
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', PORT))
    
    LED.setFlashSpeed('slow')
    LED.flash()
    cont_addr = identity.identify(server_socket)
    leds[1].setFlashSpeed('off')

    #close the UDP socket. No longer needed.
    server_socket.close()

    return cont_addr

'''
Purpose: Initiate a TCP connection to the controller. This should block until connection
         is established.
Inputs:  LED - LED object to use for indicating TCP connect.
         addr - string object indicating IP address of controller
Outputs: tcp socket object
'''
def tcp_connect(LED, addr):
    LED.setFlashSpeed('fast')
    LED.flash()

    # Attempt to establish TCP Connection to the controller
    cont_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cont_connection.connect((addr, PORT))
    cont_connection.settimeout(5)

    LED.setFlashSpeed('off')

    return cont_connection

'''
Purpose: perform UDP discovery, connect to the controller over TCP, ack the conntroller after
         it connects, register callbacks for buttons, and start the status thread
Inputs:  leds - array of LED objects
         buttons - array of button objects
Outputs: tuple containing tcp socket to controller and the status thread instance.
'''
def startup(leds, buttons):
    # Block until the identity of the controller is determined
    cont_addr = discover(leds[1])

    # Connect to the controller over TCP
    tcp_sock = tcp_connect(leds[2], cont_addr[0])

    # Ack the controller and indicate connection on LEDs
    acknowledge(tcp_sock)
    leds[0].on()
    
    # Callback function for buttons
    def btn_evt():
        leds[6].toggle_state()
        iden = identity.getIdentity()
        message = 'operation: status\r\n{0}state: {1}\r\n'.format(iden, leds[6].get_state())

        tcp_sock.send(bytes(message, 'ascii'))

    # register callbacks for buttons
    [x.set_event(btn_evt) for x in buttons]
    [x.watch_for_press() for x in buttons]

    #Start main activity
    status_thread = StatusThread(tcp_sock, leds[6])
    status_thread.start()

    return (tcp_sock, status_thread)

'''
Purpose: close the tcp socket and reset led and button objects
Inputs:  leds - array of led objects
         buttons - array of button objects
         sock - tcp connection to server
Outputs: None
'''
def shutdown(leds, buttons, sock):
    sock.close()
    [x.off() for x in leds]
    [x.unwatch() for x in buttons]

'''
Purpose: class representing a thread for sending status every 60 seconds
'''

class StatusThread(threading.Thread):

    def __init__(self, sock, led):
        threading.Thread.__init__(self)
        self.sock = sock
        self.led = led

    '''
    Purpose: Send status of device to the main controller
    Inputs: none
    Outputs: none
    '''
    def send_status(self):
        iden = identity.getIdentity()
        message = 'operation: status\r\n{0}state: {1}\r\n'.format(iden, self.led.get_state())

        self.sock.send(bytes(message, 'ascii'))
    
    '''
    Purpose: wait for an ack from the controller after sending a status. If an ack is not
             recieved, it should retry. If the socket is closed from the controller, a 
             ConnectionError is raised.
    Inputs: none
    Outputs: boolean indicating if an ack was recieved or not.
    '''
    def rec_ack(self):
        try:
            ack = None

            # Loop until the message is acknowledge or timeout
            while ack != 'operation: acknowledge\r\n':
                ack = self.sock.recv(1024)
                ack = ack.decode('ascii')


                if ack == 0:
                    raise ConnectionError

            return True
        except socket.timeout:
            return False

    '''
    Purpose: send a status every 60 seconds. An ack will be immediately checked, timing out
             after 5 seconds. If an ack does not come, status will be sent again. If the
             controller does not ack a second time, the thread should exit.
    Inputs:  none
    Outputs: returns 1 on error
    '''
    def run(self):
        failed_attempts = 0
        send_immediate = False

        while True:
            if not send_immediate:
                time.sleep(20)

            self.send_status()

            #wait for ack
            try:
                if not self.rec_ack():
                    failed_attempts += 1
                    send_immediate = True
            except ConnectionError:
                return 1

            else:
                failed_attemps = 0
                send_immediate = False

            if failed_attempts == 2:
                return 1


buttons, leds = init_GPIO()

tcp_sock, status_thread = startup(leds, buttons)

#wait for status changes
while True:
    try:
        data = tcp_sock.recv(1024)
        if data == 0:
            # controller closed connection. Rediscover
            shutdown(leds, buttons, tcp_sock)
            tcp_sock, status_thread = startup(leds, buttons)
        else:
            data = data.decode('ascii')
            attributes = data.split('\r\n')

            if attributes[0] == 'operation: status change':
                state_attribute = attributes[1].split(': ')
                if state_attribute[0] == 'state' and (state_attribute[1] == 'ON' or state_attribute[1] == 'OFF'):
                    leds[6].on() if state_attribute[1] == 'ON' else leds[6].off()
                    
                    acknowledge(tcp_sock)
    except socket.timeout:
        pass

    #Check if status thread has exited - indicates connection error
    if not status_thread.isAlive():
        #close TCP socket and re-enter discovery
        shutdown(leds, buttons, tcp_sock)
        tcp_sock, status_thread = startup(leds, buttons)

