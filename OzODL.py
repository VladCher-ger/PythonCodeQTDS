from PyQt5 import QtCore

class OzCntrl():
    def __init__(self, ser, parent = None):
        super(OzCntrl,self).__init__()
        self.ser = ser
        self.MotorThread = MotorCntrlThread(ser)
        self.initodl()

    def initodl(self):
        #turn off Echo
        self.ser.write("s0\r\n".encode())
        self.ser.readline()
        self.ser.readline()
        self.ser.timeout = 5
        #Find home
        self.ser.write("FH\r\n".encode())
        self.ser.readline()
        self.ser.readline()


    def close(self):
        self.ser.close()


    def StartRun(self):
        self.MotorThread.setTerminationEnabled(True)
        self.MotorThread.start()

class MotorCntrlThread(QtCore.QThread):

    StartAcquisition = QtCore.pyqtSignal()
    StopAcquisition = QtCore.pyqtSignal()
    def __init__(self, Motor, parent = None):
        super(MotorCntrlThread,self).__init__()
        self.Motor = Motor

    def run(self):
        self.Motor.write("s0\r\n".encode())
        self.Motor.readline()
        self.Motor.readline()

        self.Motor.write("GF\r\n".encode())
        self.Motor.readline()

        self.StartAcquisition.emit()

        self.Motor.readline()

        self.StopAcquisition.emit()

        self.Motor.write("GR\r\n".encode())
        self.Motor.readline()
        self.Motor.readline()
        pass
