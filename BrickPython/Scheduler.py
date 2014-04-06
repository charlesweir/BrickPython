# Scheduler
# Support for coroutines using Python generator functions.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import datetime
import logging
import sys, traceback
import threading

class StopCoroutineException( Exception ):
    '''Exception used to stop a coroutine'''
    pass

ProgramStartTime = datetime.datetime.now()

class Coroutine():
    def __init__(self):
        #: Semaphore is one when blocked, 0 when running
        self.semaphore = threading.Semaphore(0)

    def action(self):
        pass


class GeneratorCoroutineWrapper(Coroutine):

    def __init__(self, scheduler, generator):
        Coroutine.__init__(self)
        self.scheduler = scheduler
        self.stopEvent = threading.Event()
        self.generator = generator
        self.thread = threading.Thread(target=self.action)
        self.thread.start()

    def action(self):
        'The thread entry function - executed within thread `thread`'
        try:
            self.semaphore.acquire()
            while not self.stopEvent.is_set():
                self.generator.next()
                self.scheduler.semaphore.release()
                self.semaphore.acquire()
            self.generator.throw(StopCoroutineException)
        except (StopCoroutineException, StopIteration):
            pass
        except Exception as e:
            self.scheduler.lastExceptionCaught = e
            logging.info( "Scheduler - caught: %r" % (e) )
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = "".join(traceback.format_tb(exc_traceback))
            logging.debug( "Traceback (latest call first):\n %s" % trace )

        self.scheduler.coroutines.remove( self )
        self.scheduler.semaphore.release()

    def next(self):
        'Runs a bit of processing (next on the generator) - executed from the scheduler thread - returns only when processing has completed'
        self.semaphore.release()
        self.scheduler.semaphore.acquire()

    def stop(self):
        'Causes the thread to stop'
        self.stopEvent.set()


class Scheduler():
    ''' This manages an arbitrary number of coroutines (implemented as generator functions), supporting
    invoking each every *timeMillisBetweenWorkCalls*, and detecting when each has completed.

    It supports one special coroutine - the updatorCoroutine, which is invoked before and after all the other ones.
    '''

    timeMillisBetweenWorkCalls = 50

    @staticmethod
    def currentTimeMillis():
        'Answers the time in floating point milliseconds since program start.'
        global ProgramStartTime
        c = datetime.datetime.now() - ProgramStartTime
        return c.days * (3600.0 * 1000 * 24) + c.seconds * 1000.0 + c.microseconds / 1000.0

    def __init__(self, timeMillisBetweenWorkCalls = 50):
        Scheduler.timeMillisBetweenWorkCalls = timeMillisBetweenWorkCalls
        self.coroutines = []
        self.timeOfLastCall = Scheduler.currentTimeMillis()
        self.updateCoroutine = GeneratorCoroutineWrapper( self, self.nullCoroutine() ) # for testing - usually replaced.
        #: The most recent exception raised by a coroutine:
        self.lastExceptionCaught = Exception("None")
        #: Semaphore is one when blocked (running a coroutine), 0 when active
        self.semaphore = threading.Semaphore(0)


    def doWork(self):
        'Executes all the coroutines, handling exceptions'

        timeNow = Scheduler.currentTimeMillis()
        if timeNow == self.timeOfLastCall: # Ensure each call gets a different timer value.
            return
        self.timeOfLastCall = timeNow
        self.updateCoroutine.next()
        for coroutine in self.coroutines[:]:   # Copy of coroutines, so it doesn't matter removing one
            coroutine.next()

        self.updateCoroutine.next()

    def timeMillisToNextCall(self):
        'Wait time before the next doWork call should be called.'
        timeRequired = self.timeMillisBetweenWorkCalls + self.timeOfLastCall - Scheduler.currentTimeMillis()
        return max( timeRequired, 0 )


    def addSensorCoroutine(self, *coroutineList):
        '''Adds one or more new sensor/program coroutines to be scheduled, answering the last one to be added.
        Sensor coroutines are scheduled *before* Action coroutines'''
        for generatorFunction in coroutineList:
            latestAdded = GeneratorCoroutineWrapper(self, generatorFunction)
            self.coroutines[0:0] = [ latestAdded ]
        return generatorFunction

    def addActionCoroutine(self, *coroutineList):
        '''Adds one or more new motor control coroutines to be scheduled, answering the last coroutine to be added.
        Action coroutines are scheduled *after* Sensor coroutines'''
        for generatorFunction in coroutineList:
            latestAdded = GeneratorCoroutineWrapper(self, generatorFunction)
            self.coroutines.extend( [ latestAdded ] )
        return generatorFunction

    def setUpdateCoroutine(self, coroutine):
        # Private - set the coroutine that manages the interaction with the BrickPi.
        # The coroutine will be invoked once at the start and once at the end of each doWork call.
        self.updateCoroutine = GeneratorCoroutineWrapper(self, coroutine)

    def findCoroutineForGenerator(self, generator):
        return [c for c in self.coroutines if c.generator == generator][0]

    def stopCoroutine( self, *coroutineList ):
        'Terminates the given one or more coroutines'
        for generator in coroutineList:
            coroutine = self.findCoroutineForGenerator(generator)
            coroutine.stop()

    def stopAllCoroutines(self):
        'Terminates all coroutines (except the updater one) - rather drastic!'
        self.stopCoroutine(*[c.generator for c in self.coroutines]) # Makes a copy of the list - don't want to be changing it.

    def numCoroutines( self ):
        'Answers the number of active coroutines'
        return len(self.coroutines)

    def stillRunning( self, *coroutineList ):
        'Answers whether any of the given coroutines are still executing'
        return any( c in self.coroutines for c in coroutineList )

    #############################################################################################
    #                 Coroutines
    #############################################################################################

    @staticmethod
    def nullCoroutine():
        'Null coroutine - runs forever and does nothing'
        while True:
            yield

    @staticmethod
    def runTillFirstCompletes( *coroutineList ):
        'Coroutine that executes the given coroutines until the first completes, then stops the others and finishes.'
        while True:
            for coroutine in coroutineList:
                try:
                    coroutine.next()
                except (StopIteration, StopCoroutineException):
                    return # CW - I don't understand it, but we don't seem to need to terminate the others explicitly.
            yield

    @staticmethod
    def runTillAllComplete(*coroutineList ):
        'Coroutine that executes the given coroutines until all have completed or one throws an exception.'
        coroutines = list( coroutineList )
        while coroutines != []:
            for coroutine in coroutines:
                try:
                    coroutine.next()
                except (StopIteration, StopCoroutineException):
                    coroutines.remove( coroutine )
            yield

    @staticmethod
    def waitMilliseconds( timeMillis ):
        'Coroutine that waits for timeMillis, then finishes.'
        t = Scheduler.currentTimeMillis()
        while Scheduler.currentTimeMillis() - t < timeMillis:
            yield

    @staticmethod
    def withTimeout( timeoutMillis, *coroutineList ):
        'Coroutine that wraps the given coroutine(s) with a timeout'
        return Scheduler.runTillFirstCompletes( Scheduler.waitMilliseconds( timeoutMillis ), *coroutineList )

    @staticmethod
    def waitFor(function, *args ):
        'Coroutine that waits until the given function (with optional parameters) returns True.'
        while not function(*args):
            yield

