
# Scheduler.  To be called repeatedly by the UI or other framework.
import datetime
import sys

class StopCoroutineException( Exception ):
    '''Exception used to stop a coroutine:'''
    pass

ProgramStartTime = datetime.datetime.now()


class Scheduler():
    ''' This manages an arbitrary number of coroutines (implemented as generator functions), supporting
    invoking each every *timeMillisBetweenWorkCalls*, and detecting when each has completed.

    It supports one special coroutine - the updatorCoroutine, which is invoked before and after all the other ones.
    '''

    @staticmethod
    def currentTimeMillis():
        'Answers the time in floating point milliseconds since program start.'
        global ProgramStartTime
        c = datetime.datetime.now() - ProgramStartTime
        return c.days * (3600.0 * 1000 * 24) + c.seconds * 1000.0 + c.microseconds / 1000.0


    @staticmethod
    def nullCoroutine():
        # Noop coroutine - does nothing
        while True:
            yield

    def __init__(self, timeMillisBetweenWorkCalls = 20):
        self.timeMillisBetweenWorkCalls = timeMillisBetweenWorkCalls
        self.coroutines = []
        self.timeOfLastCall = Scheduler.currentTimeMillis()
        self.updateCoroutine = self.nullCoroutine() # for testing - usually replaced.

    def doWork(self):
        # Private: Executes all the coroutines, handling exceptions.

        timeNow = Scheduler.currentTimeMillis()
        if timeNow == self.timeOfLastCall: # Ensure each call gets a different timer value.
            return
        self.timeOfLastCall = timeNow
        self.updateCoroutine.next()
        for coroutine in self.coroutines[:]:   # Copy of coroutines, so it doesn't matter removing
            try:
                coroutine.next()
            except (StopIteration):
                self.coroutines.remove( coroutine )
            except Exception as e:
                print "Got exception: ", e
                self.coroutines.remove( coroutine )

        self.updateCoroutine.next()

    def timeMillisToNextCall(self):
        # Private: Wait time before the next doWork call should be called.
        timeRequired = self.timeMillisBetweenWorkCalls + self.timeOfLastCall - Scheduler.currentTimeMillis()
        return max( timeRequired, 0 )


    def addSensorCoroutine(self, *coroutineList):
        'Add one or more new sensor/program coroutines to be scheduled, answering the last one to be added.'
        self.coroutines[0:0] = coroutineList
        return coroutineList[-1]

    def addActionCoroutine(self, *coroutineList):
        'Add one or more new motor control coroutines to be scheduled, answering the last coroutine to be added.'
        self.coroutines.extend( coroutineList )
        return coroutineList[-1]

    def addUpdateCoroutine(self, coroutine):
        # Private - set the coroutine that manages the interaction with the BrickPi.
        # The coroutine will be invoked once at the start and once at the end of each doWork call.
        self.updateCoroutine = coroutine

    def stopCoroutine( self, *coroutineList ):
        'Terminate the given one or more coroutines'
        for coroutine in coroutineList:
            try:
                coroutine.throw(StopCoroutineException)
            except (StopCoroutineException,StopIteration):  # If the coroutine doesn't catch the exception to tidy up, it comes back here.
                self.coroutines.remove( coroutine )

    def stopAllCoroutines(self):
        'Terminate all coroutines (except the updater one) - use with care, of course!'
        self.stopCoroutine(*self.coroutines[:]) # Makes a copy of the list - don't want to be changing it.

    def numCoroutines( self ):
        'Answers the number of active coroutines'
        return len(self.coroutines)

    def stillRunning( self, *coroutineList ):
        'Answers whether any of the given coroutines are still executing'
        return any( c in self.coroutines for c in coroutineList )

    def runTillFirstCompletes( self, *coroutineList ):
        'Coroutine that executes the given coroutines until the first completes, then stops the others and finishes.'
        while True:
            for coroutine in coroutineList:
                try:
                    coroutine.next()
                except (StopIteration, StopCoroutineException):
                    return # CW - I don't understand it, but we don't seem to need to terminate the others explicitly.
                except Exception as e:
                    print "Got exception: ", e
                    return
            yield

    def runTillAllComplete(self, *coroutineList ):
        'Coroutine that executes the given coroutines until all have completed.'
        coroutines = list( coroutineList )
        while coroutines != []:
            for coroutine in coroutines:
                try:
                    coroutine.next()
                except (StopIteration, StopCoroutineException):
                    coroutines.remove( coroutine )
                except Exception as e:
                    print "Got exception: ", e
                    return
            yield

    def doWait( self, timeMillis ):
        'Coroutine that waits for timeMillis, then finishes.'
        t = Scheduler.currentTimeMillis()
        while Scheduler.currentTimeMillis() - t < timeMillis:
            yield

    def withTimeout( self, timeoutMillis, coroutine ):
        'Coroutine that wraps the given coroutine with a timeout'
        return self.runTillFirstCompletes( coroutine, self.doWait( timeoutMillis ) )

    def waitFor(self, function, *args ):
        'Coroutine that waits until the given function (with optional parameters) returns True.'
        while not function(*args):
            yield
