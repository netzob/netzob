# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
#| Standard library imports
#+----------------------------------------------
import logging
import time
import threading
import uuid

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------

from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


#+----------------------------------------------
#| NetworkOracle:
#+----------------------------------------------
class NetworkOracle(threading.Thread):

    def __init__(self, communicationChannel, isMaster):
        threading.Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Oracle.NetworkOracle.py')
        self.communicationChannel = communicationChannel
        self.isMaster = isMaster

    def setMMSTD(self, mmstd):
        self.mmstd = mmstd

    def run(self):
        self.log.info("Start the network oracle based on given MMSTD")

        # Create a new and clean memory
        memory = Memory()
        # memory = Memory(self.mmstd.getVocabulary().getVariables())
        memory.createMemory()
        # Create the abstraction layer for this connection
        abstractionLayer = AbstractionLayer(self.communicationChannel, self.mmstd.getVocabulary(), memory)

        # And we create an MMSTD visitor for this
        anID = str(uuid.uuid4())
        self.oracle = MMSTDVisitor(anID, "MMSTD-NetworkOracle", self.mmstd, self.isMaster, abstractionLayer)
        self.oracle.start()

        while (self.oracle.isAlive()):
            time.sleep(0.01)

        self.log.warn("The network ORACLE has finished")

    def stop(self):
        self.log.info("Stop the network oracle")
        self.oracle.stop()

    def hasFinish(self):
        return not self.oracle.isActive()

    def getGeneratedInputSymbols(self):
        symbols = []
        abstractionLayer = self.oracle.getAbstractionLayer()
        for i in abstractionLayer.getGeneratedInputSymbols():
            symbols.append(DictionarySymbol(i))
        return symbols

    def getGeneratedOutputSymbols(self):
        symbols = []
        abstractionLayer = self.oracle.getAbstractionLayer()
        for o in abstractionLayer.getGeneratedOutputSymbols():
            symbols.append(DictionarySymbol(o))
        return symbols

    def getResults(self):
        symbols = []
        # Retrieve all the IO from the abstraction layer
        abstractionLayer = self.oracle.getAbstractionLayer()
        print("Abstraction layer = {}".format(str(abstractionLayer)))
        for io in abstractionLayer.getGeneratedInputAndOutputsSymbols():
            symbols.append(DictionarySymbol(io))
        return symbols
