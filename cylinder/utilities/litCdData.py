import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt

# Get the path to the experimental data
scriptpath  = os.path.abspath(os.path.dirname(__file__))
datapath    = os.path.abspath(os.path.join(scriptpath,'..', 'Data'))

expcases     = ['achenbach1968','jones1969', 'shihsmooth1993']
expfilenames = ['Achenbach1968.csv','Jones1969.csv', 'ShihSmooth1993.csv']
explabels    = ['Achenbach 1968','Jones 1969','Shih: Smooth 1993']
expdata      = {}
for i,e in enumerate(expcases):
    expdata[e] = np.genfromtxt(os.path.join(datapath,expfilenames[i]),
                               delimiter=',',names=True)

cfdcases     = ['catalano_urans2003',
                'catalano_les2003',
                'lo_des2005',
                'travin_des1999',
                'porteus_urans2015',
                'squires2008']
cfdfilenames = ['CatalanoURANS2003.csv',
                'CatalanoLES2003.csv',
                'LoDES2005.csv',
                'TravinDES1999.csv',
                'PorteusURANS2015.csv',
                'Squires2008.csv']
cfdlabels    = ['Catalano URANS 2003',
                'Catalano LES 2003',
                'Lo DES 2005',
                'Travin DES 1999',
                'Porteus URANS 2015',
                'Squires DDES 2008']
cfddata = {}
for i,e in enumerate(cfdcases):
    cfddata[e] = np.genfromtxt(os.path.join(datapath,cfdfilenames[i]),
                               delimiter=',',names=True)

def plotEXP():
    for i,e in enumerate(expdata):
        plt.semilogx(expdata[e]['Reynolds_number'], expdata[e]['Cd'], 
                     label=explabels[i])

def plotCFD():
    markers = list(matplotlib.lines.Line2D.markers.keys())
    for i,c in enumerate(cfddata):
        plt.semilogx(cfddata[c]['Reynolds_number'], cfddata[c]['Cd'],
                     linestyle='',marker=markers[i],label=cfdlabels[i])

