'''
test the main functionality of our package
'''

import time
from qtpy import QtWidgets
import pytest
import safeqthreads
from safeqthreads import errors


class TestSafeQThread(object):
    
    def test_safeqthread(self):
        ''' check the basic setup of a SafeQThread instance '''
        thread = safeqthreads.SafeQThread()
        assert thread.parent is None
        assert thread.stop_running is False
        thread.stop_running = True
        assert thread.stop_running is True
        with pytest.raises(errors.StopRunningNotBoolError):
            thread.stop_running = "True"

    def test_safe_worker(self):
        ''' check that we can create an instance of SafeWorker '''
        thread = safeqthreads.SafeQThread()
        safeqthreads.SafeWorker(thread) # we need a thread to create the worker
        
        with pytest.raises(errors.SafeQThreadTypeError):
            safeqthreads.SafeWorker(22)
            

    def test_register_worker(self):
        ''' check that we can register a worker '''
        thread = safeqthreads.SafeQThread()
        # registering is automatic in worker constructor
        worker = safeqthreads.SafeWorker(thread)
        assert worker.stop_running is False # should be by default
        
        # test that we can get this worker
        assert id(thread.worker) == id(worker)
        
        # test that we cannot register another worker with this thread
        with pytest.raises(errors.WorkerAlreadyRegisteredError):
            thread.register_worker(worker)

        # test that any registered workers must be instance of SafeWorker
        with pytest.raises(errors.WorkerTypeError):
            thread.register_worker("abc")

    def test_implementation(self):
        ''' create some threads and some workers and check all runs smoothly'''
        app = QtWidgets.QApplication([]) # create our application instance
        
        class SomeWorker(safeqthreads.SafeWorker):
            def __init__(self, thread, sleep_time=1):
                super(SomeWorker, self).__init__(thread)
                self.sleep_time = sleep_time
                
            def loop(self):
                while True:
                    time.sleep(self.sleep_time)
                    if self.stop_running:
                        return
        
        # check this worker
        thread = safeqthreads.SafeQThread()
        worker = SomeWorker(thread)
        worker.stop_running = True
        worker.loop() # will only run once
        
        threads_list = []
        for _ in range(3):
            thread = safeqthreads.SafeQThread()
            worker = SomeWorker(thread) # create a worker for this thread
            worker.moveToThread(thread)
            thread.started.connect(worker.loop)
            thread.start()
            threads_list.append(thread)
        
        # test that max_wait_seconds must be an integer
        with pytest.raises(errors.MaxWaitSecondsTypeError):
            safeqthreads.close_all_threads(max_wait_seconds=2.5) # cannot be a float

        # now wait for these threads to finish before we exit (give it time)
        safeqthreads.close_all_threads(max_wait_seconds=5)
        
        # also test that a wait for QThread to finish will reach the timeout
        thread = safeqthreads.SafeQThread()
        worker = SomeWorker(thread, sleep_time=2)
        worker.moveToThread(thread)
        thread.started.connect(worker.loop)
        thread.start()
        safeqthreads.close_all_threads(max_wait_seconds=0) # not really waiting
        assert thread.isRunning() is True

        # now wait for this thread to finish properly
        safeqthreads.close_all_threads(max_wait_seconds=5)

    def test_safethread(self):
        ''' this tests the SafeThread class (which inherits from threading.Thread)
            not to be confused with the SafeQThread class (which inherits from QtCore.QThread)
        '''
        class SomeThread(safeqthreads.SafeThread):
            def __init__(self):
                super(SomeThread, self).__init__()
                self.start()
                
            def run(self):
                while True:
                    if self.stop_running:
                        return
                    time.sleep(0.1)

        threads_list = [SomeThread() for _ in range(3)]
        safeqthreads.close_all_threads()
        time.sleep(1) # wait for 'if self.stop_running' to evaluate as True
        # all of these threads in threads_list should now have their
        # stop_running attribute set to True
        assert False not in [thread.stop_running for thread in threads_list]
