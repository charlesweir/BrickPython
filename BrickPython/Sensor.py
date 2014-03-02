# Sensor - represents a single value sensor supported by the BrickPython library
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import BrickPi

class Sensor():
    '''Sensor, representing a sensor attached to one of the BrickPi ports.
    *port* may be either a PORT_ value or an integer '1'-'5'

    There are class attributes with the types defined in the BrickPi module:
        Sensor.TYPE_SENSOR_ULTRASONIC_CONT
    These are configured in the initialization parameters to BrickPiWrapper (and derived classes)

    '''

    @staticmethod
    def portNumFromId(portNumOrIdChar):
        # Answers the port number given either value.
        if (not isinstance(portNumOrIdChar, int)):
            return int(portNumOrIdChar) - 1
        return portNumOrIdChar

    def __init__(self, port):
        self.port = Sensor.portNumFromId(port)
        #: Character identifying the sensor: 1 through 5.
        self.idChar = chr(self.port + ord('1'))
        #: Array of the *maxRecentValues* most recent sensor readings
        self.recentValues = [0]
        #: How many sensor readings to store
        self.maxRecentValues = 5

    def updateValue(self, newValue):
        # Called by the framework to set the new value for the sensor.
        # We ignore zero values - probably means a comms failure.
        if newValue == 0:
            return
        self.recentValues.append( newValue )
        if len(self.recentValues) > self.maxRecentValues:
            del self.recentValues[0]

    def value(self):
        'Answers the latest sensor value received'
        return self.recentValues[-1]

    def __repr__(self):
        return "Sensor %s: %r" % (self.idChar, self.recentValues)

# Put the sensor types (which are globals in BrickPi) to be attributes of Sensor

for name in dir(BrickPi):
    if name.startswith('TYPE_'):
        setattr(Sensor, name, getattr(BrickPi, name))
