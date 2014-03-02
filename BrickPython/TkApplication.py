# TkApplication class.  Superclass for applications using the Tkinter framework
#
# Applications using the BrickPi derive from this, implementing appropriate functionality.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import Tkinter as tk

from BrickPiWrapper import *
import logging

# TODO: How to stop two coroutines running at once on the same port?

class TkApplication(BrickPiWrapper):
    '''
    Main application class using the Tk toolkit.  Implements the regular calls required by the scheduler.

    The default implementation creates a simple small window which
    exits when it receives the 'Q' key, but this can be changed by overriding the doInitialization() method.

    '''

    def __init__(self, sensorConfiguration={}):
        '''Initialization: *sensorConfiguration* is a map, e.g. {'1': Sensor.ULTRASONIC_CONT}
        as passed to BrickPiWrapper'''
        BrickPiWrapper.__init__(self, sensorConfiguration )
        self.root = tk.Tk()

        self.doInitialization()

        self.timerTick()

    def doInitialization(self):
        'Default initialization function with a simple window - override if you want something different'
        self.root.geometry('300x200')
        self.label = tk.Label(text="BrickPi")
        self.label.pack()
        self.root.bind('<KeyPress>', self.onKeyPress)


    def mainloop(self):
        'The main loop for the application - call this after initialization.  Returns on exit.'
        self.root.mainloop()

    def timerTick(self):
        # Private: Does all the coroutine processing, every 20ms or so.
        self.doWork()
        self.root.after(int(self.timeMillisToNextCall()), self.timerTick)

    def onKeyPress(self, event):
        '''Default key press handling - answers True if it's handled the key.
        Override this function to add extra keypress handling. '''
        char = event.char
        if char == "": # Key such as shift or control...
            pass
        elif(char=='q'):
            logging.info( "Application terminated")
            self.root.destroy()
        else:
            return False
        return True


