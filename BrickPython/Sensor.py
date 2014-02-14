
# Sensor, representing a sensor attached to one of the BrickPi ports.

class Sensor():
    def __init__(self, port):
        self.port = port
        self.idChar = chr(port + ord('1'))
        self.recentValues = [0]
        self.maxRecentValues = 5

    def updateValue(self, newValue):
        # Ignore zero values - probably means a comms failure.
        if newValue == 0:
            return
        self.recentValues.append( newValue )
        if len(self.recentValues) > self.maxRecentValues:
            del self.recentValues[0]

    def value(self):
        return self.recentValues[-1]

    def __repr__(self):
        return "Sensor %s: %r" % (self.idChar, self.recentValues)


