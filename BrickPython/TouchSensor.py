# TouchSensor - represents an NXT touch sensor supported by the BrickPython library
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

from Sensor import Sensor

class TouchSensor(Sensor):
    '''TouchSensor, representing a sensor attached to one of the BrickPi ports.
    Parameter *port* may be either a value (BrickPi.PORT_1) or an integer '1'-'5'

    Just using the BrickPi TYPE_SENSOR_TOUCH didn't work for me; hence this.

    value() is True if the button is pressed; False otherwise.
    '''
    def __init__(self, port):
        Sensor.__init__(self, port, Sensor.RAW)
        #: Function that gets called with new value as parameter when the value changes - default, none.
        self.callbackFunction = lambda x: 0
        self.recentValue = True # default, 0, is pressed.

    def updateValue(self, newValue):
        previousValue = self.recentValue
        Sensor.updateValue(self, newValue)
        self.recentValue = False if self.recentValue > 500 else True
        if self.recentValue != previousValue:
            self.callbackFunction(self.recentValue)

    def waitForChange(self):
        previousValue = self.recentValue
        while self.recentValue == previousValue:
            yield
