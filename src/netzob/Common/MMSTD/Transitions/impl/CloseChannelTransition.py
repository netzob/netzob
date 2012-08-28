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
from gettext import gettext as _
import logging
import time


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition
from lxml import etree


#+---------------------------------------------------------------------------+
#| CloseChannelTransition:
#|    Special transition in charge of closing the transition
#+---------------------------------------------------------------------------+
class CloseChannelTransition(AbstractTransition):

    TYPE = "CloseChannel"

    def __init__(self, id, name, inputState, outputState, disconnectionTime):
        AbstractTransition.__init__(self, CloseChannelTransition.TYPE, id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition.py')
        self.disconnectionTime = disconnectionTime

    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return True

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.activate()
        result = self.closeConnection(abstractionLayer)
        self.deactivate()
        if result:
            return self.outputState
        else:
            return None

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        self.activate()
        result = self.closeConnection(abstractionLayer)
        self.deactivate()
        if result:
            return self.outputState
        else:
            return None

    #+-----------------------------------------------------------------------+
    #| closeConnection
    #|     Close the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def closeConnection(self, abstractionLayer):
        self.log.debug("CloseChannelTransition executed.")
        time.sleep(int(self.disconnectionTime) / 1000)
        abstractionLayer.disconnect()
        time.sleep(int(self.disconnectionTime) / 1000)
        return True

    def getDescription(self):
        return "CloseChannelTransition"

    def getDisconnectionTime(self):
        return self.disconnectionTime

    def save(self, root, namespace):
        xmlState = etree.SubElement(root, "{" + namespace + "}transition")
        xmlState.set("id", str(self.getID()))
        xmlState.set("name", str(self.getName()))
        xmlState.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:CloseChannelTransition")

        xmlStartState = etree.SubElement(xmlState, "{" + namespace + "}startState")
        xmlStartState.text = str(self.getInputState().getID())

        xmlEndState = etree.SubElement(xmlState, "{" + namespace + "}endState")
        xmlEndState.text = str(self.getOutputState().getID())

        xmlDisconnectionTime = etree.SubElement(xmlState, "{" + namespace + "}disconnectionTime")
        xmlDisconnectionTime.text = str(self.getDisconnectionTime())

    #+-----------------------------------------------------------------------+
    #| parse
    #|     Extract from an XML declaration the definition of the transition
    #| @param states the states already parsed while analyzing the MMSTD
    #| @return the instanciated object declared in the XML
    #+-----------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(states, xmlTransition, namespace, version):

        idTransition = xmlTransition.get("id")
        nameTransition = xmlTransition.get("name")

        idStartTransition = xmlTransition.find("{" + namespace + "}startState").text.strip()
        idEndTransition = xmlTransition.find("{" + namespace + "}endState").text.strip()

        inputStateTransition = None
        outputStateTransition = None
        for state in states:
            if state.getID() == idStartTransition:
                inputStateTransition = state
            if state.getID() == idEndTransition:
                outputStateTransition = state

        disconnectionTime = int(xmlTransition.find("{" + namespace + "}disconnectionTime").text)

        transition = CloseChannelTransition(idTransition, nameTransition, inputStateTransition, outputStateTransition, disconnectionTime)
        inputStateTransition.registerTransition(transition)
        return transition
