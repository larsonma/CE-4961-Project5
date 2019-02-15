#!/usr/bin/env python3

import threading
import RPi.GPIO as GPIO

'''
Purpose: provide easy control of LED GPIO pins and provide flashing ability
         that runs in a seperate thread.
'''
class LED:

    modes = {'slow': 1.0, 'fast': 0.5, 'faster': 0.25}

    def __init__(self, pin):
        self.pin = pin
        self.state = 'OFF'
        self.timer = None
        self.mode = 'off'

        GPIO.setup([self.pin], GPIO.OUT)

    '''
    Purpose: turn LED off by setting GPIO pin high
    Inputs:  none
    Outpu:  none
    '''
    def off(self):
        self.state = 'OFF'
        GPIO.output(self.pin, GPIO.HIGH)

    '''
    Purpose: turn LED on by setting GPIO pin low
    Inputs:  none
    Output:  none
    '''
    def on(self):
        self.state = 'ON'
        GPIO.output(self.pin, GPIO.LOW)

    '''
    Purpose: get the state of the LED
    Inputs:  none
    Output:  'OFF' or 'ON' depending on LED state
    '''
    def get_state(self):
        return self.state

    '''
    Purpose: toggle the LED. If the LED is on, the LED is turned off and vice versa
    Inputs:  none
    Output:  none
    '''
    def toggle_state(self):
        if self.state == 'OFF':
            self.state = 'ON'
            self.on()
        else:
            self.state = 'OFF'
            self.off()

    '''
    Purpose: kicks off the flash activity of the LED by toggling the LED based on a timer.
    Inputs:  none
    Output:  none
    '''
    def toggle(self):

        if self.mode == 'off':
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
                self.off()
        else:
       	    self.toggle_state()
 
            self.timer = threading.Timer(self.modes[self.mode], self.toggle)
            self.timer.start()
    
    '''
    Purpose: kick off the flash behavior of the LED object.
    Inputs:  none
    Output:  none
    '''
    def flash(self):
        self.toggle()

    
    '''
    Purpose: Change the flash speed of the LED.
    Inputs:  mode - flash speed mode, as defined by the modes constant
    Output:  none
    '''
    def setFlashSpeed(self, mode='off'):
        if mode == 'off' or mode == 'slow' or mode == 'fast' or mode == 'faster':
            if mode == 'off':
                self.off()

            self.mode = mode
        else:
            raise ValueError('Invalid LED mode: {0}'.format(mode))



