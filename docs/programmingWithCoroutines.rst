===========================
Programming with Coroutines
===========================

A simple example
----------------


Here's a simple application, from ``ExamplePrograms/SimpleApp.py``::

	from BrickPython.TkApplication import *

	class SimpleApp(TkApplication):
	    def __init__(self):
	        TkApplication.__init__(self)
	        self.addSensorCoroutine( self.doActivity() ) #A

	    def doActivity(self):
	    	'Coroutine to rotate a motor forward and backward'
	        motorA = self.motor('A')
	        motorA.zeroPosition() #B
	        while True:
	            for i in motorA.moveTo( 2*90 ): #C
	                yield #D

	            for i in motorA.moveTo( 0 ):
	                yield

	if __name__ == "__main__":
	    SimpleApp().mainloop()

Line A creates a coroutine from the coroutine method doActivity() and adds it to the scheduler.   A coroutine must have
one or more `yield` calls, such as the one at line D, and the scheduler can then call it using 'next()'
- see, for example https://wiki.python.org/moin/Generators

To properly leverage coroutines, we want to be able to call other coroutines, and wait until they've finished.
Lines C,D show how this is done.   `motorA.moveTo(2*90)` is itself a coroutine - one that implements the Servo motor
PID algorithm - and we can call it using Python's 'iteration'::

	for i in coroutine(): yield

The dummy variable `i` is ignored.

We could, of course, add extra code between C and D - for example to check a sensor.  It will be executed for each work call.
``ExamplePrograms/DoorControl.py`` shows how this can work.

Composing Coroutines
--------------------

We can also combine coroutines.  The `Scheduler` methods `runTillFirstCompletes` and `runTillAllComplete` 


