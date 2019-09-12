import socket
from PyQt5 import QtCore
import time
from scapy.all import ARP, Ether, srp

class CoraZ7Eth():
    def __init__(self, parent=None):
        super(CoraZ7Eth,self).__init__()
        self.Cora = None

    def Connect(self, MAC, PORT):

        ans,_ = srp(Ether(dst=MAC)/ARP(pdst="134.91.61.0/24"), timeout=1, verbose=False)

        try:
            IP = ans[0][1].psrc
            #print(IP)
        except:
            return "Search unsuccesful\n"

        self.Cora = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Cora.settimeout(2)
        try:
            self.Cora.connect((IP, PORT))
            self.EthThread = EthThread((IP, PORT))
            self.Cora.sendall(b'Init')
            rec = self.Cora.recv(64)
            print(rec)
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
        print(conndata)

    def run(self):

        self.running = True
        self.rec = bytearray()
        gesval=0
        print("start")
        self.usleep(1000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Cora:
            try:
                Cora.connect(self.conndata)
                Cora.sendall(b'Start')
                print(Cora.recv(64))
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
                    self.rec.clear()
                self.msleep(20)
                Cora.sendall(b'flush')
                try:
                    buff = Cora.recv(4096)
                    gesval = gesval+len(buff)

                    if b'Done' in buff:
                        print("Rec end")
                        self.running = False
                        continue
                    self.rec.extend(buff)
                    del buff

                except:
                    self.Error.emit("Error")
                    self.DataReady.emit(bytearray())
                    print("end")
                    del self.rec
                    return


            print(len(self.rec))
            if len(self.rec)<200000:
                self.Error.emit("Error")
                print("end")
                self.DataReady.emit(bytearray())
                del self.rec
                return
            else:
                self.DataReady.emit(self.rec)
                del self.rec
            print("end")
        return

    def KillSelf(self):
        self.running = False
        #print("Terminated")
