# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
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
#+---------------------------------------------- 
class Entropy(object):
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, symbol):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Entropy.py')
        self.symbol = symbol

    #+---------------------------------------------- 
    #| buildDistributionView :
    #|   show messages distribution
    #+----------------------------------------------    
    def buildDistributionView(self):
        resX = []
        resY = []
        segments = []
        i = 0
        for field in self.symbol.getFields():
            maxCell = -1
            for cell in self.symbol.getMessagesValuesByField(field):
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
