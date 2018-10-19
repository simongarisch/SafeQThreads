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
    #safeqthreads.close_all_threads() # <-- comment me out and see what happens


if __name__ == "__main__":
    main()