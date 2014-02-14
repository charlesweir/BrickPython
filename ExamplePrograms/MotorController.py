# James and Charles Weir
# Controlling a servo motor

from Application import *


class MyApp(Application):
    
    def __init__(self):
        Application.__init__(self, {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT })
    
    def rotate(self, degrees):
        self.stopAllCoroutines()
        motor = self.motor('A')
        print "Rotating motor A %d degrees" % degrees
        co = motor.moveTo( motor.position() + degrees*2 )
        self.addActionCoroutine( co )

    def setSpeed(self, speed):
        self.stopAllCoroutines()
        motor = self.motor('A')
        print "Speed for motor A %.2f" % speed
        co = motor.runAtConstantSpeed( speed )
        self.addActionCoroutine( co )

    def onKeyPress(self, event):
        if Application.onKeyPress(self, event):
            return
        
        char = event.char
        if char in "0123456789":
            # rotate forwards:
            self.rotate(90 * (ord(char) - ord("0")))
        elif char in "abcdefghijklmnop":
            # rotate reverse:
            self.rotate(-90 * (ord(char) - ord("a") + 1))
        elif char in "ABCDEFG":
            self.setSpeed(180 * (ord(char) - ord("A") ))
        
        # Adjust PID settings:
        elif char in "xyzXYZ":
            if char == 'x':
                self.pidSetting.distanceMultiplier *= 1.1
            elif char == 'X':
                self.pidSetting.distanceMultiplier /= 1.1
            elif char == 'y':
                self.pidSetting.speedMultiplier *= 1.1
            elif char == 'Y':
                self.pidSetting.speedMultiplier /= 1.1
            elif char == 'z':
                self.pidSetting.sumDistanceMultiplier *= 1.1
            elif char == 'Z':
                self.pidSetting.sumDistanceMultiplier /= 1.1
            print "%r" % (self.pidSetting)
            self.motor('A').setPIDSetting( self.pidSetting )

if __name__ == "__main__":
    print "Starting"
    app = MyApp()
    app.mainloop()
