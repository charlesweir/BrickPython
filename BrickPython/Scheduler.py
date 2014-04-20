# Scheduler
# Support for coroutines using either Python generator functions or thread-based coroutines.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import threading
from Coroutine import Coroutine, StopCoroutineException

class GeneratorCoroutineWrapper(Coroutine):
    '''Internal: Wraps a generator-style coroutine with a thread'''

    def __init__(self, generator):
        '''`scheduler` - the main Scheduler object
        `generator` - the generator object created by calling the generator function'''
        Coroutine.__init__(self, self.action)
        self.generator = generator

    def action(self):
        'The thread entry function - executed within thread `thread`'
        for _ in self.generator:
            Coroutine.wait()

    def stop(self):
        try:
            self.generator.throw(StopCoroutineException())
        except StopCoroutineException:
            pass
        Coroutine.stop(self)


class Scheduler():
    ''' This manages an arbitrary number of coroutines (including generator functions), supporting
    invoking each every *timeMillisBetweenWorkCalls*, and detecting when each has completed.

    It supports one special coroutine - the updatorCoroutine, which is invoked before and after all the other ones.
    '''

    timeMillisBetweenWorkCalls = 50

    @staticmethod
    def makeCoroutine(coroutineOrGenerator):
        return coroutineOrGenerator if coroutineOrGenerator is Coroutine else GeneratorCoroutineWrapper(coroutineOrGenerator)


    @staticmethod
    def currentTimeMillis():
        return Coroutine.currentTimeMillis()

    def __init__(self, timeMillisBetweenWorkCalls = 50):
        Scheduler.timeMillisBetweenWorkCalls = timeMillisBetweenWorkCalls
        self.coroutines = []
        self.timeOfLastCall = Scheduler.currentTimeMillis()
        self.updateCoroutine = Scheduler.makeCoroutine( self.nullCoroutine() ) # for testing - usually replaced.
        #: The most recent exception raised by a coroutine:
        self.lastExceptionCaught = Exception("None")

    def doWork(self):
        'Executes all the coroutines, handling exceptions'

        timeNow = Scheduler.currentTimeMillis()
        if timeNow == self.timeOfLastCall: # Ensure each call gets a different timer value.
            return
        self.timeOfLastCall = timeNow
        self.updateCoroutine.call()
        for coroutine in self.coroutines[:]:   # Copy of coroutines, so it doesn't matter removing one
            coroutine.call()
            if not coroutine.is_alive():
                self.coroutines.remove(coroutine)
                self.lastExceptionCaught = coroutine.lastExceptionCaught

        self.updateCoroutine.call()

    def timeMillisToNextCall(self):
        'Wait time before the next doWork call should be called.'
        timeRequired = self.timeMillisBetweenWorkCalls + self.timeOfLastCall - Scheduler.currentTimeMillis()
        return max( timeRequired, 0 )


    def addSensorCoroutine(self, *coroutineList):
        '''Adds one or more new sensor/program coroutines to be scheduled, answering the last one to be added.
        Sensor coroutines are scheduled *before* Action coroutines'''
        for generatorFunction in coroutineList:
            latestAdded = Scheduler.makeCoroutine(generatorFunction)
            self.coroutines.insert(0, latestAdded)
        return generatorFunction

    def addActionCoroutine(self, *coroutineList):
        '''Adds one or more new motor control coroutines to be scheduled, answering the last coroutine to be added.
        Action coroutines are scheduled *after* Sensor coroutines'''
        for generatorFunction in coroutineList:
            latestAdded = Scheduler.makeCoroutine(generatorFunction)
            self.coroutines.append(latestAdded)
        return generatorFunction

    def setUpdateCoroutine(self, coroutine):
        # Private - set the coroutine that manages the interaction with the BrickPi.
        # The coroutine will be invoked once at the start and once at the end of each doWork call.
        self.updateCoroutine = Scheduler.makeCoroutine(coroutine)

    def findCoroutineForGenerator(self, generator):
        return (c for c in self.coroutines if c.generator == generator).next()

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
    # Generator-based coroutines.  Kept for backward compatibility.
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

