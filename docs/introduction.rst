.. Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

===========================
Introduction to BrickPython
===========================

I love the BrickPi.  It's a really powerful system, with the potential to do a lot.

This BrickPython package extends the BrickPi_python package to make it easier to program.  It introduces two things:
objects, and coroutines.

As a taster, here's a coroutine function to detect presence via a sensor, open a door, wait and close it again; all while still permitting other things to happen::

    def openDoorWhenSensorDetected(self):
        motorA = self.motor('A')
        sensor1 = self.sensor('1')
        motorA.zeroPosition()
        while True:
            while sensor1.value() > 8:
                yield

            for i in motorA.moveTo( -2*90 ):
                yield

            for i in self.doWait( 4000 ):
                yield

            for i in motorA.moveTo( 0 ):
                yield

The actual implementation - which also supports user input to change the behavior at any time - is :class:`.DoorControlApp` in ``ExamplePrograms/DoorControl.py``

Why Objects
===========

Objects make programming easier.  Objects can be intelligent (for example, the Motor object can know its speed); they
can be easier to debug (Motor can print itself in a useful way); and they separate out concerns (you can deal with one
Motor at a time).

Why Coroutines?
===============

Creating programs to control things is difficult.  Several things can be happening at once, and the program
needs to be able to deal with all of them.

So, for example, if you had a little bot with two wheels each controlled by a motor, and with two sensors to
detect the direction, you'd want to continuously adjust the speed of each motor, look at both the sensors, and maybe
also react to keyboard input from the user.

But this makes programming rather hard.  One might want to have a nice simple function::

	runMotorAtConstantSpeedForTime( aSpeed, aTime )

But with normal Python programming model the program can only be executing one thing at a time.  So if it's executing
that function, all the other input (other motor, sensors, user) is being ignored.

**Ouch!**

There are two conventional approaches to this problem, both with disadvantages:

*   **Event based programming**: Whenever anything happens (a new motor position, a sensor change, a user keystroke etc),
    the framework makes a call into your program.   This is a very common idiom, but it's surprisingly hard to program:
    every function has to decide what to do based on the values of variables.  This leads to a style of programming called 'state
    machine programming'.  It's workable (c.f. Syntropy, a methodology based on state machines).
    But it's not easy.


* 	**Multithreading**: Different activities in the program each gets their own 'thread'.  So in the example above, we might
	have a thread for each motor, each running a `runMotorAtConstantSpeed` function.  That gives a nicer structure to the
	program.  But there are appalling downsides: communication between threads is tricky, and sharing variables or data
	between threads can be fraught with subtle and difficult-to-track down problems.

This framework uses a third option: **Coroutines**.   With a coroutine, you can write 'long running' functions, which
nevertheless allow other things to go on before they return.  This relies on the Python 'yield' statement, which
allows a function to go 'on hold' while other processing happens.

Strictly speaking, what this package supports aren't true coroutines: a 'true' coroutine has its own stack.
Python doesn't support that, but we have ways around the problem.

Python 3.4 will have better support for coroutines - see http://docs.python.org/3.4/library/asyncio.html .

I'm grateful for David Beazley his tutorial on Python coroutines: http://dabeaz.com/coroutines/ .

The Scheduler
=============

To make our coroutines work, we need something that coordinates them and manages the interaction with the BrickPi.  These are the classes `Scheduler` and its derived class `BrickPiWrapper`.

:class:`.Scheduler` handles coroutines, calling them regularly every 'work call' (50 times per second), and provides methods to manage them:
starting and stopping them, combining them, and supporting features such as timeouts for a coroutine.

When the :class:`.Scheduler` stops a coroutine, the coroutine receives a :class:`.StopCoroutineException`; catching this allows the coroutine to tidy up properly.

The class :class:`.BrickPiWrapper` extends the :class:`.Scheduler` to manage the BrickPi interaction, managing the :class:`.Motor` and :class:`.Sensor` objects, calling the BrickPi twice
for every work call (once before, and once after all the coroutines have run), taking data from and subsequently updating
each :class:`.Motor` and :class:`.Sensor`.

So with the scheduler, here's all that's required to make a :class:`.Motor` move to a new position::

        co = theBrickPiWrapper.motor('A').moveTo( newPositionIndegrees*2 )
        theBrickPiWrapper.addActionCoroutine( co )

That will move for up to 3 seconds to the new position - and while it's doing it, everything else
is still 'live' and being processed: user input, other
coroutines, sensor input, you name it.

Integration with the Tk Graphical User Interface
================================================

To make user input easy, this module provides and integration with the Tk graphical interface, using the Python Tkinter framework.
The class that does this is :class:`.TkApplication`.   By default it
shows a small grey window which accepts keystrokes, and exits when the 'q' key is pressed, but this can be overridden.

Our example applications have a main class that derives from :class:`.TkApplication`, which itself derives from :class:`.BrickPiWrapper`.


Other Integrations
==================

Integrations with other frameworks, or none at all, are equally straightforward.   The framework must call the
method :meth:`.Scheduler.doWork()` regularly, pausing for :meth:`.Scheduler.timeMillisToNextCall()` after each call.

For example :class:`.CommandLineApplication` provides a scheduler for applications that don't require user input.

Motors and Sensors
==================

The :class:`.Motor` class implements methods to record and calculate the current speed.  It also implements the servo motor PID algorithm as the coroutine :meth:`.Motor.moveTo()`, allowing the motor
to position itself accurately to a couple of degrees.  There's also a 'constant speed' coroutine :meth:`.Motor.setSpeed()`.

The :class:`.Sensor` class keeps a record, :attr:`.Sensor.recentValues`, of the last few readings; its method :meth:`.Sensor.value()` answers the most recent one.  The type of each sensor
is set up via initialization parameters to :class:`.BrickPiWrapper` (via :class:`.TkApplication` or :class:`.CommandLineApplication`).

Example Applications
====================

* :class:`.MotorControllerApp` is for experimenting with a motor connected to port A.  It supports varying the PID settings, and moving different distances or at constant speed.

* :class:`.DoorControlApp` is an example of more real-life functionality.  It uses a sensor to detect an approaching person, opens a door for 4 seconds, then closes it again.
  On user input, it can 'lock' the door - closing it immediately and disabling it from opening again.

Other Environments
==================

To help with development, this package also runs on other environments.  It's been tested on Mac OS X, but should run on
any Python environment.  In non-RaspberryPi environments, it replaces the hardware connections with a 'mock'
serial connection, which ignores motor settings and always returns default values (0)
for sensors and motor positions.

In particular, all the unit tests will run on any environment.

Test Code
=========

Finally, there are unit tests for all of the code here.  If you have ``nosetests`` installed, run::

	nosetests

from the top level directory, or invoke them through the package manager using::

    python setup.py test

