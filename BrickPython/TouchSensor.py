# TouchSensor - represents an NXT touch sensor supported by the BrickPython library
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

from Sensor import Sensor

class TouchSensor(Sensor):
    '''TouchSensor, representing an NXT touch sensor attached to one of the BrickPi ports.
    Parameter *port* may be either a value (BrickPi.PORT_1) or an integer '1'-'5'

    value() is True if the button is pressed; False otherwise.
    '''
    def __init__(self, port):
        # Just using the BrickPi TYPE_SENSOR_TOUCH didn't work for me; hence raw.
        Sensor.__init__(self, port, Sensor.RAW)

    def cookValue(self, rawValue):
        return True if rawValue < 500 else False

