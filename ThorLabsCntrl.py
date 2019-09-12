from PyQt5 import QtCore, QtGui, Qt
import ThorLabs

class MotorCntrl(QtGui.QMainWindow, ThorLabs.Ui_MainWindow):
    def __init__(self, Mototr, parent=None):
        super(MotorCntrl, self).__init__()
        self.Motor = Mototr
        self.Positions = [self.StartPos, self.StartMeasPos, self.StopMeasPos, self.EndPos]
        self.MotorThread = MotorCntrlThread(Motor=Mototr, Positions=self.Positions)
        self.setupUi(self)
        self.setVelocity()
        self.Motor.move_home(False)
        self.show()

        self.ApplyB.clicked.connect(self.setVelocity)
        self.HomeB.clicked.connect(self.Home)

        self.PositionSlide.sliderMoved.connect(self.Movestage)

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
        self.VelT.setText(str(VelParam[2]))
        self.AccelT.setText(str(VelParam[1]))
        self.HVelT.setText(str(self.Motor.move_home_velocity))

    def StartRun(self):
        self.MotorThread.setTerminationEnabled(True)
        self.MotorThread.start()

class MotorCntrlThread(QtCore.QThread):

    StartAcquisition = QtCore.pyqtSignal()
    StopAcquisition = QtCore.pyqtSignal()
    def __init__(self, Motor,Positions , parent = None):
        super(MotorCntrlThread,self).__init__()
        self.Motor = Motor
        self.Positions = Positions
    def run(self):
        self.Motor.move_to(self.Positions(float(self.Positions(0).text())),True)
        self.Motor.move_to(float(self.Positions(3).text()), False)

        while self.Motor.position <float(self.Positions(1).text()):
            None
        self.StartAcquisition.emit()
        while self.Motor.position <float(self.Positions(2).text()):
            None
        self.StopAcquisition.emit()
        self.msleep(5)
        return
