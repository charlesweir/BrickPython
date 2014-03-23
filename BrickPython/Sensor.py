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
        assert( result in range(0,4)) # Yes, there are 5 sensor ports, but brickpi_python doesn't support #5
        return result

    def __init__(self, port, sensorType=RAW):
        self.port = Sensor.portNumFromId(port)
        self.type = sensorType
        #: Character identifying the sensor: 1 through 5.
        self.idChar = chr(self.port + ord('1'))
        #: The most recent value to return
        self.recentValue = self.cookValue(0)
        #: The most recent raw value received from the BrickPi
        self.rawValue = 0
        #: Function that gets called with new value as parameter when the value changes - default, none.
        self.callbackFunction = lambda x: 0

    def updateValue(self, newValue):
        # Called by the framework to set the new value for the sensor.
        # We ignore zero values - probably means a comms failure.
        if newValue == 0:
            return
        self.rawValue = newValue
        previousValue = self.recentValue
        self.recentValue = self.cookValue(newValue)
        if self.recentValue != previousValue:
            self.callbackFunction(self.recentValue)

    def waitForChange(self):
        'Coroutine that completes when the sensor value changes'
        previousValue = self.recentValue
        while self.recentValue == previousValue:
            yield

    def value(self):
        'Answers the latest sensor value received'
        return self.recentValue

    def cookValue(self, rawValue):
        'Answers the value to return for a given input sensor reading'
        return rawValue

    def __repr__(self):
        return "%s %s: %r (%d)" % (self.__class__.__name__, self.idChar, self.displayValue(), self.rawValue)

    def displayValue(self):
        'Answers a good representation of the current value for display'
        return self.value()

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

class UltrasonicSensor(Sensor):
    '''Represents an NXT ultrasonic sensor attached to one of the BrickPi ports.
    Parameter *port* may be either a value (BrickPi.PORT_1) or an integer '1'-'5'

    value() is distance to the nearest 5 cm, with a maximum of MAX_VALUE
    '''
    #: The reading when no object is in sight:
    MAX_VALUE = 30
    #: Round readings to nearest centimeters.
    ROUND_TO = 5
    #: How many readings to smooth over.
    SMOOTHING_RANGE=10

    def __init__(self, port):
        self.recentRawValues = [0]
        Sensor.__init__(self, port, Sensor.ULTRASONIC_CONT)

    def cookValue(self, rawValue):
        self.recentRawValues.append( rawValue )
        if len(self.recentRawValues) > UltrasonicSensor.SMOOTHING_RANGE:
            del self.recentRawValues[0]
        smoothedValue = min(self.recentRawValues)
        result = int(self.ROUND_TO * round(float(smoothedValue)/self.ROUND_TO))  # Round to nearest 5
        return min(result, UltrasonicSensor.MAX_VALUE)

#     def displayValue(self):
#         return self.recentRawValues

class LightSensor(Sensor):
    '''Represents my NXT color sensor.
    The BrickPi_Python COLOR_FULL setting didn't work for me at all - always has value 1.
    (though it did light up a red LED on the device).

    But in RAW mode the sensor does seem to detect the difference between light and dark backgrounds.

    value() is either LIGHT or DARK
    '''
    #: Detected a light background:
    LIGHT = 1
    #: Detected a dark background:
    DARK = 0

    def __init__(self, port):
        Sensor.__init__(self, port, Sensor.RAW)

    def cookValue(self, rawValue):
        return LightSensor.LIGHT if rawValue < 740 else LightSensor.DARK

    def displayValue(self):
        return ("Dark","Light")[self.value()]

