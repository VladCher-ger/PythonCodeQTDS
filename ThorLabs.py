# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Cherniak\Desktop\QTDSoZThor\venv\ThorLabs.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(333, 282)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.VelT = QtWidgets.QLineEdit(self.centralwidget)
        self.VelT.setObjectName("VelT")
        self.verticalLayout.addWidget(self.VelT)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.AccelT = QtWidgets.QLineEdit(self.centralwidget)
        self.AccelT.setObjectName("AccelT")
        self.verticalLayout.addWidget(self.AccelT)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.HVelT = QtWidgets.QLineEdit(self.centralwidget)
        self.HVelT.setObjectName("HVelT")
        self.verticalLayout.addWidget(self.HVelT)
        self.ApplyB = QtWidgets.QPushButton(self.centralwidget)
        self.ApplyB.setObjectName("ApplyB")
        self.verticalLayout.addWidget(self.ApplyB)
        self.HomeB = QtWidgets.QPushButton(self.centralwidget)
        self.HomeB.setObjectName("HomeB")
        self.verticalLayout.addWidget(self.HomeB)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 333, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Velocity in mm/s"))
        self.VelT.setText(_translate("MainWindow", "160"))
        self.label_2.setText(_translate("MainWindow", "Acceleration in mm/s^2"))
        self.AccelT.setText(_translate("MainWindow", "2000"))
        self.label_3.setText(_translate("MainWindow", "Velocity in mm/s"))
        self.HVelT.setText(_translate("MainWindow", "120"))
        self.ApplyB.setText(_translate("MainWindow", "Apply"))
        self.HomeB.setText(_translate("MainWindow", "Home"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
