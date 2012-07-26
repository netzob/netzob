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
from gettext import gettext as _
import logging
#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
import matplotlib.pyplot as plt
from pylab import figure, show
from random import randint
from matplotlib.widgets import Button


#+----------------------------------------------
#| MessagesDistributionView:
#|     Class for calculating and viewing messages distribution
#+----------------------------------------------
class MessagesDistributionView(object):
    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, symbolList):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Views.MessagesDistributionView.py')
        self.symbolList = symbolList

    def buildListDistributionView(self):
        symbolPointList = []
        symbolNameList = []
        segments = []
        #calculate the distribution for each symbol
        for symbol in self.symbolList:
            i = 0
            resX = []
            resY = []
            symbolNameList.append(symbol.getName())
            for field in symbol.getFields():
                maxCell = -1
                for cell in symbol.getUniqValuesByField(field):
                    for j in range(len(cell) / 2):
                        resX.append(i + j)
                        resY.append(int(cell[j * 2:j * 2 + 2], 16))
                    if len(cell) / 2 > maxCell:
                        maxCell = len(cell) / 2
                i += maxCell
            symbolPointList.append([resX, resY])
        segments.append(i)

        #create figure
        fig = figure("Message distribution of symbol : " + str(symbolNameList))
        fig.set_facecolor('w')

        #add calculate point on the figure
        pointObjectList = []
        for sym in symbolPointList:
            axis = fig.add_subplot(111, frame_on=False)
            (resX, resY) = sym
            p = axis.plot(resX, resY, '.', color=self.createColor())
            pointObjectList.append(p[0])

        #add legend
        axis.legend(pointObjectList , symbolNameList, 'upper right')
        axis.hold(True)

        #add reload color button
        reloadColor = plt.axes([0.74, 0.9, 0.15, 0.075])
        button = Button(reloadColor, 'Reload color')
        button.on_clicked(self.reloadColor_cb)
        self.axis = axis
        self.pointObjectList = pointObjectList
        self.symbolNameList = symbolNameList

        #create the vertical bar
        """for segment in segments:
            axis.plot([segment, segment], [0, max(resY) + 5], 'k-')"""

        #set the limit of the figure
        axis.set_xlim(0, max(resX) + 5)
        axis.set_ylim(0, max(resY) + 5)
        show()


    def reloadColor_cb(self, event):
        for point in self.pointObjectList:
            point.set_color(self.createColor())

        self.axis.legend(self.pointObjectList , self.symbolNameList, 'upper right')

    def createColor(self):
        return '#' + hex(randint(0, pow(255, 3))).lstrip('0x').zfill(6)
