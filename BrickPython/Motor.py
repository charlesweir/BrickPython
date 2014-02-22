
# Motor and associated classes, representing a motor attached to one of the BrickPi ports.

import datetime
from Scheduler import *
import logging

class PIDSetting():
    def __init__(self,distanceMultiplier=0.9,speedMultiplier=0.23,sumDistanceMultiplier=0.05):
        self.distanceMultiplier = distanceMultiplier
        self.speedMultiplier = speedMultiplier
        self.sumDistanceMultiplier = sumDistanceMultiplier

    def __repr__(self):
        return "PID Setting: distanceMultiplier=%3.4f, speedMultiplier=%3.4f, sumDistanceMultiplier=%3.4f" % (self.distanceMultiplier,
                                                                        self.speedMultiplier, self.sumDistanceMultiplier)

# Represents a location at a given time.  Time in milliseconds, position in clicks.
class TimePosition():
    def __init__(self,time=0.0,position=0):
        self.time = float(time)
        self.position = int(position)

    def __repr__(self):
        return "TimeDist: (%.3f, %d)" % (self.time, self.position)

    # Answers the speed in clicks per second coming to this point from other:
    def averageSpeedFrom(self, other):
        result = 0.0
        if self.time != other.time:
            result = 1000.0 * (self.position - other.position) / (self.time - other.time)
        return result

class Motor():
    def timeMillis(self):
        return Scheduler.currentTimeMillis()

    def __init__(self, port, scheduler = None):
        self.port = port
        self.idChar = chr(port + ord('A'))
        self._enabled = False
        self._position = 0
        self._power = 0
        self.pidSetting = PIDSetting()
        self.currentTP = self.previousTP = TimePosition(0, self.timeMillis())
        self.scheduler = scheduler
        self.basePosition = 0

    def setPIDSetting( self, pidSetting ):
        self.pidSetting = pidSetting
    def setPower(self, p):
        self._power = int(p)
    def power(self):
        return self._power
    def position(self):
        return self.currentTP.position
    def enabled(self):
        return self._enabled
    def enable(self, whether):
        self._enabled = whether

    def zeroPosition(self):
        self.basePosition += self.position()

    def speed(self):
        return self.currentTP.averageSpeedFrom( self.previousTP )

    def updatePosition(self, newPosition):
        self.previousTP = self.currentTP
        self.currentTP = TimePosition( self.timeMillis(), newPosition - self.basePosition )

    def moveTo( self, *args ):
        return self.positionUsingPIDAlgorithm( *args )

    def positionUsingPIDAlgorithm( self, target, timeoutMillis = 3000 ):
        return self.scheduler.withTimeout( timeoutMillis, self.positionUsingPIDAlgorithmWithoutTimeout( target ) )


    def stopAndDisable(self):
        self.setPower(0)
        self.enable(False)
        logging.info("Motor %s stopped" % (self.idChar))

    def positionUsingPIDAlgorithmWithoutTimeout( self, target ):
        sumDistance = 0 # Sum of all the distances (=I bit of PID ).
        self.enable(True)
        logging.info( "Motor %s moving to %d" % (self.idChar, target) )
        try:
            while True:
                delta = (target - self.currentTP.position)
                sumDistance += delta
                speed = self.speed()

                if abs(delta) <= 4 and abs(speed) < 10.0:
                    break

                power = (self.pidSetting.distanceMultiplier * delta
                         - self.pidSetting.speedMultiplier * speed
                         + self.pidSetting.sumDistanceMultiplier * sumDistance )
                self.setPower( power )

                yield

        finally:
            self.stopAndDisable()


    def setSpeed( self, targetSpeedInClicksPerSecond, timeoutMillis = 3000 ):
        return self.scheduler.withTimeout( timeoutMillis, self.runAtConstantSpeed( targetSpeedInClicksPerSecond ) )

    def runAtConstantSpeed( self, targetSpeedInClicksPerSecond ):
        speedErrorMargin = 10
        power = 20.0
        if targetSpeedInClicksPerSecond < 0:
            power = -power
        self.enable(True)
        logging.info( "Motor %s moving at constant speed %.3f" % (self.idChar, targetSpeedInClicksPerSecond) )
        try:
            while abs(targetSpeedInClicksPerSecond - 0.0) > speedErrorMargin: # Don't move if the target speed is zero.
                speed = self.speed()
                if abs(speed - targetSpeedInClicksPerSecond) < speedErrorMargin:
                    pass
                elif abs(speed) < abs(targetSpeedInClicksPerSecond):
                    power *= 1.1
                elif abs(speed) > abs(targetSpeedInClicksPerSecond):
                    power /= 1.1
                self.setPower( power )

                yield

        finally:
            self.stopAndDisable()

