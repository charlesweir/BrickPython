# Sensor class

#TODO: Remove need for clients to import * from BrickPython by
# getting rid of the use of PORT_* values in the interfaces,
# and duplicating TYPE_SENSOR_ULTRASONIC_CONT etc as static members of class Sensor.

class Sensor():
    '''Sensor, representing a sensor attached to one of the BrickPi ports.'''
    def __init__(self, port):
        self.port = port
        #: Character identifying the sensor: 1 through 5.
        self.idChar = chr(port + ord('1'))
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


