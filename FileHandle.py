import os
from tkinter import filedialog
import numpy

def updatecnfg( attribute=None, value=0.0):
    f = open('cnfg.txt', 'r+')
    line = f.readlines()
    f.close()

    f = open('cnfg.txt', 'w+')
    if attribute == "speed":
        for i in line:
            if attribute in i:
                f.write('Stage speed [mm/s]; {:.4f}\n'.format(value))
            else:
                f.write(i)
    else:
        for i in line:
            if attribute in i:
                f.write(attribute + ';'+str(value)+'\n')
            else:
                f.write(i)
    f.close()

    with open('cnfg.txt', 'r') as f:
        for line in f.readlines():
            category, value = line.strip().split(";")

            if "RepRate" in category:
                repRate = float(value)

            elif "speed" in category:
                speed = float(value)

            elif "Number" in category:
                number = float(value)

            elif "Avarage" in category:
                avg = float(value)

    const = 2 * number * speed / (2.99792458 * 96154 / avg)

    with open("Resolution.txt", 'w+') as f:
        f.write("Resolution in ps; {:.6}".format(const))


def initconfig():
    if os.path.isfile('./cnfg.txt'):
        with open('cnfg.txt', 'r') as f:
            for line in f.readlines():
                category, value = line.strip().split(";")

                if "RepRate" in category:
                    repRate = float(value)

                elif "speed" in category:
                    speed = float(value)

                elif "Number" in category:
                    number = float(value)

                elif "Avarage" in category:
                    avg = float(value)

    else:

        with open('cnfg.txt', 'a+') as f:
            f.write('Laser RepRate [GHz]; 43.24\n')
            f.write('Stage speed [mm/s]; 120\n')
            f.write('Number of optical paths; 2\n')
            f.write('Running Avarage; 64\n')

        repRate = 43.47
        speed = 120
        number = 2
        avg = 64

    const = 2 * number * speed / (2.99792458 * 96154 / avg)

    with open("Resolution.txt", 'w+') as f:
        f.write("Resolution in ps; {:.6}".format(const))

def getResolution():

    with open("Resolution.txt", 'r') as f:
        for line in f.readlines():
            category, value = line.strip().split(';')
    return float(value)

def getAttribute(attribute=None):

    if os.path.isfile('./cnfg.txt'):
        with open('cnfg.txt', 'r') as f:
            for line in f.readlines():
                category, value = line.strip().split(";")

                if attribute in category:
                    return float(value)
    else:
        return 30

def SaveData( time, data, path=None):

    time = numpy.asarray(time)
    data = numpy.asarray(data)

    if path == None:
        try:
            savefile = filedialog.asksaveasfile(mode='w', defaultextension=".csv").name
        except:
            return
    else:
        savefile = path
        print(savefile)

    try:
        with open(savefile, "w+") as f:
           for t,val in zip(time,data):
               f.write(str(t)+";"+str(val)+"\n")
    except:
        None

