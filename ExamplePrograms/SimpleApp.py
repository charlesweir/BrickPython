# Simple example application for BrickPython.


import sortOutPythonPaths
from BrickPython.TkApplication import *

class SimpleApp(TkApplication):
    def __init__(self):
        TkApplication.__init__(self)
        self.addSensorCoroutine( self.doActivity() )

    def doActivity(self):
        'Coroutine to rotate a motor forward and backward'
        motorA = self.motor('A')
        motorA.zeroPosition()
        while True:
            for i in motorA.moveTo( 2*90 ):
                yield

            for i in motorA.moveTo( 0 ):
                yield

if __name__ == "__main__":
    SimpleApp().mainloop()