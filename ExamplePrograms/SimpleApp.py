# Simple example application for BrickPython.


import sortOutPythonPaths
from BrickPython.CommandLineApplication import *

class SimpleApp(CommandLineApplication):
    'Simple command line example application'
    def __init__(self):
        CommandLineApplication.__init__(self)
        self.addSensorCoroutine( self.doActivity() )

    def doActivity(self):
        'Coroutine to rotate a motor forward and backward'
        motorA = self.motor('A')
        motorA.zeroPosition()
        while True:
            print 'a'
            for i in motorA.moveTo( 2*90 ):
                yield
            print 'b'
            for i in motorA.moveTo( 0 ):
                yield

if __name__ == "__main__":
    SimpleApp().mainloop()