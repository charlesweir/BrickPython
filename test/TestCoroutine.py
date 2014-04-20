# Tests for Scheduler
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

# Run tests as
#   python TestCoroutine.py
# or, if you've got it installed:
#   nosetests



from BrickPython.Coroutine import *
import unittest
import logging
from mock import *

class TestCoroutine(unittest.TestCase):
    ''' Tests for the Scheduler class, its built-in coroutines, and its coroutine handling.
    '''
    coroutineCalls = []
    @staticmethod
    def dummyCoroutineFunc():
        for i in range(1, 5):
            TestCoroutine.coroutineCalls.append(i)
            Coroutine.wait();

    @staticmethod
    def dummyCoroutineFuncThatDoesCleanup():
        for i in range(1, 6):
            TestCoroutine.coroutineCalls.append(i)
            try:
                Coroutine.wait()
            finally:
                TestCoroutine.coroutineCalls.append( -1 )

    @staticmethod
    def dummyCoroutineFuncThatThrowsException():
        raise Exception("Hello")

    def setUp(self):
        TestCoroutine.coroutineCalls = []

    def tearDown(self):
        pass

    def testCoroutinesGetCalledUntilDone(self):
        # When we start a coroutine
        f = TestCoroutine.dummyCoroutineFunc
        coroutine = Coroutine( f )
        # It's a daemon thread
        self.assertTrue( coroutine.isDaemon())
        # It doesn't run until we call it.
        self.assertEqual(TestCoroutine.coroutineCalls, [] )
        # Each call gets one iteration
        coroutine.call()
        self.assertEqual(TestCoroutine.coroutineCalls, [1] )
        # And when we run it until finished
        for i in range(0,10):
            coroutine.call()
        # It has completed
        self.assertEqual(TestCoroutine.coroutineCalls, [1,2,3,4] )
        self.assertFalse( coroutine.isAlive() )

    def testCoroutinesGetStoppedAndCleanedUp(self):
        # When we start a coroutine
        coroutine = Coroutine(TestCoroutine.dummyCoroutineFuncThatDoesCleanup)
        # run it for a bit then stop it
        coroutine.call()
        coroutine.stop()
        # It has stopped and cleaned up
        self.assertFalse( coroutine.isAlive())
        self.assertEquals( TestCoroutine.coroutineCalls, [1,-1] )

    def testCoroutineExceptionLogging(self):
        coroutine = Coroutine(TestCoroutine.dummyCoroutineFuncThatThrowsException)
        coroutine.logger = Mock()
        coroutine.call()
        self.assertTrue(coroutine.logger.info.called)
        firstParam = coroutine.logger.info.call_args[0][0]
        self.assertRegexpMatches(firstParam, "Coroutine - caught exception: .*Exception.*")
        self.assertRegexpMatches(coroutine.logger.debug.call_args[0][0], "Traceback.*")


    def testCoroutineWaitMilliseconds(self):
        def dummyCoroutineFuncWaiting1Sec():
            Coroutine.waitMilliseconds(1000)

        coroutine = Coroutine(dummyCoroutineFuncWaiting1Sec)
        # Doesn't matter not restoring this; tests never use real time:
        Coroutine.currentTimeMillis = Mock(side_effect = [1,10,500,1200])
        for i in range(1,3):
            coroutine.call()
            self.assertTrue(coroutine.is_alive(),"Coroutine dead at call %d" % i)
        coroutine.call()
        self.assertFalse(coroutine.is_alive())

    def testCoroutineCanHaveParameters(self):
        def func(*args, **kwargs):
            print "In coroutine: %r %r" % (args, kwargs)
            self.assertEquals(args, (1))
            self.assertEquals(kwargs, {"extra": 2})
        coroutine = Coroutine(func, 1, extra=2)
        coroutine.call()

        pass

    def testWaitCanPassAndReceiveParameters(self):
        pass

    def testRunCoroutinesUntilFirstCompletes(self):
        pass

    def testRunCoroutinesUntilAllComplete(self):
        pass



#     def testWaitMilliseconds(self):
#         # If we wait for 10 ms
#         for i in self.scheduler.waitMilliseconds(10):
#             pass
#         # that's about the time that will have passed:
#         assert( self.scheduler.currentTimeMillis() in range(10,12) )
#
#     def testRunTillFirstCompletes(self):
#         # When we run three coroutines using runTillFirstCompletes:
#         for i in self.scheduler.runTillFirstCompletes(TestCoroutine.dummyCoroutine(1,9),
#                                                       TestCoroutine.dummyCoroutine(1,2),
#                                                       TestCoroutine.dummyCoroutine(1,9) ):
#             pass
#         #  the first to complete stops the others:
#         self.assertEquals( TestCoroutine.coroutineCalls, [1,1,1,2] )
#         self.assertEquals( self.scheduler.numCoroutines(), 0)
#
#     def testRunTillAllComplete( self ):
#         # When we run three coroutines using runTillAllComplete:
#         for i in self.scheduler.runTillAllComplete( *[TestCoroutine.dummyCoroutine(1,i) for i in [2,3,4]] ):
#             pass
#         #  they all run to completion:
#         print TestCoroutine.coroutineCalls
#         assert( TestCoroutine.coroutineCalls == [1,1,1,2,2,3] )
#         assert( self.scheduler.numCoroutines() == 0)
#
#     def testWithTimeout(self):
#         # When we run a coroutine with a timeout:
#         for i in self.scheduler.withTimeout(10, TestCoroutine.dummyCoroutineThatDoesCleanup(1,99) ):
#             pass
#         # It completes at around the timeout, and does cleanup:
#         print TestCoroutine.coroutineCalls
#         self.assertTrue( 0 < TestCoroutine.coroutineCalls[-2] <= 10) # N.b. currentTimeMillis is called more than once per doWork call.
#         self.assertEquals( TestCoroutine.coroutineCalls[-1], -1 )
#
#     def testTimeMillisToNextCall(self):
#         # Given a mock timer, and a different scheduler set up with a known time interval
#         scheduler = Scheduler(20)
#         # when we have just coroutines that take no time
#         scheduler.addActionCoroutine( TestCoroutine.dummyCoroutine() )
#         # then the time to next tick is the default less a bit for the timer check calls:
#         scheduler.doWork()
#         ttnt = scheduler.timeMillisToNextCall()
#         assert( ttnt in range(17,20) )
#         # when we have an additional coroutine that takes time
#         scheduler.addSensorCoroutine( TestCoroutine.dummyCoroutineThatTakesTime() )
#         # then the time to next tick is less by the amount of time taken by the coroutine:
#         scheduler.doWork()
#         ttnt = scheduler.timeMillisToNextCall()
#         assert( ttnt in range(7,10) )
#         # but when the coroutines take more time than the time interval available
#         for i in range(0,2):
#             scheduler.addSensorCoroutine( TestCoroutine.dummyCoroutineThatTakesTime() )
#         # the time to next tick never gets less than zero
#         scheduler.doWork()
#         ttnt = scheduler.timeMillisToNextCall()
#         assert( ttnt == 0 )
#         # and incidentally, we should have all the coroutines still running
#         assert( scheduler.numCoroutines() == 4 )
#
#     def timeCheckerCoroutine(self):
#         # Helper coroutine for testEachCallToACoroutineGetsADifferentTime
#         # Checks that each call gets a different time value.
#         time = Scheduler.currentTimeMillis()
#         while True:
#             yield
#             newTime = Scheduler.currentTimeMillis()
#             self.assertNotEquals( newTime, time )
#             time = newTime
#
#     def testEachCallToACoroutineGetsADifferentTime(self):
#         scheduler = Scheduler()
#         Scheduler.currentTimeMillis =  Mock( side_effect = [0,0,0,0,0,0,0,0,0,0,1,2,3,4,5] )
#         # For any coroutine,
#         scheduler.setUpdateCoroutine( self.timeCheckerCoroutine() )
#         # We can guarantee that the timer always increments between calls (for speed calculations etc).
#         for i in range(1,10):
#             scheduler.doWork()
#
#     def testTheWaitForCoroutine(self):
#         scheduler = Scheduler()
#         arrayParameter = []
#         # When we create a WaitFor coroutine with a function that takes one parameter (actually an array)
#         coroutine = scheduler.waitFor( lambda ap: len(ap) > 0, arrayParameter )
#         # It runs
#         for i in range(0,5):
#             coroutine.next()
#         # Until the function returns true.
#         arrayParameter.append(1)
#         TestCoroutine.checkCoroutineFinished( coroutine )
#
#     @staticmethod
#     def throwingCoroutine():
#         yield
#         raise Exception("Hello")
#
#     def testExceptionThrownFromCoroutine(self):
#         scheduler = Scheduler()
#         self.assertIsNotNone(scheduler.lastExceptionCaught)
#         scheduler.addActionCoroutine(self.throwingCoroutine())
#         for i in range(1,3):
#             scheduler.doWork()
#         self.assertEquals(scheduler.lastExceptionCaught.message, "Hello")
#
#     def testRunTillFirstCompletesWithException(self):
#         # When we run three coroutines using runTillFirstCompletes:
#         self.scheduler.addActionCoroutine(self.scheduler.runTillFirstCompletes(self.throwingCoroutine(),
#                                                       TestCoroutine.dummyCoroutine(1,2),
#                                                       TestCoroutine.dummyCoroutine(1,9) ))
#         for i in range(1,10):
#             self.scheduler.doWork()
#         #  the first to complete stops the others:
#         self.assertEquals( TestCoroutine.coroutineCalls, [1,1] )
#         self.assertEquals( self.scheduler.numCoroutines(), 0)
#         # and the exception is caught by the Scheduler:
#         self.assertEquals(self.scheduler.lastExceptionCaught.message, "Hello")
#
#     def testRunTillAllCompleteWithException( self ):
#         # When we run three coroutines using runTillAllComplete:
#         self.scheduler.addActionCoroutine(self.scheduler.runTillAllComplete(self.throwingCoroutine(),
#                                                       TestCoroutine.dummyCoroutine(1,2)))
#         for i in range(1,10):
#             self.scheduler.doWork()
#         #  the first to complete stops the others:
#         self.assertEquals( TestCoroutine.coroutineCalls, [1] )
#         self.assertEquals( self.scheduler.numCoroutines(), 0)
#         # and the exception is caught by the Scheduler:
#         self.assertEquals(self.scheduler.lastExceptionCaught.message, "Hello")
#
#     def testCanCatchExceptionWithinNestedCoroutines(self):
#         self.caught = 0
#         def outerCoroutine(self):
#             try:
#                 for i in self.throwingCoroutine():
#                     yield
#             except:
#                 self.caught = 1
#         for i in outerCoroutine(self):
#             pass
#         self.assertEquals(self.caught, 1)


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.DEBUG) # Logging is a simple print
    unittest.main()

