# Scheduler
# Support for coroutines using Python generator functions.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import logging
import sys, traceback
import threading
import datetime

class StopCoroutineException( Exception ):
    '''Exception used to stop a coroutine'''
    pass

ProgramStartTime = datetime.datetime.now()

class Coroutine( threading.Thread ):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.logger = logging
        self.mySemaphore = threading.Semaphore(0)
        self.callerSemaphore = threading.Semaphore(0)
        self.stopEvent = threading.Event()
        self.setDaemon(True) # Daemon threads don't prevent the process from exiting.
        self.func = func
        self.lastExceptionCaught = None
        self.start()

    @staticmethod
    def currentTimeMillis():
        'Answers the time in floating point milliseconds since program start.'
        global ProgramStartTime
        c = datetime.datetime.now() - ProgramStartTime
        return c.days * (3600.0 * 1000 * 24) + c.seconds * 1000.0 + c.microseconds / 1000.0

    def run(self):
        self.callResult = None
        try:
            self.mySemaphore.acquire()
            self.func(*self.args,**self.kwargs)
        except (StopCoroutineException, StopIteration):
            pass
        except Exception as e:
            self.lastExceptionCaught = e
            self.logger.info( "Coroutine - caught exception: %r" % (e) )
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = "".join(traceback.format_tb(exc_traceback))
            self.logger.debug( "Traceback (latest call first):\n %s" % trace )
        self.stopEvent.set() # Need to tell caller to do a join.
        self.callerSemaphore.release()
        threading.Thread.run(self) # Does some cleanup.

    def call(self, param = None):
        '''Executed from the caller thread.  Runs the coroutine until it calls wait.
        Does nothing if the thread has terminated.
        If a parameter is passed, it is returned from the Coroutine.wait() function in the coroutine thread.'''
        if self.is_alive():
            self.callParam = param
            self.mySemaphore.release()
            self.callerSemaphore.acquire()
            if self.stopEvent.is_set():
                self.join() # Ensure that is_alive is false on exit.
        return self.callResult

    def stop(self):
        '''Executed from the caller thread.  Stops the coroutine, causing its thread to terminate.
        On completion the thread has terminated: is_active() is false.
        To support this, a coroutine mustn't catch the StopCoroutineException (unless it re-raises it).
        '''
        self.stopEvent.set()
        self.call()
        self.join()

    @staticmethod
    def wait(param = None):
        '''Called from within the coroutine to hand back control to the caller thread.
        If a parameter is passed, it will be returned from Coroutine.call in the caller thread.
        '''
        self=threading.currentThread()
        self.callResult = param
        self.callerSemaphore.release()
        self.mySemaphore.acquire()
        if (self.stopEvent.isSet()):
            raise StopCoroutineException()
        return self.callParam

    @staticmethod
    def waitMilliseconds(timeMillis):
        '''Called from within the coroutine to wait the given time.
        I.e. Invocations of the coroutine using call() will do nothing until then. '''
        startTime = Coroutine.currentTimeMillis()
        while Coroutine.currentTimeMillis() - startTime < timeMillis:
            Coroutine.wait()

    @staticmethod
    def runTillFirstCompletes(*coroutines):
        def runTillFirstCompletesFunc(*coroutineList):
            while all(c.is_alive() for c in coroutineList):
                for c in coroutineList:
                    c.call()
                    if not c.is_alive():
                        break
                Coroutine.wait()
            for c in coroutineList:
                if c.is_alive():
                    c.stop()

        result = Coroutine(runTillFirstCompletesFunc, *coroutines)
        return result

    @staticmethod
    def runTillAllComplete(*coroutines):
        def runTillAllCompleteFunc(*coroutineList):
            while any(c.is_alive() for c in coroutineList):
                for c in coroutineList:
                    c.call()
                Coroutine.wait()

        result = Coroutine(runTillAllCompleteFunc, *coroutines)
        return result

    def withTimeout(self, timeoutMillis):
        '''Answers this coroutine, decorated with a timeout that stops it if called after timeoutMillis has elapsed.
        '''
        def timeoutFunc(timeoutMillis):
            Coroutine.waitMilliseconds(timeoutMillis)
        result = Coroutine.runTillFirstCompletes(self, Coroutine(timeoutFunc, timeoutMillis))
        return result

