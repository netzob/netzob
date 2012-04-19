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

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import threading

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| MMSTDVisitor:
#|     Definition of a visitor of an MMSTD automata
#+---------------------------------------------------------------------------+
class MMSTDVisitor(threading.Thread):

    def __init__(self, name, mmstd, isMaster, abstractionLayer):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.MMSTDVisitor.py')
        self.name = name
        self.model = mmstd
        self.isMaster = isMaster
        self.abstractionLayer = abstractionLayer
        self.active = False

    def run(self):
        if self.isMaster:
            self.log.debug("Starting the MMSTDVisitor as a Master")
        else:
            self.log.debug("Starting the MMSTDVisitor as a Client")
        self.active = True
        if self.isMaster:
            self.runAsMaster()
        else:
            self.runAsClient()
        self.log.debug("End of execution for the MMSTDVisitor")

    def stop(self):
        self.log.debug("Stops the MMSTDVisitor")
        self.abstractionLayer.disconnect()
        self.active = False

    def runAsMaster(self):
        self.log.debug("The MMSTD Visitor is running as a master")
        currentState = self.model.getInitialState()
        while self.active:
            currentState = currentState.executeAsMaster(self.abstractionLayer)
            if currentState == None:
                self.active = False
        self.log.debug("The MASTER stops !")

    def runAsClient(self):
        self.log.debug("The MMSTD Visitor is running as a client")

        currentState = self.model.getInitialState()
        while self.active:
            self.log.debug("Run as a client the state " + str(currentState.getName()))
            currentState = currentState.executeAsClient(self.abstractionLayer)
            if currentState == None:
                self.log.warn("The execution of the transition didn't provide the next state")
                self.active = False
        self.log.debug("The CLIENT stops !")

    def getInputMessages(self):
        return self.abstractionLayer.getInputMessages()

    def getOutputMessages(self):
        return self.abstractionLayer.getOutputMessages()

    def getMemory(self):
        return self.abstractionLayer.getMemory()

    def getAbstractionLayer(self):
        return self.abstractionLayer

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name

    def getModel(self):
        return self.model

    def isMaster(self):
        return self.isMaster

    def isActive(self):
        return self.active

    def setModel(self, model):
        self.model = model

    def setName(self, name):
        self.name = name
