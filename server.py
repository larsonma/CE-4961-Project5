#!/usr/bin/env python3

import socket
import identity
import time
import RPi.GPIO as GPIO
import led

PORT = 4961

def init_LEDs():
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


inputs, leds = init_LEDs()
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

leds[2].setFlashSpeed('off')
leds[0].on()

print('identity established')
