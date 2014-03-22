# Tests for Sensor
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import unittest
from BrickPython.BrickPi import PORT_1
from BrickPython.Sensor import Sensor, TouchSensor
import TestScheduler

class TestSensor(unittest.TestCase):
    'Tests for the Sensor classes'

    def testSensor(self):
        sensor = Sensor( PORT_1 )
        self.assertEquals(sensor.port, PORT_1)
        assert( sensor.idChar == '1' )
        assert( sensor.value() == 0 )
        sensor.updateValue( 3 )
        assert( sensor.value() == 3 )

    def testSensorTextRepresentation(self):
        self.assertEquals( repr(Sensor( PORT_1 ) ), 'Sensor 1: 0 (0)')

    def testDifferentWaysToInitialize(self):
        self.assertEquals( repr(Sensor( '1' ) ), 'Sensor 1: 0 (0)')
        self.assertEquals( repr(Sensor( '1', Sensor.COLOR_NONE ) ), 'Sensor 1: 0 (0)')

    def testTouchSensor(self):
        sensor = TouchSensor( '1' )
        self.assertEquals(sensor.port, 0)
        self.assertEquals( sensor.idChar, '1' )
        self.assertEquals( sensor.value(), True ) # Pressed in
        sensor.updateValue( 1000 )
        self.assertEquals( sensor.value(), False )

    def testTouchSensorTextRepresentation(self):
        self.assertEquals( repr(TouchSensor( '1' ) ), 'TouchSensor 1: True (0)')

    def testCallbackWhenChanged(self):
        result = [True]
        def callbackFunc(x):
            result[0] = x
        sensor = TouchSensor( '1' )
        sensor.callbackFunction = callbackFunc
        sensor.updateValue( 1000 )
        self.assertEquals( result[0], False )
        # And no call when it doesn't change
        result[0] = True
        sensor.updateValue( 1000 )
        self.assertEquals( result[0], True )
        # But does get a call when it changes back
        result[0] = False
        sensor.updateValue( 20 )
        self.assertEquals( result[0], True )

    def testCoroutineWaitingForChange(self):
        sensor = TouchSensor( '1' )
        coroutine = sensor.waitForChange()
        coroutine.next()
        coroutine.next()
        sensor.updateValue( 1000 )
        TestScheduler.TestScheduler.checkCoroutineFinished( coroutine )

if __name__ == '__main__':
    unittest.main()

