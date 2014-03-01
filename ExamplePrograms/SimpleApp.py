# Very simple example application for BrickPython.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

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
            print 'Moving forward'
            for i in motorA.moveTo( 2*90 ):
                yield
            print 'Moving back'
            for i in motorA.moveTo( 0 ):
                yield

if __name__ == "__main__":
    SimpleApp().mainloop()