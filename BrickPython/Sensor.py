# Sensor - represents a single value sensor supported by the BrickPython library
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import BrickPi

class Sensor():
    '''Sensor, representing a sensor attached to one of the BrickPi ports.
    Parameter *port* may be either a value (BrickPi.PORT_1) or an integer '1'-'5'

    There are class attributes with the types defined in the BrickPi module, e.g. Sensor.ULTRASONIC_CONT
    You can configure the sensor type for each port in the initialization parameters to BrickPiWrapper (and derived classes)

    Used both as class in its own right, and as superclass for other sensor types.
    '''
    RAW               = BrickPi.TYPE_SENSOR_RAW
    LIGHT_OFF         = BrickPi.TYPE_SENSOR_LIGHT_OFF
    LIGHT_ON          = BrickPi.TYPE_SENSOR_LIGHT_ON
    TOUCH             = BrickPi.TYPE_SENSOR_TOUCH
    ULTRASONIC_CONT   = BrickPi.TYPE_SENSOR_ULTRASONIC_CONT
    ULTRASONIC_SS     = BrickPi.TYPE_SENSOR_ULTRASONIC_SS
    RCX_LIGHT         = BrickPi.TYPE_SENSOR_RCX_LIGHT
    COLOR_FULL        = BrickPi.TYPE_SENSOR_COLOR_FULL
    COLOR_RED         = BrickPi.TYPE_SENSOR_COLOR_RED
    COLOR_GREEN       = BrickPi.TYPE_SENSOR_COLOR_GREEN
    COLOR_BLUE        = BrickPi.TYPE_SENSOR_COLOR_BLUE
    COLOR_NONE        = BrickPi.TYPE_SENSOR_COLOR_NONE
    I2C               = BrickPi.TYPE_SENSOR_I2C
    I2C_9V            = BrickPi.TYPE_SENSOR_I2C_9V

    @staticmethod
    def portNumFromId(portNumOrIdChar):
        # Answers the port number given either port number or the ID Char.
        if isinstance(portNumOrIdChar, int):
            result = portNumOrIdChar
        else:
            result = int(portNumOrIdChar) - 1
        assert( result in range(0,3))
        return result

    def __init__(self, port, type=RAW):
        self.port = Sensor.portNumFromId(port)
        self.type = type
        #: Character identifying the sensor: 1 through 5.
        self.idChar = chr(self.port + ord('1'))
        #: The most recent sensor reading
        self.recentValue = 0

    def updateValue(self, newValue):
        # Called by the framework to set the new value for the sensor.
        # We ignore zero values - probably means a comms failure.
        if newValue == 0:
            return
        self.recentValue = newValue

    def value(self):
        'Answers the latest sensor value received'
        return self.recentValue

    def __repr__(self):
        return "%s %s: %r" % (self.__class__.__name__, self.idChar, self.recentValue)

