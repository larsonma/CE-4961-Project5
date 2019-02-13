#!/usr/bin/env python3

import threading
import RPi.GPIO as GPIO

class LED:

    modes = {'slow': 1.0, 'fast': 0.5, 'faster': 0.25}

    def __init__(self, pin):
        self.pin = pin
        self.state = 'off'
        self.timer = None
        self.mode = 'off'

        GPIO.setup([self.pin], GPIO.OUT)

    def off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def on(self):
        GPIO.output(self.pin, GPIO.LOW)

    def toggle(self):

        if self.mode == 'off':
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
        else:
            if self.state == 'off':
                self.state = 'on'
                self.on()
            else:
                self.state = 'off'
                self.off()
        
            self.timer = threading.Timer(self.modes[self.mode], self.toggle)
            self.timer.start()

    def flash(self):
        self.toggle()


    def setFlashSpeed(self, mode='off'):
        if mode == 'off' or mode == 'slow' or mode == 'fast' or mode == 'faster':
            self.mode = mode
        else:
            raise ValueError('Invalid LED mode: {0}'.format(mode))



