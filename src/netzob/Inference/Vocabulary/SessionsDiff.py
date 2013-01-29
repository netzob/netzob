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
import re

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.Format import Format
from netzob.Common.Functions.Visualization.BackgroundColorFunction import BackgroundColorFunction

class SessionsDiff(object):
    """
    SessionsDiff:
    Provides inference functions for sessions
    """

    def __init__(self, project, sessions):
        """
        Constructor:
        @param project : the project where the search will be executed
        @param project : the sessions of which inference will be processed
        """
        self.project = project
        self.sessions = sessions
        self.results = []

    def getResults(self):
        return self.results

    def execute(self):
        self.results = []
        if len(self.sessions) <= 1:
            return

        # Compare, for each session, message by message
        # and build a common session model
        commonSessionModel = []
        for iMsg in range(len(self.sessions[0].getMessages())):
            refMessage = self.sessions[0].getMessages()[iMsg]
            cellsPerSession = {}
            refCells = refMessage.applyAlignment(styled=False, encoded=False)

            # Pre-compute splitted cells for each iMsg of each session
            for iSession in range(len(self.sessions[1:])):
                targetSession = self.sessions[iSession + 1]
                if iMsg >= len(targetSession.getMessages()):
                    continue
                targetMessage = targetSession.getMessages()[iMsg]
                targetCells = targetMessage.applyAlignment(styled=False, encoded=False)
                cellsPerSession[iSession] = targetCells

            # Compare cells by cells
            commonSplittedMessage = []
            for iCell in range(len(refCells)):
                commonCell = ""

                # Compare, in each cell, character by character
                for iCar in range(len(refCells[iCell])):
                    isSimilar = True
                    for iSession in range(len(self.sessions[1:])):
                        if iCell >= len(cellsPerSession[iSession]):
                            isSimilar = False
                            commonCell += ""
                            break
                        if iCar >= len(cellsPerSession[iSession][iCell]):
                            isSimilar = False
                            commonCell += ""
                            break
                        if refCells[iCell][iCar] != cellsPerSession[iSession][iCell][iCar]:
                            isSimilar = False
                            commonCell += "-"
                            break
                    if isSimilar:
                        commonCell += refCells[iCell][iCar]
                commonSplittedMessage.append(commonCell)
            commonSessionModel.append(commonSplittedMessage)


        # Colorize each session according to the common model
        for session in self.sessions:
            for iMsg in range(len(session.getMessages())):
                message = session.getMessages()[iMsg]
                cells = message.applyAlignment(styled=False, encoded=False)
                resMsg = []
                for iCell in range(len(cells)):
                    cell = cells[iCell]
                    resCell = ""
                    for iCar in range(len(cell)):
                        if iMsg < len(commonSessionModel):
                            if iCell < len(commonSessionModel[iMsg]):
                                if iCar < len(commonSessionModel[iMsg][iCell]):
                                    resCell += commonSessionModel[iMsg][iCell][iCar]
                                else:
                                    resCell += "-"
                            else:
                                resCell += "-"
                        else:
                            resCell += "-"
                    resMsg.append(resCell)

                # Compute the non matching segments, at the message level (i.e. we merge all the fields first)
                data = "".join(resMsg)
                nonMatchingSegments = [(m.start(), str(m.end())) for m in re.finditer("-+", data)]

                # Add, as a result, a tupple containing the current message and the non-matching segments
                if len(nonMatchingSegments) > 0:
                    self.results.append((message, nonMatchingSegments))

    def colorizeResults(self):
        for (message, nonMatchingSegments) in self.getResults():
            for (start, end) in nonMatchingSegments:
                function = BackgroundColorFunction("Search", "#DD8888")
                message.addVisualizationFunction(function, start, end)
