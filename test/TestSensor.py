# Tests for Sensor
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import unittest
from BrickPython.BrickPi import PORT_1
from BrickPython.Sensor import Sensor, TouchSensor, UltrasonicSensor, LightSensor
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

    def testUltrasonicSensor(self):
        sensor = UltrasonicSensor( '1' )
        self.assertEquals(sensor.port, 0)
        self.assertEquals( sensor.idChar, '1' )
        for input, output in {0:0, 2:0, 3:5, 4:5, 9:10, 11:10, 14:15, 16:15, 22:20, 23:25, 26:25,
                              255: UltrasonicSensor.MAX_VALUE
                              }.items():
            sensor.updateValue( input )
            self.assertEquals( sensor.value(), output )

    def testLightSensor(self):
        #Light is 680, dark about 800
        sensor = LightSensor('4')
        self.assertEquals(sensor.port, 3)
        self.assertEquals( sensor.idChar, '4' )
        for input, output in { 680: LightSensor.LIGHT, 800: LightSensor.DARK
                              }.items():
            sensor.updateValue( input )
            self.assertEquals( sensor.value(), output )
        self.assertEquals( repr(sensor), "LightSensor 4: 'Dark' (800)")

if __name__ == '__main__':
    unittest.main()

