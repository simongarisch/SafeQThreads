'''
defines the classes:
-> SafeQThread (inherits from QtCore.QThread) and
-> SafeWorker (inherits from QtCore.QObject)

Objects for each of these classes will have a stop_running attribute (bool)
that we can set to True if we want to indicate this thread should exit early.

a close_all_threads function is also provided that, when called,
will go through all existing SafeQThread objects and:
-> set the object attribute stop_running = True
-> call thread.quit()
-> wait for all SafeQThread objects to exit subject to a timeout of max_wait_seconds
'''

import time
from weakref import WeakSet
from qtpy import QtWidgets, QtCore
from . import errors
from .descriptors import StopRunning


class SafeQThread(QtCore.QThread):
    ''' make sure this thread stops when the app closes '''
    stop_running = StopRunning()
    thread_set = WeakSet()
    
    def __init__(self, parent=None):
        ''' initialise our thread object '''
        super(SafeQThread, self).__init__(parent)
        self.parent = parent
        self.stop_running = False
        self._worker = None
        self.thread_set.add(self) # add this thread to the thread set

    @classmethod
    def stop_all_threads(cls):
        ''' set the stop_running attribute to True for all threads
            and their workers (if they have one)
        '''
        for thread in cls.thread_set:
            worker = thread.worker
            if worker is not None:
                worker.stop_running = True
            thread.stop_running = True
            
    @classmethod
    def quit_all_threads(cls):
        ''' call quit on all SafeQThread instances '''
        for thread in cls.thread_set:
            thread.quit()

    @classmethod
    def any_threads_busy(cls):
        checks = [thread.isRunning() for thread in cls.thread_set]
        return(True if True in checks else False)

    @property
    def worker(self):
        return(self._worker)

    def register_worker(self, worker):
        ''' register a worker QtCore.QObject associated with this thread
            there should only be one worker per thread '''
        if not isinstance(worker, SafeWorker):
            raise errors.WorkerTypeError
        if self._worker is not None:
            raise errors.WorkerAlreadyRegisteredError
        self._worker = worker


class SafeWorker(QtCore.QObject):
    ''' a QObject that has a stop_running attribute that associated QThreads can call '''
    stop_running = StopRunning() # descriptor for the stopRunning attribute
    def __init__(self, thread, parent=None):
        super(SafeWorker, self).__init__(parent)
        if not isinstance(thread, SafeQThread):
            raise errors.SafeQThreadTypeError
        self.stop_running = False
        thread.register_worker(self)


def close_all_threads(max_wait_seconds=3):
    ''' wait for a certain number of seconds (max_wait_seconds) for the threads to finish '''

    if not isinstance(max_wait_seconds, int):
        raise errors.MaxWaitSecondsTypeError
    
    start = time.time()
    app = QtWidgets.QApplication.instance()
    SafeQThread.stop_all_threads() # set stop_running attribute to true for all SafeQThread instances
    SafeQThread.quit_all_threads() # and call thread.quit for each of these threads
    while SafeQThread.any_threads_busy():
        if app is not None:
            # http://pyqt.sourceforge.net/Docs/PyQt4/qcoreapplication.html#processEvents
            app.processEvents()
        end = time.time()
        if (end - start) > max_wait_seconds:
            return
