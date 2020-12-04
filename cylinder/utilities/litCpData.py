import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt


# Get the path to the experimental data
scriptpath  = os.path.abspath(os.path.dirname(__file__))
datapath    = os.path.abspath(os.path.join(scriptpath,'..', 'Data', 'Pressure'))

expcases     = ['achenbach1968',
                'Roshko1961', 
                'VanNunen1970']
expfilenames = ['Achenbach1965_Re3p6M.csv',
                'Roshko1961_Re8p5M.csv',
                'VanNunen1970_Re8M.csv']
explabels    = ['Achenbach 1968 - Re=3.6M',
                'Roshko 1961 - Re=8.5M',
                'Van Nunen 1970 - Re=7.6M']
expdata = {}
for i,e in enumerate(expcases):
    expdata[e] = np.genfromtxt(os.path.join(datapath, expfilenames[i]),
                               delimiter=',',names=True)

cfdcases     = ['porteusurans2015',
                'squirescoarseddes2008',
                'squiresfineddes2008']
cfdfilenames = ['PorteusURANS2015_Re3p6M.csv',
                'Squires2008CoarseDDES_8M.csv',
                'Squires2008FineDDES_8M.csv']
cfdlabels    = ['Porteus URANS - Re = 3.6M',
                'Squires DDES Coarse - Re = 8M',
                'Squires DDES Fine - Re = 8M']
cfddata = {}
for i,e in enumerate(cfdcases):
    cfddata[e] = np.genfromtxt(os.path.join(datapath,cfdfilenames[i]),
                               delimiter=',',names=True)

def plotEXP():
    for i,e in enumerate(expdata):
        plt.plot(expdata[e]['Theta'], expdata[e]['Cp'], label=explabels[i])

def plotCFD():
    markers = list(matplotlib.lines.Line2D.markers.keys())
    for i,c in enumerate(cfddata):
        plt.plot(cfddata[c]['Theta'], cfddata[c]['Cp'],  linestyle='',marker=markers[i],label=cfdlabels[i])

