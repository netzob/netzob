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
import time
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition


#+---------------------------------------------------------------------------+
#| SimpleTransition:
#|     Definition of a simple transition (only sends something after X ms)
#+---------------------------------------------------------------------------+
class SimpleTransition(AbstractTransition):

    def __init__(self, id, name, inputState, outputState, timeBeforeActing, outputSymbol):
        AbstractTransition.__init__(self, "SimpleTransition", id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.SimpleTransition.py')
        self.outputSymbol = outputSymbol
        self.timeBeforeActing = timeBeforeActing

    #+-----------------------------------------------------------------------+
    #| getOutputSymbol
    #|     Return the associated output symbol
    #| @return the outputSymbol
    #+-----------------------------------------------------------------------+
    def getOutputSymbol(self):
        return self.outputSymbol

    #+-----------------------------------------------------------------------+
    #| getTimeBeforeSending
    #|     Return the time which will be paused before sending something
    #| @return the time time before sending
    #+-----------------------------------------------------------------------+
    def getTimeBeforeActing(self):
        return self.timeBeforeActing

    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return True

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Wait for the reception of a messag
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.activate()
        self.log.debug("Executing as a client")

        time.sleep(0.5)
        # write a message
        abstractionLayer.writeSymbol(self.outputSymbol)
        self.deactivate()
        return self.outputState

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Send input symbol and waits to received one of the output symbol
    #| @param input method access to the input flow
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        self.activate()
        self.log.debug("Execute as a master")
        # write a message
        abstractionLayer.writeSymbol(self.outputSymbol)

        # listen for input symbol for fex secondes
        abstractionLayer.receiveSymbolWithTimeout(3)

        self.deactivate()
        return self.outputState

    def getDescription(self):
        outputSymbolId = self.getOutputSymbol().getName()

        return "(" + str(outputSymbolId) + ";{after " + str(self.timeBeforeActing) + "})"

    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #| @return String representation of the XML
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        return None

    #+-----------------------------------------------------------------------+
    #| parse
    #|     Extract from an XML declaration the definition of the transition
    #| @param dictionary the dictionary which is used in the current MMSTD
    #| @param states the states already parsed while analyzing the MMSTD
    #| @return the instanciated object declared in the XML
    #+-----------------------------------------------------------------------+
    @staticmethod
    def parse(xmlTransition, dictionary, states):
        return None
