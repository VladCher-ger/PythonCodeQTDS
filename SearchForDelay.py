import serial


class DelayLineInit():
    def __init__(self, parent = None):
        super(DelayLineInit, self).__init__()
        self.ser = None
        self.ThorLabs = None
    def SearchForOzODL(self):


        ser = serial.Serial()
        ser.baudrate = 9600
        ser.timeout = 1
        ser.buffersize = 1024
        Port=['COM1','COM2','COM3',
                   'COM4','COM5','COM6',
                   'COM7','COM8','COM9',
                   'COM10','COM11','COM12',
                   'COM13','COM14','COM15',
                   'COM16','COM17','COM18']

        for i in range(len(Port)):
            try:
                ser.port = Port[i]
                ser.open()
                ser.write("Echo\n".encode())
                echo = ser.readline()
                if "Echo" in echo.decode("utf-8"):
                    self.ser = ser
                    return ser
                else:
                    ser.close
            except:
                None
        return None

    def SearchForThorLabs(self, SN):

        import thorlabs_apt as apt

        try:
            self.ThorLabs = apt.Motor(SN)

            return self.ThorLabs
        except:
            self.ThorLabs = None


