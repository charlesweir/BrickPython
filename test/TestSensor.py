# Tests for Sensor
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import unittest
from BrickPython.BrickPiWrapper import PORT_1
from BrickPython.Sensor import Sensor

class TestSensor(unittest.TestCase):
    'Test for the Sensor object'

    def testSensor(self):
        sensor = Sensor( PORT_1 )
        assert( sensor.idChar == '1' )
        assert( sensor.value() == 0 )
        sensor.updateValue( 3 )
        assert( sensor.value() == 3 )
        assert( sensor.recentValues == [0,3] )
        for i in range(1,6):
            sensor.updateValue( i )
        assert( sensor.recentValues == range(1,6) )

    def testSensorTextRepresentation(self):
        self.assertEquals( repr(Sensor( PORT_1 ) ), 'Sensor 1: [0]')

if __name__ == '__main__':
    unittest.main()

