#!/usr/bin/env python3

import socket
import identity
import time
import threading
import RPi.GPIO as GPIO
import led
import * from StatusThread

PORT = 4961
state = 'OFF'

def init_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    leds = [led.LED(6),led.LED(13),led.LED(12),led.LED(26),led.LED(20),led.LED(21),led.LED(4)]
    inputs = [16,19]

    i#GPIO.setup(outputs, GPIO.OUT)
    GPIO.setup(inputs, GPIO.IN)

    # momentarily flash LEDs to indicate initalization
    [x.on() for x in leds]
    time.sleep(1)
    [x.off() for x in leds]

    return (inputs, leds)

def acknowledge(sock):
    message = 'operation: acknowledge\r\nname: {0}'.format(identity.getName())

    sock.send(bytes(message, 'ascii'))

inputs, leds = init_GPIO()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', PORT))


# Block until the identity of the controller is determined
leds[1].setFlashSpeed('slow')
leds[1].flash()
cont_addr = identity.identify(server_socket)
leds[1].setFlashSpeed('off')


leds[2].setFlashSpeed('fast')
leds[2].flash()

# Attempt to establish TCP Connection to the controller
cont_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cont_connection.connect(cont_addr)

# Ack the controller and indicate connection on LEDs
acknowledge(cont_connection)
leds[2].setFlashSpeed('off')
leds[0].on()

#Start main activity
status_thread = StatusThread(cont_addr, state)
status_thread.start()

#wait for status changes
while True:
    data = cont_connection.recv(1024)
    data = data.decode('ascii')
    attributes = data.split('\r\n')

    if attributes[0] == 'operation: status change':
        state_attribute = attributes[3].split(': ')
        if state_attribute[0] == 'state' and (state_attribute[1] == 'ON' or state_attribute[1] == 'OFF'):
            state = state_attribute[1]
            led[6].on() if state == 'ON' else led[6].off()

            acknowledge(cont_connection)

    #Check if status thread has exited - indicates connection error
    if not status_thread.is_alive():
        #close TCP socket and re-enter discovery
        cont_connection.close()

print('identity established')
