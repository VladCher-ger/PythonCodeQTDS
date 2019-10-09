# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Cherniak\Desktop\QTDSoZThor\venv\ProBar.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Probar(object):
    def setupUi(self, Probar):
        Probar.setObjectName("Probar")
        Probar.resize(270, 51)
        Probar.setWindowTitle("Loading AVG")
        self.verticalLayoutWidget = QtWidgets.QWidget(Probar)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 10, 251, 31))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LoadCsvBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.LoadCsvBar.setProperty("value", 24)
        self.LoadCsvBar.setObjectName("LoadCsvBar")
        self.verticalLayout.addWidget(self.LoadCsvBar)

        self.retranslateUi(Probar)
        QtCore.QMetaObject.connectSlotsByName(Probar)

    def retranslateUi(self, Probar):
        _translate = QtCore.QCoreApplication.translate
        Probar.setWindowTitle(_translate("Probar", "Form"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Probar = QtWidgets.QWidget()
    ui = Ui_Probar()
    ui.setupUi(Probar)
    Probar.show()
    sys.exit(app.exec_())
