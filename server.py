#!/usr/bin/env python3

import socket
import identity
import time
import threading
import RPi.GPIO as GPIO
import led
from StatusThread import *

PORT = 4961
state = 'OFF'

def init_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    leds = [led.LED(6),led.LED(13),led.LED(12),led.LED(26),led.LED(20),led.LED(21),led.LED(4)]
    inputs = [16,19]

    #GPIO.setup(outputs, GPIO.OUT)
    GPIO.setup(inputs, GPIO.IN)

    # momentarily flash LEDs to indicate initalization
    [x.on() for x in leds]
    time.sleep(1)
    [x.off() for x in leds]

    return (inputs, leds)

def acknowledge(sock):
    message = 'operation: acknowledge\r\nname: {0}'.format(identity.getName())

    sock.send(bytes(message, 'ascii'))

def discover(LED):
    # Block until the identity of the controller is determined
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', PORT))
    
    LED.setFlashSpeed('slow')
    LED.flash()
    cont_addr = identity.identify(server_socket)
    leds[1].setFlashSpeed('off')

    server_socket.close()

    return cont_addr

def tcp_connect(LED, addr):
    LED.setFlashSpeed('fast')
    LED.flash()

    # Attempt to establish TCP Connection to the controller
    cont_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cont_connection.connect((addr, PORT))
    cont_connection.setblocking(False)

    LED.setFlashSpeed('off')

    return cont_connection

def startup(leds):
    # Block until the identity of the controller is determined
    cont_addr = discover(leds[1])

    # Connect to the controller over TCP
    tcp_sock = tcp_connect(leds[2], cont_addr[0])

    # Ack the controller and indicate connection on LEDs
    acknowledge(tcp_sock)
    leds[0].on()

    #Start main activity
    status_thread = StatusThread((cont_addr[0], PORT), state)
    status_thread.start()

    return (tcp_sock, status_thread)


inputs, leds = init_GPIO()

tcp_sock, status_thread = startup(leds)

#wait for status changes
while True:
    try:
        data = tcp_sock.recv(1024)
        if data == 0:
            #TODO cleanup properly
            tcp_sock.close()
            leds[0].off()
            tcp_sock, status_thread = startup(leds)
        else:
            data = data.decode('ascii')
            attributes = data.split('\\r\\n')
            
            if attributes[0] == 'operation: status change':
                state_attribute = attributes[3].split(': ')
                if state_attribute[0] == 'state' and (state_attribute[1] == 'ON' or state_attribute[1] == 'OFF'):
                    state = state_attribute[1]
                    leds[6].on() if state == 'ON' else leds[6].off()
                    
                    acknowledge(tcp_sock)
    except BlockingIOError:
        pass

    #Check if status thread has exited - indicates connection error
    if not status_thread.isAlive():
        print('Did not respond to status')

        #close TCP socket and re-enter discovery
        tcp_sock.close()
        leds[0].off()
        tcp_sock, status_thread = startup(leds)

