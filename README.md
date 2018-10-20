[![Build Status](https://travis-ci.org/simongarisch/safeqthreads.svg?branch=master)](https://travis-ci.org/simongarisch/safeqthreads)
[![Coverage Status](https://coveralls.io/repos/github/simongarisch/safeqthreads/badge.svg?branch=master)](https://coveralls.io/github/simongarisch/safeqthreads?branch=master)

# safeqthreads

The motivation behind safeqthreads is to allow Qthreads to finish before the application exits. If the application exits before a QThread is finished the Python garbage collector will release the QThread and potentially cause Python to crash.

## Installation
safeqthreads is both python 2 and 3 compatible
```bash
pip install safeqthreads
```

## QThreads and the Python garbage collector (gc)
If the Python gc releases a QThread before PyQt is finished with it then this can cause Python to crash. Here is a basic example:
```python
# how to crash PyQt 101 ...
from PyQt5 import QtWidgets, QtCore
import time

def targetFunc():
    time.sleep(5)

def runThread():
    thread = QtCore.QThread()
    thread.started.connect(targetFunc)
    thread.start()
    
runThread()
```
![Python crashes](https://github.com/simongarisch/safeqthreads/blob/master/crash.png)

This same issue can occur when a PyQt application exits before QThreads are finished.

## Some background
There are a couple of ways that you can run threads in PyQt:
-  The [threading module](https://docs.python.org/3/library/threading.html) within the Python standard library
-  Use [QThread](http://pyqt.sourceforge.net/Docs/PyQt4/qthread.html) from PyQt

When working with PyQt the QThreads option gives you access to additional PyQt functionality such as signals and slots. <br>

We can create threads using the standard library by inheriting from the threading.Thread class and overriding the run method; you'll see many examples of QThread implemented in this way, but it's [not recommended](http://blog.qt.io/blog/2010/06/17/youre-doing-it-wrong/). Instead, it's suggested that a worker (which inherits from QObject) be created and moved to a thread with its [moveToThread](http://pyqt.sourceforge.net/Docs/PyQt4/qobject.html#moveToThread) method. We'll provide examples of using safeqthreads with both.

## Using safeqthreads with threads and workers
safeqthreads.close_all_threads() is the last line that runs at the end of the main function. If you comment this line out then there is a chance that you'll get either of:
-  A warning of 'QThread: Destroyed while ethread is still running'
-  Python has stopped working (a crash)
```python
import time
from PyQt5 import QtWidgets, QtCore
import safeqthreads

class UpdateSignal(QtCore.QObject):
    fire = QtCore.pyqtSignal(int)
    
class SomeWorker(safeqthreads.SafeWorker):
    ''' a worker that does something trivial like
        incrementing a counter every second
    '''
    def __init__(self, thread, signal):
        # this thread will be passed to the constructor of SafeWorker
        # which will register this worker with the thread
        super(SomeWorker, self).__init__(thread)
        self.signal = signal
        self.counter = 0

    def loop(self):
        while True:
            if self.stop_running:
                return
            else:
                self.counter += 1
                self.signal.fire.emit(self.counter)
            time.sleep(3)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("The Main Window")
        self.resize(300, 300)
        self.create_thread()

    def create_thread(self):
        # create the signal
        signal = self.signal = UpdateSignal()
        signal.fire.connect(self.signal_catcher)

        # then create an instance of SafeQThread
        thread = self.thread = safeqthreads.SafeQThread()
        worker = self.worker = SomeWorker(thread, signal)

        # http://pyqt.sourceforge.net/Docs/PyQt4/qobject.html#moveToThread
        worker.moveToThread(thread)
        thread.started.connect(worker.loop)
        thread.start()

    @QtCore.pyqtSlot(int)
    def signal_catcher(self, counter):
        self.setWindowTitle(str(counter))

        
def main():
    app = QtWidgets.QApplication([]) # create the app instance
    win = MainWindow()
    win.show()                       # show the window
    app.exec_()                      # enter the app mainloop
    safeqthreads.close_all_threads() # <-- comment me out and see what happens


if __name__ == "__main__":
    main()
```

Here is my terminal before and after commenting out 'safeqthreads.close_all_threads()'.
![QThread destroyed](https://github.com/simongarisch/safeqthreads/blob/master/commenting_out.png)

## Using safeqthreads and inheriting from QThread
As mentioned earlier, this is not the recommended approach. Use worker and moveToThread() instead as detailed above. In any case, here is an example where we inherit from QThread and override the run method.
```python
import time
from PyQt5 import QtWidgets, QtCore
import safeqthreads

class UpdateSignal(QtCore.QObject):
    fire = QtCore.pyqtSignal(int)


class SomeThread(safeqthreads.SafeQThread):
    def __init__(self, signal):
        super(SomeThread, self).__init__()
        self.signal = signal
        self.counter = 0
        self.start()
        
    def run(self):
        ''' this performs like our worker.loop method 
            from the previous example '''
        while True:
            if self.stop_running:
                return
            else:
                self.counter += 1
                self.signal.fire.emit(self.counter)
            time.sleep(3)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("The Main Window")
        self.resize(300, 300)
        self.create_thread()

    def create_thread(self):
        signal = self.signal = UpdateSignal()
        signal.fire.connect(self.signal_catcher)
        thread = self.thread = SomeThread(signal) # and create our thread

    @QtCore.pyqtSlot(int)
    def signal_catcher(self, counter):
        self.setWindowTitle(str(counter))


def main():
    app = QtWidgets.QApplication([]) # create the app instance
    win = MainWindow()
    win.show()                       # show the window
    app.exec_()                      # enter the app mainloop
    safeqthreads.close_all_threads()


if __name__ == "__main__":
    main()
```
