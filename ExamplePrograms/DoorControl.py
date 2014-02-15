# James and Charles Weir
#
# Application to automatically open and close a door using a proximity sensor.
# It also closes and 'locks' it when C is pressed (so the sensor no longer opens it), starting again when S or O is pressed
# The door is attached to a motor, which opens it by moving through 90 degrees, and closes it the same way.
# The sensor is mounted above the door, so it detects approaching 'peaple'.

from BrickPython.TkApplication import *


class DoorControlApp(TkApplication):

    def __init__(self):
        TkApplication.__init__(self, {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT })
        self.sensorActive = True
        self.addSensorCoroutine( self.openDoorWhenSensorDetected() )

    def openDoorWhenSensorDetected(self):
        motorA = self.motor('A')
        sensor1 = self.sensor('1')
        motorA.zeroPosition()
        while True:

            while sensor1.value() > 8 or not self.sensorActive:
                yield

            print "Opening - sensor 1 value is ", sensor1.value()
            for i in motorA.moveTo( -2*90, 2000 ):
                if not self.sensorActive: break
                yield


            print "Waiting 4 seconds"
            for i in self.doWait( 4000 ):
                if not self.sensorActive: break
                yield

            print "Shutting door"
            for i in motorA.moveTo( 0, 2000 ):
                yield

            print "Door closed"

    def onKeyPress(self, event):
        if TkApplication.onKeyPress(self, event):
            return

        char = event.char
        if char in 'Cc':
            print "Closing and disabling door now"
            self.sensorActive = False

        elif char in 'SsOo':
            print "Re-activating door"
            self.sensorActive = True



if __name__ == "__main__":
    print "Starting"
    app = DoorControlApp()
    app.mainloop()
