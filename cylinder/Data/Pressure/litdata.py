import matplotlib, pickle
import matplotlib.pyplot as plt

import numpy as np

		

expcases = ['achenbach1968','Roshko1961', 'VanNunen1970']
expfilenames = ['Achenbach1965_Re3p6M.csv','Roshko1961_Re8p5M.csv','VanNunen1970_Re8M.csv']
explabels = ['Achenbach 1968 - Re=3.6M','Roshko 1961 - Re=8.5M','Van Nunen 1970 - Re=7.6M']
expdata = {}
for i,e in enumerate(expcases):
    expdata[e] = np.genfromtxt(expfilenames[i],delimiter=',',names=True)

cfdcases = ['porteusurans2015','squirescoarseddes2008','squiresfineddes2008']
cfdfilenames = ['PorteusURANS2015_Re3p6M.csv','Squires2008CoarseDDES_8M.csv','Squires2008FineDDES_8M.csv']
cfdlabels = ['Porteus URANS - Re = 3.6M','Squires DDES Coarse - Re = 8M','Squires DDES Fine - Re = 8M']
cfddata = {}
for i,e in enumerate(cfdcases):
    cfddata[e] = np.genfromtxt(cfdfilenames[i],delimiter=',',names=True)

with open('lit_data.pkl','wb') as f:
    pickle.dump([expcases,expdata,explabels,cfdcases,cfddata,cfdlabels],f)

if __name__=="__main__":
    markers = list(matplotlib.lines.Line2D.markers.keys())
    fig = plt.figure()
    for i,e in enumerate(expdata):
        plt.plot(expdata[e]['Theta'],expdata[e]['Cp'],label=explabels[i])
    for i,c in enumerate(cfddata):
        plt.plot(cfddata[c]['Theta'],cfddata[c]['Cp'],linestyle='',marker=markers[i],label=cfdlabels[i])
    plt.xlabel(r'$\theta$')
    plt.ylabel(r'$C_p$')
    plt.legend(loc=0)
    plt.grid()
    plt.savefig('CpLitData.pdf')
    plt.show()

