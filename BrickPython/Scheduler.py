
# Scheduler.  To be called repeatedly by the UI or other framework.
import datetime
import sys

# Exception used to stop a coroutine:
class StopCoroutineException( Exception ):
    pass

ProgramStartTime = datetime.datetime.now()

class Scheduler():
    
    # Public members:
    #    latestSensorCoroutine - the most recent sensor/control coroutine to have been added.
    #    latestActionCoroutine - the most recent motor control coroutine to have been added.
    
    # Answers the time in ms since program start.
    @staticmethod
    def currentTimeMillis():
        global ProgramStartTime
        c = datetime.datetime.now() - ProgramStartTime
        return c.days * (3600.0 * 1000 * 24) + c.seconds * 1000.0 + c.microseconds / 1000.0

    # Noop coroutine - does nothing
    @staticmethod
    def nullCoroutine():
        while True:
            yield
    
    def __init__(self, timeMillisBetweenWorkCalls = 20):
        self.timeMillisBetweenWorkCalls = timeMillisBetweenWorkCalls
        self.coroutines = []
        self.timeOfLastCall = Scheduler.currentTimeMillis()
        self.updateCoroutine = self.nullCoroutine() # for testing - usually replaced.

    # Private: Executes all the coroutines, handling exceptions.
    def doWork(self):
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

    # Private: Wait time before the next doWork call should be called.
    def timeMillisToNextCall(self):
        timeRequired = self.timeMillisBetweenWorkCalls + self.timeOfLastCall - Scheduler.currentTimeMillis()
        return max( timeRequired, 0 )

    # Add one or more new sensor/program coroutines to be scheduled, answering the last one.
    def addSensorCoroutine(self, *coroutineList):
        self.coroutines[0:0] = coroutineList
        self.latestSensorCoroutine = coroutineList[-1]
        return self.latestSensorCoroutine

    # Add one or more new motor control coroutines to be scheduled, answering the last coroutine to be added.
    def addActionCoroutine(self, *coroutineList):
        self.coroutines.extend( coroutineList )
        self.latestActionCoroutine = coroutineList[-1]
        return self.latestActionCoroutine

    # Private - set the coroutine that manages the interaction with the BrickPi.
    # This will be invoked once at the start of each doWork call, and then again at the end.
    def addUpdateCoroutine(self, coroutine):
        self.updateCoroutine = coroutine

    # Terminate the given one or more coroutines
    def stopCoroutine( self, *coroutineList ):
        for coroutine in coroutineList:
            try:
                coroutine.throw(StopCoroutineException)
            except (StopCoroutineException,StopIteration):  # If the coroutine doesn't catch the exception to tidy up, it comes back here.
                self.coroutines.remove( coroutine )

    # Terminate all coroutines - use with care, of course!
    def stopAllCoroutines(self):
        self.stopCoroutine(*self.coroutines[:]) # Makes a copy of the list - don't want to be changing it.

    # Number of active coroutines
    def numCoroutines( self ):
        return len(self.coroutines)
    
    # Answers whether any of the given coroutines are still executing
    def stillRunning( self, *coroutineList ):
        return any( c in self.coroutines for c in coroutineList )
    

    # Coroutine that executes the given coroutines until the first completes, then stops the others and finishes.
    def runTillFirstCompletes( self, *coroutineList ):
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
    
    # Coroutine that executes the given coroutines until all have completed.
    def runTillAllComplete(self, *coroutineList ):
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

    # Coroutine that waits for timeMillis, then finishes.
    def doWait( self, timeMillis ):
        t = Scheduler.currentTimeMillis()
        while Scheduler.currentTimeMillis() - t < timeMillis:
            yield

    # Coroutine that wraps the given coroutine with a timeout:
    def withTimeout( self, timeoutMillis, coroutine ):
        return self.runTillFirstCompletes( coroutine, self.doWait( timeoutMillis ) )

