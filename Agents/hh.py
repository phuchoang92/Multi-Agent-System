import sys, time
from PyQt5 import QtWidgets, QtCore


class Thread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.pause = False

    def run(self):
        for i in range(100):
            if self.pause:
                print("Paused")
                while self.pause: time.sleep(1)
            print("Number: " + str(i))
            time.sleep(1)


class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'QThread Pause test'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.button = QtWidgets.QPushButton('Pause', self)
        self.button.move(175, 75)
        self.button.clicked.connect(self.thread_pause_resume)
        self.thread = Thread()
        self.show()
        self.thread.start()

    @QtCore.pyqtSlot()
    def thread_pause_resume(self):
        if self.button.text() == "Pause":
            self.thread.pause = True
            self.button.setText("Resume")
        else:
            self.thread.pause = False
            self.button.setText("Pause")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
