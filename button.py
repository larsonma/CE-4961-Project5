#!/usr/bin/env python3

import RPi.GPIO as GPIO

'''
Purpose: wrap a button GPIO bin with callback capabilities.
'''
class Button:

    def __init__(self, pin, event=None):
        self.pin = pin
        self.event = event

        GPIO.setup(self.pin, GPIO.IN)
    
    '''
    Purpose: callback function for the button's GPIO pin. calls the passed event.
    Inputs:  channel - pin number of GPIO pin that fired callback.
    Outpus:  none
    '''
    def button_callback(self, channel):
        self.event()
    
    '''
    Purpose: register GPIO pin with callback. Should only be called after setting event.
    Input:   none
    Output:  none
    '''
    def watch_for_press(self):
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.button_callback, bouncetime=200)

    '''
    Purpose: remove edge detection from GPIO pin. Will prevent callback from being called.
    Input:   none
    Output:  none
    '''
    def unwatch(self):
        GPIO.remove_event_detect(self.pin)

    '''
    Purpose: set a custom even to call when the button is pressed.
    Input:   event - function to call when button is pressed
    Output:  none
    '''
    def set_event(self, event):
        self.unwatch()
        self.event = event
