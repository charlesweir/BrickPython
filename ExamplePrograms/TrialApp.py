# App
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import sys, os # Python path kludge - omit these 2 lines if BrickPython is installed.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from BrickPython.TkApplication import TkApplication
from BrickPython.Sensor import Sensor, TouchSensor, LightSensor,\
    UltrasonicSensor
import logging

class App(TkApplication):
    '''Application to do stuff.
    '''

    def __init__(self):
        settings = {'1': LightSensor, '2': TouchSensor, '3': UltrasonicSensor }
        TkApplication.__init__(self, settings)
        self.root.wm_title("Trial running")
        for c in "ABCD":
            self.motor(c).zeroPosition()
            self.addActionCoroutine(self.motor(c).runAtConstantSpeed(180))
        for c in settings:
            self.addSensorCoroutine(self.showChanges(c))

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

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG) # All log messages printed to console.
    logging.info( "Starting" )
    app = App()
    app.mainloop()
