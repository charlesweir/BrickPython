# Test for BrickPiWrapper

# Run tests as
#   python Test.py
# or, if you've got it installed:
#   nosetests

# Install mock and nosetests on pi or mac using:
#   sudo easy_install nose
#   sudo easy_install mock



from BrickPython.BrickPiWrapper import BrickPiWrapper, StopCoroutineException
import unittest
from mock import Mock


class TestMotor(unittest.TestCase):
    ''' Tests for the Motor class, especially for PID Servo Motor functionality'''
    def setUp(self):
        self.bp = BrickPiWrapper()
        motor = self.motor = self.bp.motor( 'A' )
        #motor.position = Mock()
        motor.timeMillis = Mock()
        motor.timeMillis.side_effect = range(0,9999)

    def testZeroPosition( self ):
        motor = self.motor
        # When the motor is zeroed at absolute position 1
        motor.updatePosition(1)
        motor.zeroPosition()
        # then absolute position 2 is read as position 1
        motor.updatePosition(2)
        self.assertEquals( motor.position(), 1 )
        # When the motor is zeroed again at absolute position 2
        motor.zeroPosition()
        # then absolute position 3 is read as position 1
        motor.updatePosition(3)
        self.assertEquals( motor.position(), 1 )

    def testSpeedCalculation(self):
        motor = self.motor
        # When the motor is moving at 1 click per call (every millisecond)
        motor.updatePosition(1)
        motor.updatePosition(2)
        # The speed is 1000 clicks per second.
        print motor.speed()
        assert( int(motor.speed()) == 1000)

    # Tests for positionUsingPIDAlgorithm:

    def testGeneratorFunctionWorks(self):
        motor = self.motor
        # When we try to reposition the motor
        positions = [0,5,11,10,10,10].__iter__()
        generator = motor.positionUsingPIDAlgorithmWithoutTimeout( 10 )
        # it keeps going
        for i in generator:
            motor.updatePosition( positions.next() )
            assert( motor.enabled() )
        # until it reaches the target position
        assert( motor.position() == 10 )
        # then switches off
        assert( not motor.enabled() )
        assert( motor.power() == 0 )

    def testFinishesIfNearEnough(self):
        motor = self.motor
        # When the motor gets near enough to the target
        positions = [0,99,99,99].__iter__()
        generator = motor.positionUsingPIDAlgorithmWithoutTimeout( 100 )
        for i in generator:
            motor.updatePosition( positions.next() )
        # it still completes :
        self.assertEquals( motor.position(), 99 )
        self.assertFalse( motor.enabled() )

    def testChecksSpeedOnFinishing(self):
        motor = self.motor
        # When the motor gets to the right position, but is still going fast:
        positions = [0,50,100,150].__iter__()
        co = motor.positionUsingPIDAlgorithm( 100 )
        for i in range(3):
            motor.updatePosition( positions.next() )
            co.next()
        # it doesn't stop (no StopIteration exception has been thrown)

    def testPowerIsFunctionOfDistance(self):
        motor = self.motor
        # When it's some distance from the target, but not moving
        co = motor.positionUsingPIDAlgorithmWithoutTimeout( 100 )
        motor.updatePosition( 0 )
        co.next()
        motor.updatePosition( 0 )
        co.next()
        # There's power to the motor in the right direction.
        assert( motor.power() > 0 )

    def testPowerIsFunctionOfSpeed(self):
        motor = self.motor
        # When the motor is going fast
        co = motor.positionUsingPIDAlgorithmWithoutTimeout( 100 )
        # when it reaches the target
        motor.updatePosition( 0 )
        co.next()
        motor.updatePosition( 100 )
        co.next()
        # It doesn't finish and the power is in reverse.
        assert( motor.power() < 0 )

    def testPowerIsFunctionOfSumDistance(self):
        motor = self.motor
        # When the motor isn't moving and is some distance from the target
        co = motor.positionUsingPIDAlgorithmWithoutTimeout( 100 )
        # The motor power increases with time
        motor.updatePosition( 0 )
        co.next()
        p1 = motor.power()
        motor.updatePosition( 0 )
        co.next()
        assert( motor.power() > p1 )

    def testTimesOutIfNeverReachesTarget(self):
        motor = self.motor
        co = motor.positionUsingPIDAlgorithm( 100 )
        # If the motor never reaches the target in 6 seconds:
        for i in range(0,6000/20):
            self.bp.doWork()
        # It terminates
        self.assertFalse( self.bp.stillRunning( co ) )

    def testAlternateNameAndUseOfScheduler(self):
        motor = self.motor
        # When we use the other name for the operation
        generator = motor.moveTo( 10 )
        # and invoke the scheduler while the motor moves to the position
        positions = [0,5,11,10,10,10]
        for i in range(len(positions)):
            motor.updatePosition( positions[i] )
            self.bp.doWork()
        # Then we complete correctly
        self.assertFalse( self.bp.stillRunning( generator ))
        self.assertEquals( motor.position(), 10 )

    def testCanCancelOperation(self):
        motor = self.motor
        # if we start the motor
        co = motor.positionUsingPIDAlgorithmWithoutTimeout( 100 )
        co.next()
        assert( motor.enabled() )
        # then stop the coroutine
        try:
            co.throw(StopCoroutineException)
            # the coroutine stops
            assert( False )
        except (StopCoroutineException, StopIteration): # The exception should stop the coroutine
            pass
        # and switch off the motor.
        assert( not motor.enabled() )
        assert( motor.power() == 0 )

if __name__ == '__main__':
    unittest.main()

