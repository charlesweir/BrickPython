# Test for BrickPiWrapper

# Run tests as
#   python Test.py
# or, if you've got it installed:
#   nosetests

# Install mock and nosetests on pi or mac using:
#   sudo easy_install nose
#   sudo easy_install mock



from BrickPiWrapper import *
import unittest
from Sensor import *

class SensorTests(unittest.TestCase):
    global Sensor

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



if __name__ == '__main__':
    unittest.main()

