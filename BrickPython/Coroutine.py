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
        print "Coroutine: %r %r" % (args, kwargs)
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
            while True:
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

#
#         self.scheduler.coroutines.remove( self )
#         self.scheduler.semaphore.release()

class GeneratorCoroutineWrapper(Coroutine):
    '''Internal: Wraps a generator-style coroutine with a thread'''

    def __init__(self, scheduler, generator):
        '''`scheduler` - the main Scheduler object
        `generator` - the generator object created by calling the generator function'''
        Coroutine.__init__(self)
        self.scheduler = scheduler
        self.stopEvent = threading.Event()
        self.generator = generator
        self.thread = threading.Thread(target=self.action)
        self.thread.setDaemon(True) # Daemon threads don't prevent the process from exiting.
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
        'Causes the thread to stop - executed from the scheduler thread'
        self.stopEvent.set()

