===========================
Programming with Coroutines
===========================

A simple example
----------------


Here's a simple application, from ``ExamplePrograms/SimpleApp.py``::

	from BrickPython.CommandLineApplication import *

	class SimpleApp(CommandLineApplication):
	    def __init__(self):
	        CommandLineApplication.__init__(self)
	        self.addSensorCoroutine( self.doActivity() )  #A

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

It uses the simplest scheduler: the `CommandLineApplication`.

Line A creates a coroutine from the coroutine method doActivity() and adds it to the scheduler.   A coroutine method must have
one or more `yield` calls, such as the one at line D, so that calling the method returns a coroutine
which the scheduler can invoke using 'next()'.
For more about such 'generator functions', see https://wiki.python.org/moin/Generators

To get the most benefit from coroutines we want to be able to call other coroutines, and to wait until they've finished.
Lines C,D show how this is done.   `motorA.moveTo(2*90)` is itself a coroutine - one that implements the Servo motor
PID algorithm - and thus we can invoke it using Python's iteration syntax::

	for i in coroutine():
	    yield

The dummy variable `i` is ignored.

We could, of course, add extra code between C and D - for example to check a sensor.  It will be executed for each work call.
``ExamplePrograms/DoorControl.py`` shows how this can work.

Composing Coroutines
--------------------

We can also combine coroutines.

The coroutine method `Scheduler.runTillFirstCompletes` creates a new coroutine from
a list of coroutines and terminates them all (and itself) when the first completes.
The coroutine method `Scheduler.runTillAllComplete`
similarly runs until all of a list of coroutines complete.

The `Scheduler.withTimeout` coroutine method adds a timeout to a coroutine, terminating it if it hasn't completed after
the given timeout.

Ready-made coroutines
---------------------

`Scheduler.waitFor` answers a coroutine that terminates when a given function returns true.

`Motor.moveTo` and `Motor.setSpeed` are coroutines that control a motor.

