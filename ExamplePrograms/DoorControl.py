# James and Charles Weir


#Kludge to add the directory above this to the PYTHONPATH:
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from BrickPython.TkApplication import *

class DoorControlApp(TkApplication):
    '''Application to automatically open and close a door using a proximity sensor.
    It also closes and 'locks' it when C is pressed (so the sensor no longer opens it), starting again when S or O is pressed

    The door is attached to a motor, which opens it by moving through 90 degrees, and closes it the same way.

    The sensor is mounted above the door, so it detects approaching 'peaple'.
    '''

    def __init__(self):
        TkApplication.__init__(self, {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT })
        self.doorLocked = False
        self.addSensorCoroutine( self.openDoorWhenSensorDetected() )

    def openDoorWhenSensorDetected(self):
        '''Coroutine that waits until the sensor detects something nearby, then opens the door, keeps it open for
        4 seconds, then closes it again and repeats.

        It uses the flag *doorLocked* to determine whether the user has 'locked' the door.
        '''
        motorA = self.motor('A')
        sensor1 = self.sensor('1')
        motorA.zeroPosition()
        while True:

            while sensor1.value() > 8 or self.doorLocked:
                yield

            print "Opening - sensor 1 value is ", sensor1.value()
            for i in motorA.moveTo( -2*90, 2000 ):
                if self.doorLocked: break
                yield


            print "Waiting 4 seconds"
            for i in self.doWait( 4000 ):
                if self.doorLocked: break
                yield

            print "Shutting door"
            for i in motorA.moveTo( 0, 2000 ):
                yield

            print "Door closed"

    def onKeyPress(self, event):
        'Handle key input from the user'
        if TkApplication.onKeyPress(self, event):
            return

        char = event.char
        if char in 'Cc':
            print "Closing and disabling door now"
            self.doorLocked = True

        elif char in 'SsOo':
            print "Re-activating door"
            self.doorLocked = False



if __name__ == "__main__":
    print "Starting"
    app = DoorControlApp()
    app.mainloop()
