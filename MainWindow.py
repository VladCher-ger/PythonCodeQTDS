from PyQt5 import QtCore, QtGui,Qt
import pyqtgraph as pg
import time as sleeptime
import sys
import numpy as np
import csv
import datetime
import os
from multiprocessing import Process
from scipy.signal import find_peaks
from scipy.fftpack import fft
from scipy.signal import windows
from tkinter import filedialog

import Main
import SearchForDelay
import CoraEth
import CoraEth_Thorlabs
import ThorLabsCntrl
import OzODL
import CsvMassRead
import FileHandle

from shutil import copyfile

import gc


class MainApplication(QtGui.QMainWindow, Main.Ui_MainWindow ):


    def __init__(self, parent=None):
        super(MainApplication, self).__init__(parent)

        FileHandle.initconfig()



                                                        # Verbindet Hauptprogramm mit GUI
        self.setupUi(self)

                                                        # Erzeugt das Erste Grahpenelement
        self.lifeGraph = pg.PlotWidget()
        self.GraphHolder.addWidget(self.lifeGraph)

                                                         #Erzeugt das Zweiter Graphenelement
        self.storeGraph = pg.PlotWidget()
        self.GraphHolder.addWidget(self.storeGraph)

                                                         #Verbindung der Toolbaroptionen mit Actionen und Shortcuts
        self.actionExit.setShortcut("Ctrl+E")
                                                        #Schließen des Programms
        self.actionExit.triggered.connect(self.Close)

                                                        #Bereitstellen der Postcalculationfunktionen
        self.PostCalc = CsvMassRead.PostCalculation()

                                                        #Toolbaractionen mit Funktionsverbindungen
        self.actionLoad_Graph.triggered.connect(self.PostCalc.LoadPLot)
        self.actionMake_AVG.triggered.connect(self.PostCalc.MakeAvg)

        #MakeFFT bleibt immer gleich, übergibt eine Fensterfunktion nach Auaswahl an die FFT
        self.actionBlackman.triggered.connect(lambda: self.PostCalc.MakeFFT(windows.blackman))
        self.actionHann.triggered.connect(lambda: self.PostCalc.MakeFFT(windows.hann))
        self.actionHanning.triggered.connect(lambda: self.PostCalc.MakeFFT(windows.hanning))
        self.actionNone.triggered.connect(lambda: self.PostCalc.MakeFFT(None))

        #Zurechtschneiden der Zeitaufnahme für FFT berechnungnen ohne Fenster
        self.actionFull.triggered.connect(lambda: self.PostCalc.ZeroFit(False))
        #self.actionSmall.triggered.connect(lambda: self.PostCalc.ZeroFit(True))
        self.actionSmall.triggered.connect( self.PostCalc.SelfAvarage)

        #Berechnung der Mittleren Peakpositionen
        self.actionFind_Peaks.triggered.connect(self.PostCalc.findPeakPos)

        #Berechnung des Brechungsindex, oder der Dicke. Benötigt zwei Dateien mit den Mittleren Peakpositionen.
        self.CalcRefrect = CsvMassRead.CalcRefrect()

        #Je nach benötigter Information, wird nach der dicke der Probe oder dem Brechungsindex gefragt
        self.actionCalc_refrectiv.triggered.connect(lambda: self.CalcRefrect.LoadFiles(True))
        self.actionCalc_thikness.triggered.connect(lambda: self.CalcRefrect.LoadFiles(False))

        self.actionCalc_Absorbtion.triggered.connect(self.CalcRefrect.ClacAbsorbtion)

        self.SearchDelayB.clicked.connect(self.SearchDelay)
        self.DelayLine = None
        self.ConnectCoraB.clicked.connect(self.ConnectToCora)




    #Alte Funktion, wir nur noch für Thorlabsdelayline Verwendet. Funktioniert Wahschienlich mit diesem Skript nicht mehr
    def SearchDelay(self):
        searcher = SearchForDelay.DelayLineInit()
        
        self.DelayLine = searcher.SearchForThorLabs(SN=int(self.ThorSN.text()))
        
        if self.DelayLine == None:
            self.LogBox.setPlainText("KBD101 not connected\n"+self.LogBox.toPlainText())
        elif self.DelayLine == searcher.ThorLabs:
            self.LogBox.setPlainText("KBD101 found\n"+self.LogBox.toPlainText())
            self.DelayT.setText("KBD101")
            self.SetUpThorlabsSignals()
            #FileHandle.updatecnfg(attribute='Number', value=2)

    #Verbinden der Funktionen und Actionenen mit Thorlabscontrolle
    def SetUpThorlabsSignals(self):
        self.MotorCntrl = ThorLabsCntrl.MotorCntrl(self.DelayLine)
        self.MotorCntrl.MotorThread.StartAcquisition.connect(self.StartMeas)
        self.MotorCntrl.MotorThread.StopAcquisition.connect(self.StopMeas)
        self.actionThorlabs.triggered.connect(self.MotorCntrl.showself)
        self.actionThorlabs.setShortcut("Ctrl+M")
        FileHandle.updatecnfg(attribute='Number', value=2)


    #Stellt ein Eth verbindung mit dem Board her. Übergibt Dabei Portnummer und MAC-Addresse aus GUI
    def ConnectToCora(self):
        # Erstellen der Ethernetcomm Klasse zur Kommunikation mit dem Armprozessor
        if self.DelayLine == None:
            self.EthDevice = CoraEth.CoraZ7Eth()
            #Remote Start der messung
            self.RunMeas.clicked.connect(self.StartRun)
            FileHandle.updatecnfg(attribute='Number', value=1)
            FileHandle.updatecnfg(attribute='speed', value=30)
            #Erzeugung eines Threads zum zeitlichen Buffern zwischen Messungen
            self.TimerThread = TimerThread()
            #Automatisches Startet einer neuen Messung, wenn die ANzahl an gewünschten Messungen noch nicht Erfolgt ist
            self.TimerThread.Emit.connect(self.EthDevice.StartAcquisition)
        else:
            self.EthDevice = CoraEth_Thorlabs.CoraZ7Eth()
            #Remote Start der messung
            self.RunMeas.clicked.connect(self.StartRun)

            #Erzeugung eines Threads zum zeitlichen Buffern zwischen Messungen
            self.TimerThread = TimerThread()
            #Automatisches Startet einer neuen Messung, wenn die ANzahl an gewünschten Messungen noch nicht Erfolgt ist
            self.TimerThread.Emit.connect(self.MotorCntrl.StartRun)

        connect = self.EthDevice.Connect(self.IPT.text(), int(self.PORTT.text()))
        self.LogBox.setPlainText(connect)
        if "Connected" in connect:
            self.EthDevice.EthThread.DataReady.connect(self.UpdateGraph)
            self.EthDevice.EthThread.Error.connect(self.printLogError)

    #Logbox für Statusanzeige und Feebacks
    def printLogError(self, Error):
        self.LogBox.setPlainText(Error +" on " +str(self.NumberOfRuns) +"\n" + self.LogBox.toPlainText())

    #Beginn der 1. Messung. Fragt die Anzahl der Messungen ab, resetet alle Graphen und Prüft nach Speicherbedarf der Messung
    def StartRun(self):
        gc.collect()
        self.NumberOfRuns = int(self.NRunsT.text())
        self.progressBar.setMaximum(self.NumberOfRuns)
        self.progressBar.setValue(0)
        self.storeGraph.clear()
        #Wenn die Messung nicht Gespeichert wird, oder nur 1 mal Stattfindet, kann eine lifefft im 2. Grahpen angezeigt werden
        if self.NumberOfRuns == 1:
            self.lifefft = True
        else:
            self.lifefft = False

        try:
            #Speicher Dialog für die Messung. Erstellt einen Ordner mit dem Eingegebenen Namen und fügt einen Zeitstempel hinzu.
            if self.StoreMeas.isChecked():
                now = datetime.datetime.now()
                self.path = filedialog.asksaveasfilename()
                self.folder =self.path + now.strftime("_%b_%d_%Y_%H_%M_%S")
                os.mkdir(self.folder)


                copyfile('.\cnfg.txt', self.folder+'\cnfg.txt')
                copyfile('.\Resolution.txt', self.folder + '\Resolution.txt')



            #gibt den Befehl an das Board zum Straten einer Messung
            #Dabei wird ein Thread erstellt, der alle n ms die Daten abfragt.
            #Ist die Messung Worbei wird ein 'Done' in den Daten mitgeschickt.
            #Der Thread beendet die Übertragung und gibt die gespeicherten Daten zur weiterverarbeitung an UpdateGraph weiter
            if self.DelayLine == None:
                self.EthDevice.StartAcquisition()
            else:
                self.MotorCntrl.StartRun()
        except:
            None

    def StartMeas(self):
        err = self.EthDevice.StartAcquisition()
        self.LogBox.setPlainText(err)

    def StopMeas(self):
        self.EthDevice.EthThread.KillSelf()

    def UpdateGraph(self, RawData):

        self.const = FileHandle.getResolution()
        #self.const =0.00325*4
        print(self.const)
        self.lifeGraph.clear()
        try:
            if self.lifefft == False and self.StoreMeas.isChecked():
                self.storeGraph.addItem(self.curve)
            else:
                self.storeGraph.clear()
        except:
            None
        self.Data = []
        self.time = []
        self.curve = self.lifeGraph.getPlotItem().plot()

        #Sortiert die Rohdaten nach nach Order und Wandelt aus dem macht aus dem 12 bit zweierkomplement ein 16 Bit zweierkomplement
        if len(RawData) > 50:
            # Wählt nach den Einstellungen aus, ob life FFt oder nicht

            for i in range(0, len(RawData)-1,2):
                self.Data.append(int.from_bytes((RawData[i],(0xf0 ^ RawData[i+1]) if 0x08 & RawData[i+1] else RawData[i+1] ),byteorder='little',signed=True))

            #Normierung auf ADC-Auflösung und Spannungsteilerverhältnis von 3.3
            self.Data = np.true_divide(self.Data, (4096/3.3))
            #Erstellen einer Zeitachse aus Equidistanten Messpunkten
            self.time = np.arange(0, len(self.Data), 1)*self.const
            #Abbilden der Kurve
            self.curve.setData(self.time, self.Data)

            #Speichern, oder nicht
            if self.StoreMeas.isChecked():
                CSVProcess(self.Data, self.folder, self.progressBar.value())

            #Life FFT oder nicht
            if self.lifefft or not self.StoreMeas.isChecked():
                window = windows.blackman(len(self.Data))
                my_fft = fft(self.Data*window)
                freq = np.linspace(0.0, 1.0/(2.0*self.const*1e-12), len(self.Data)//2)
                my_fft = np.abs(my_fft/len(self.Data))
                my_fft = 2*my_fft[1:len(self.Data)//2+1]
                my_fft = 20*np.log10(my_fft)
                freqmask = freq > 7e12
                noicemean = np.mean(my_fft[freqmask])

                freqmask = freq <5e12

                dataitem = self.storeGraph.getPlotItem().plot()

                dataitem.setData(freq[freqmask] ,my_fft[freqmask])
        else:
            self.NumberOfRuns = self.NumberOfRuns + 1
        print('Updategraph')
        #Wiederhohlen der Messung und Updaten des Messfortschrittbalkens
        if(self.NumberOfRuns>1):

            self.NumberOfRuns = self.NumberOfRuns - 1
            self.progressBar.setValue(self.progressBar.maximum()-self.NumberOfRuns)

            if self.NumberOfRuns%20 == 0:
                self.storeGraph.clear()
            RawData.clear()
            gc.collect()

            self.TimerThread.start()


        else:
            self.progressBar.setValue(self.progressBar.maximum())
            self.LogBox.setPlainText("Finished")

    #Schließt alle offenen Threads bevor das Programm beendet
    def Close(self):
        try:
            self.PostCalc.root.destroy()
        except:
            None
        try:
            self.DelayLine.close()
        except:
            None
        try:
            CoraEth.EthThread.KillSelf()
        except:
            None
        try:
            CoraEth_Thorlabs.EthThread.KillSelf()
        except:
            None
        self.close()
        try:
            self.MotorCntrl.close()
            self.MotorCntrl.Motor.move_home(False)
        except:
            None


class TimerThread(QtCore.QThread):

    Emit = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(TimerThread, self).__init__()

    def run(self):
        sleeptime.sleep(0.2)
        self.Emit.emit()


#Speichern der Daten in zuvor Erstellten Ordner mit Vortlaufender Nummerierung
def CSVProcess( data, folder, number):

    a = np.asarray(data)
    np.savetxt(folder+"/"+str(number)+".csv" ,a ,fmt="%f" ,delimiter=";")

    del data
    del folder
    del number
    return




if __name__ == '__main__':


    app = QtCore.QCoreApplication.instance()
    if app is None:
       app = QtGui.QApplication(sys.argv)
    window = MainApplication()
    window.show()
    app.exec_()
