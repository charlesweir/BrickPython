# CommandLineApplication class.  Provides a dummy scheduler for BrickPiWrapper.
# Applications using the BrickPi derive from this, implementing appropriate functionality.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.


from BrickPiWrapper import BrickPiWrapper
import time

class CommandLineApplication(BrickPiWrapper):
    '''
    Main application class for command-line only apps.  Doesn't support user input.
    '''

    def __init__(self, sensorConfiguration={}):
        '''Initialization: *sensorConfiguration* is a map, e.g. {'1': Sensor.TYPE_SENSOR_ULTRASONIC_CONT}
        as passed to BrickPiWrapper'''
        BrickPiWrapper.__init__(self, sensorConfiguration )

    def mainloop(self):
        'The main loop for the application - call this after initialization.  Never returns.'
        while True:
            self.doWork()
            time.sleep(self.timeMillisToNextCall() / 1000.0)

