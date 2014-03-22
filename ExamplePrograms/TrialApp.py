# App
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import sys, os # Python path kludge - omit these 2 lines if BrickPython is installed.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from BrickPython.TkApplication import TkApplication
from BrickPython.Sensor import Sensor, TouchSensor
import logging

class App(TkApplication):
    '''Application to do stuff.
    '''

    def __init__(self):
        settings = {'3': Sensor.ULTRASONIC_CONT } #, '2': TouchSensor }
        TkApplication.__init__(self, settings)
        self.root.wm_title("Trial running")
        for c in "ABCD":
            self.motor(c).zeroPosition()
        for c in settings:
            self.addSensorCoroutine(self.showSensorValues(c))

    def showChanges(self, sensorId):
        sensor = self.sensor(sensorId)
        while True:
            for i in sensor.waitForChange(): yield
            print sensor

    def showSensorValues(self, sensorId):
        sensor = self.sensor(sensorId)
        while True:
            for i in self.waitMilliseconds(1000): yield
            print sensor

##        for c in "ABCD":
##            motor= self.motor(c)
##            for i in motor.moveTo(90*2): yield
##            for i in motor.moveTo(0): yield
##

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG) # All log messages printed to console.
    logging.info( "Starting" )
    app = App()
    app.mainloop()
