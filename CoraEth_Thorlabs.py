import socket
from PyQt5 import QtCore


class CoraZ7Eth():
    def __init__(self, parent=None):
        super(CoraZ7Eth,self).__init__()
        self.Cora = None
    def Connect(self, IP, PORT):



        self.Cora = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Cora.settimeout(0.5)
        try:
            self.Cora.connect((IP, PORT))
            self.EthThread = EthThread((IP, PORT))
            self.Cora.close()
            return "Connected to CoraZ7\n"
        except:
            return "Cant find Coraz7\n"

    def StartAcquisition(self):
        try:
            while self.EthThread.isRunning():
                None
            self.EthThread.setTerminationEnabled(True)
            self.EthThread.start()
            return "Started"
        except:
            return "Failed"


class EthThread(QtCore.QThread):

    Error = QtCore.pyqtSignal(str)
    DataReady = QtCore.pyqtSignal(bytearray)

    def __init__(self, conndata, parent=None):
        super(EthThread, self).__init__()
        self.conndata = conndata

    def run(self):

        self.running = True
        self.rec = bytearray()
        gesval=0
        print("start")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Cora:
            try:
                Cora.connect(self.conndata)
                Cora.sendall(b'Hallo')
                Cora.recv(64)
            except:
                self.Error.emit("Connection Failure ")
                self.running = False
                self.DataReady.emit(bytearray())
                print("end")
                self.rec.clear()
                return

            while self.running:
                if(gesval>300000):
                    self.running = False
                    print("Overflow")

                    for i in range(0,20):
                        self.msleep(0.5)
                        if self.running==False:
                            continue

                    self.rec.clear()

                Cora.sendall(b'flush')
                try:
                    buff = Cora.recv(4096)
                    gesval = gesval+len(buff)
                    #print(len(buff))
                    self.rec.extend(buff)

                except:
                    self.Error.emit("Error")
                    self.msleep(50)
                    self.DataReady.emit(bytearray())
                    print("end")
                    return



            Cora.sendall(b'flush')
            try:
                buff = Cora.recv(4096)
                self.rec.extend(buff)

            except:
                self.Error.emit("Error")
                print("end")
                self.DataReady.emit(bytearray())
                return
            self.usleep(2000)
            Cora.sendall(b'Sag')
            print(len(self.rec))
            if len(self.rec)<100:
                self.Error.emit("Error")
                print("end")
                self.DataReady.emit(bytearray())
                return
            else:
                self.DataReady.emit(self.rec)
            print("end")
        return

    def KillSelf(self):
        self.running = False
        #print("Terminated")
