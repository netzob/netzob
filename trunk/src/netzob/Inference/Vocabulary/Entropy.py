# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
from pylab import figure, show

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Entropy :
#|     Class for calculating and viewing entropy information
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Entropy(object):
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, group):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Entropy.py')
        self.group = group

    #+---------------------------------------------- 
    #| buildDistributionView :
    #|   show messages distribution
    #+----------------------------------------------    
    def buildDistributionView(self):
        resX = []
        resY = []
        segments = []
        i = 0
        for iCol in range(len(self.group.getColumns())):
            maxCell = -1
            for cell in self.group.getCellsByCol(iCol):
                for j in range(len(cell) / 2):
                    resX.append(i + j)
                    resY.append(int(cell[j * 2:j * 2 + 2], 16))
                if len(cell) / 2 > maxCell:
                    maxCell = len(cell) / 2
            i += maxCell
            segments.append(i)

        fig = figure()#figsize=(800, 500))#, dpi=75)
        axis = fig.add_subplot(111, frame_on=False)
        axis.hold(True)
        axis.plot(resX, resY, '.')
        for segment in segments:
            axis.plot([segment, segment], [0, 255], 'k-')
        axis.set_xlim(0, 255)
        axis.set_ylim(0, 255)
        show()
