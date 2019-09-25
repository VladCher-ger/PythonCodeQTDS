from PyQt5 import QtCore, QtGui, Qt
import ThorLabs
import FileHandle

class MotorCntrl(QtGui.QMainWindow, ThorLabs.Ui_MainWindow):
    def __init__(self, Mototr, parent=None):
        super(MotorCntrl, self).__init__()
        self.Motor = Mototr

        self.setupUi(self)
        self.setVelocity()
        self.Motor.move_home(False)

        self.Positions = [float(self.StartPos.text()), float(self.StartMeasPos.text()), float(self.StopMeasPos.text()),
                          float(self.EndPos.text())]

        self.MotorThread = MotorCntrlThread(Motor=Mototr, Positions=self.Positions)
        self.show()

        self.ApplyB.clicked.connect(self.setVelocity)
        self.HomeB.clicked.connect(self.Home)

        self.SetParam.clicked.connect(self.setparam)

        self.PositionSlide.sliderMoved.connect(self.Movestage)

    def setparam(self):

        self.Positions = [float(self.StartPos.text()), float(self.StartMeasPos.text()), float(self.StopMeasPos.text()),
                          float(self.EndPos.text())]

    def Movestage(self):

        self.Motor.move_to(self.PositionSlide.value())

    def showself(self):

        self.show()

    def Home(self):

        self.Motor.move_home(False)

    def setVelocity(self):

        self.Motor.set_velocity_parameters(1,float(self.AccelT.text()),float(self.VelT.text()))
        self.Motor.set_move_home_parameters(direction=self.Motor.move_home_direction,
                                            lim_switch=self.Motor.move_home_lim_switch,
                                            velocity=float(self.HVelT.text()),zero_offset=1)
        VelParam = self.Motor.get_velocity_parameters()
        self.VelT.setText(f"{VelParam[2]:.3f}")
        self.AccelT.setText(f"{VelParam[1]:.3f}")
        self.HVelT.setText(f"{self.Motor.move_home_velocity:.3f}")

        FileHandle.updatecnfg(attribute='speed', value=VelParam[2])


    def StartRun(self):
        self.MotorThread.setTerminationEnabled(True)
        while self.MotorThread.isRunning():
            None
        self.MotorThread.start()

class MotorCntrlThread(QtCore.QThread):

    StartAcquisition = QtCore.pyqtSignal()
    StopAcquisition = QtCore.pyqtSignal()
    def __init__(self, Motor, Positions, parent = None):

        super(MotorCntrlThread, self).__init__()
        self.Motor = Motor
        self.Positions = Positions

    def run(self):

        self.Motor.move_to(self.Positions(0), True)
        self.Motor.move_to(self.Positions(3), False)

        while self.Motor.position < self.Positions(1):
            None
        self.StartAcquisition.emit()
        while self.Motor.position < self.Positions(2):
            None
        self.StopAcquisition.emit()
        self.msleep(5)
        return
