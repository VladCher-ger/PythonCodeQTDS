import tkinter as tk
from tkinter import filedialog
from os import walk
import csv
import numpy as np
from scipy.signal import find_peaks, hanning
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from PyQt5 import  QtGui, Qt, QtCore, QtWidgets
import time as sleeptime
import gc

import FileHandle


import ProBar, Dialog

class CalcRefrect(QtWidgets.QDialog, Dialog.Ui_Dialog):
    def __init__(self):
        super(CalcRefrect,self).__init__()
        self.setupUi(self)


        self.rejected.connect(self.close)

    def LoadFiles(self,Refrect = True):

        self.Refrect = Refrect



        file1 = filedialog.askopenfilename()
        file2 = filedialog.askopenfilename()

        folder = file1.split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        times1 = []
        with open(file1) as csv_reader:
             reader = csv.reader(csv_reader, delimiter=';')

             for row in reader:
                 times1.append(float(row[0]))

        times2 = []
        with open(file2) as csv_reader:
             reader = csv.reader(csv_reader, delimiter=';')

             for row in reader:
                 times2.append(float(row[0]))

        minlenght = len(times1) if len(times1) < len(times2) else len(times2)

        diffvect = np.subtract(times1[0:minlenght], times2[0:minlenght])

        diffvect = np.asarray(diffvect)

        avgdiff = np.average(diffvect)

        self.resultavgdiff = abs(avgdiff)
        print(self.resultavgdiff)

        if Refrect:
            self.label.setText("Instert d / mm")
        else:
            self.label.setText("Inster n")

        self.accepted.connect(self.Calc)
        self.show()

    def ClacAbsorbtion(self):

        file_path = filedialog.askopenfilename()

        folder = file_path.split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        f = []
        val = []



        try:
            with open(file_path) as csv_file:
                reader = csv.reader(csv_file, delimiter=';')

                for row in reader:
                    f.append(float(row[0]))
                    val.append(float(row[1]))
        except:
            print("error 1")
            return

        f2 = []
        val2 = []
        file_path = filedialog.askopenfilename()
        try:
            with open(file_path) as csv_file:
                reader = csv.reader(csv_file, delimiter=';')

                for row in reader:
                    f2.append(float(row[0]))
                    val2.append(float(row[1]))
        except:
            print("error 2")
            return


        self.f = np.asarray(f)
        val = np.asarray(val)
        f2 = np.asarray(f2)
        val2 = np.asarray(val2)

        fmask = self.f < 3e12
        f2mask = f2 <3e12

        self.peaks,_ = find_peaks(val[fmask], distance=43e9/self.f[1])

        self.peaks2,_ = find_peaks(val2[f2mask], distance=43e9/f2[1])

        mean1 = np.mean(val[self.peaks[1:35]])
        mean2 = np.mean(val2[self.peaks2[1:35]])

        if mean1 >= mean2:
            None
        else:
            self.f, val ,f2, val2 = f2, val2, self.f, val

            self.peaks, self.peaks2 = self.peaks2, self.peaks
        plt.figure(figsize=(20,25))
        self.gs = plt.GridSpec(2,2)
        plt.subplot(self.gs[0,0])
        plt.plot( self.f[fmask], val[fmask],  label = 'Referenz')
        plt.plot( f2[f2mask], val2[f2mask] ,label= 'Probe')
        plt.xlabel("f / THz")
        plt.ylabel(r"20Log(I$_{det}$3*10$^3 \frac{V}{A}$)")
        plt.legend()
        plt.grid()

        plt.subplot(self.gs[0,1])
        plt.plot(self.f[self.peaks], val[self.peaks],"x", label = 'Referenz')
        plt.plot( f2[self.peaks2], val2[self.peaks2],"o" , label = 'Probe')
        plt.xlabel("f / THz")
        plt.ylabel(r"20Log(I$_{det}$3*10$^3 \frac{V}{A}$)")
        plt.legend()
        plt.grid()

        self.absorb = val[self.peaks[0:35]] - val2[self.peaks2[0:35]]

        self.label.setText("Probe thickness in cm")

        self.accepted.connect(self.Calc2)
        self.show()

        return

    def Calc2(self):

        d =  float(self.lineEditValue.text())
        alpha = np.true_divide(self.absorb, 10*np.log10(np.e)*d)

        plt.subplot(self.gs[1,:])
        plt.plot(self.f[self.peaks[0:35]], alpha, '--', Marker = 'x')
        plt.xlabel("f / THz")
        plt.ylabel("Absorbtion / $cm^{-1}$")
        plt.grid()

        try:
            a = np.transpose([self.f[self.peaks[0:35]], alpha])
            savefile = filedialog.asksaveasfile(mode='w',defaultextension=".csv")
            np.savetxt(savefile, a , delimiter=";")
        except:
            print("Error")
            None

        plt.show()


    def Calc(self):

        input = float(self.lineEditValue.text())

        if self.Refrect:
            result = self.resultavgdiff * 1e-12 * 299792458 / (input * 1e-3) + 1
        else:
            result = self.resultavgdiff * 1e-12 * 299792458 / (1 - input)

        print(result)

class PostCalculation(QtGui.QWidget,ProBar.Ui_Probar):

    def __init__(self, parent = None):
        super(PostCalculation, self).__init__()

        self.root = tk.Tk()
        self.root.withdraw()
        self.setupUi(self)


    def MakeAvg(self, printer):



        file_path = filedialog.askopenfilenames()

        folder = file_path[0].split('/')

        path = ''
        for i in range(0,len(folder)-1):
            path = path + folder[i]+"/"
        path = path +'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        cutval = []

        self.LoadCsvBar.setMaximum(len(file_path))
        self.show()
        for numb,i in enumerate(file_path):
            val = []
            self.LoadCsvBar.setValue(numb+1)
            QtGui.QGuiApplication.processEvents()
            try:
                with open(i) as csv_file:
                    reader = csv.reader(csv_file, delimiter=';')

                    for row in reader:
                       if len(row) == 1:
                            val.append(float(row[0]))
                       else:
                           val.append(float(row[1]))
            except:

                break
                self.close()
                return

            valarray = np.asarray(val)

            maxval = np.max(valarray)

            peaks,_ = find_peaks(valarray, height=(maxval*0.6, maxval), distance=20/self.deltaT)

            distance = peaks[1:-1]-peaks[0:-1-1]

            try:
                if np.min(distance)*self.deltaT< 18 or np.max(distance)*self.deltaT >28:

                    continue
            except:
                continue

            if(min(peaks)<20):

                continue

            valarray = valarray[peaks[0]-20:-1]

            cutval.append(valarray)
        #############################################
        #self.close()
        plt.subplot(2,1,1)
        plt.grid(which ='both',axis='both')
        print("/////////////////")
        length = []

        for i in cutval:
            length.append(len(i))
        try:
            minlength = np.min(length)
        except:
            self.close()
            return
        Timeaxis = np.arange(0, minlength, 1)*self.deltaT


        timemask = Timeaxis<210
        Timeaxis = Timeaxis[timemask]
        avg = np.zeros(len(Timeaxis))

        for number,i in enumerate(cutval):
            cutval[number] = i[0:minlength]
            cutval[number] = cutval[number][timemask]
            avg = avg + cutval[number]
            plt.plot(Timeaxis, cutval[number])

        avg = np.true_divide(avg, len(cutval))
        print(len(cutval))
        ###################################################################################
        plt.subplot(2,1,2)
        plt.plot(Timeaxis, avg)
        plt.grid(which ='both',axis='both')

        self.close()
        try:
            savefile = filedialog.asksaveasfile(mode='w',defaultextension=".csv")
            np.savetxt(savefile, avg , delimiter=";")
        except:
            None
        plt.show()

    def ZeroFit(self, small = False):



        avg = []

        file_path = filedialog.askopenfilename()

        folder = file_path[0].split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        try:
            with open(file_path) as csv_file:
                reader = csv.reader(csv_file, delimiter=';')

                for row in reader:
                   if len(row) == 1:
                        avg.append(float(row[0]))
                   else:
                       avg.append(float(row[1]))
        except:
            return

        avg = np.asarray(avg)
        Timeaxis = np.arange(0 ,len(avg) ,1)*self.deltaT
        maxval = max(avg)
        peaks,_ = find_peaks(avg, height=(maxval*0.8, maxval), distance=200)

        firstzero = np.where(np.diff(np.sign(avg[peaks[1]:peaks[1]+300])))[0]

        if small:
            secondzero = np.where(np.diff(np.sign(avg[peaks[2]:peaks[2]+300])))[0]
            avg_window = avg[peaks[1]+firstzero[0]: peaks[2]+secondzero[0]]
            Timeaxis_window = np.arange(0 ,len(avg_window) ,1)*self.deltaT
        else:
            lastzero =  np.where(np.diff(np.sign(avg[peaks[-2]:peaks[-2]+300])))[0]
            avg_window = avg[peaks[1]+firstzero[0]: peaks[-2]+lastzero[0]]
            Timeaxis_window = np.arange(0 ,len(avg_window) ,1)*self.deltaT

        try:
            savefile = filedialog.asksaveasfile(mode='w',defaultextension=".csv")
            np.savetxt(savefile, avg_window , delimiter=";")
        except:
            None

        plt.plot(Timeaxis_window, avg_window, Timeaxis_window[-1]+Timeaxis_window, avg_window)
        plt.show()

    def MakeFFT(self, window = None):

        avg = []

        file_path = filedialog.askopenfilename()

        folder = file_path.split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        try:
            with open(file_path) as csv_file:
                reader = csv.reader(csv_file, delimiter=';')

                for row in reader:
                   if len(row) == 1:
                        avg.append(float(row[0]))
                   else:
                       avg.append(float(row[1]))
        except:
            return


        avg = np.asarray(avg)
        Timeaxis = np.arange(0 ,len(avg) ,1)*self.deltaT

        plt.subplot(2,1,1)
        plt.plot(Timeaxis, avg)

        if window == None:
            my_fft = fft(avg)
        else:
            my_fft = fft(avg*window(len(avg)))

        freq = np.linspace(0.0, 1.0/(2.0*self.deltaT*1e-12), len(avg)//2)

        my_fft = np.abs(my_fft/len(avg))
        my_fft = 2*my_fft[1:len(avg)//2+1]
        my_fft = 20*np.log10(my_fft)
        freqmask = freq > 7e12
        noicemean = np.mean(my_fft[freqmask])

        ########################################################
        plt.subplot(2,1,2)
        plt.xlim([0, 8e12])
        plt.xticks(np.arange(min(freq), max(freq)+1, 0.5e12))
        plt.xlim([0, 7e12])
        plt.grid(which ='both',axis='both')
        amp = my_fft #- noicemean#- max(my_fft)

        print(freq[amp >= np.max(amp)])

        plt.plot(freq, amp)

        a = np.transpose([freq, amp])
        try:
            savefile = filedialog.asksaveasfile(mode='w',defaultextension=".csv")
            np.savetxt(savefile, a , delimiter=";")
        except:
            None

        plt.show()

    def findPeakPos(self):



        file_path = filedialog.askopenfilenames()

        folder = file_path[0].split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        self.LoadCsvBar.setMaximum(len(file_path))
        self.show()
        avg_peak=[]
        minlength = 0
        for numb,i in enumerate(file_path):
            val = []
            self.LoadCsvBar.setValue(numb+1)
            QtGui.QGuiApplication.processEvents()
            try:
                with open(i) as csv_file:
                    reader = csv.reader(csv_file, delimiter=';')

                    for row in reader:
                       if len(row) == 1:
                            val.append(float(row[0]))
                       else:
                           val.append(float(row[1]))
            except:
                break
                self.close()
                return

            valarray = np.asarray(val)

            maxval = np.max(valarray)

            peaks,_ = find_peaks(valarray, height=(maxval*0.8, maxval), distance=200)

            if minlength == 0 or minlength > len(peaks):
                minlength = len(peaks)

            avg_peak.append(peaks)

        helparray = np.zeros(minlength)
        for i in avg_peak:
            helparray = helparray + i[0:minlength]

        helparray = helparray/len(file_path)*self.deltaT

        self.close()

        helparray = np.asarray(helparray)
        try:
            savefile = filedialog.asksaveasfile(mode='w',defaultextension=".csv")
            np.savetxt(savefile, helparray , delimiter=";")
        except:
            None

    def CalcN(self):
        w = QDialog()





    def LoadPLot(self):



        file_path = filedialog.askopenfilenames()

        folder = file_path[0].split('/')

        path = ''
        for i in range(0, len(folder) - 1):
            path = path + folder[i] + "/"
        path = path + 'Resolution.txt'

        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    category, value = line.strip().split(';')
                self.deltaT = float(value)
        except:
            self.deltaT = FileHandle.getResolution()

        self.LoadCsvBar.setMaximum(len(file_path))
        self.show()


        try:
            for numb,i in enumerate(file_path):
                avg = []
                Timearray = []
                oneax = True
                self.LoadCsvBar.setValue(numb+1)
                QtGui.QGuiApplication.processEvents()
                with open(i) as csv_file:
                    reader = csv.reader(csv_file, delimiter=';')

                    for row in reader:
                            if len(row) == 2:
                                Timearray.append(float(row[0]))
                                avg.append(float(row[1]))
                                oneax = False
                            else:
                                avg.append(float(row[0]))

                avgarray = np.asarray(avg)

                if oneax:
                    Timearray = np.arange(0,len(avgarray),1)*self.deltaT

                plt.plot(Timearray, avgarray)

                del Timearray
                del avgarray
                del avg
                gc.collect()


        except:
            self.close()
            return


        self.close()
        plt.grid()
        plt.show()
        plt.clf()
        plt.close()
        gc.collect()
        return



