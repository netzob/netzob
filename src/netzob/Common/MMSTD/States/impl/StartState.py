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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from lxml import etree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.States.AbstractState import AbstractState


#+---------------------------------------------------------------------------+
#| StartState:
#|     Definition of a starting state (open the communication layer)
#+---------------------------------------------------------------------------+
class StartState(AbstractState):

    def __init__(self, id, name):
        AbstractState.__init__(self, "StartState", id, name)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.States.impl.StartState.py')
        self.transitions = []

    #+-----------------------------------------------------------------------+
    #| getTransitions
    #|     Return the associated transitions
    #| @return the transitions
    #+-----------------------------------------------------------------------+
    def getTransitions(self):
        return self.transitions

    #+-----------------------------------------------------------------------+
    #| registerTransition
    #|     Associate a new transition ot the current state
    #| @param transition the transition to associate
    #+-----------------------------------------------------------------------+
    def registerTransition(self, transition):
        self.transitions.append(transition)

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Execute the state as a client
    #| @param abstractionLayer the layer between the MMSTD and the world
    #| @return the next state after execution of current one
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.log.debug("Execute state " + self.name + " as a client")

        # if no transition exists we quit
        if len(self.getTransitions()) == 0:
            return None

        self.activate()

        # We open the connection
        abstractionLayer.connect()

        # Wait for a message
        (receivedSymbol, message) = abstractionLayer.receiveSymbol()
        if not receivedSymbol is None:
            self.log.debug("The following symbol has been received : " + str(receivedSymbol))
            # Now we verify this symbol is an accepted one
            for transition in self.getTransitions():
                if transition.isValid(receivedSymbol):
                    self.log.debug("Received data '" + message + "' is valid for transition " + str(transition.getID()))
                    newState = transition.executeAsClient(abstractionLayer)
                    self.deactivate()
                    return newState
            self.log.warn("The message abstracted in a symbol is not valid according to the automata")
        self.deactivate()
        return self

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Execute the state as a server
    #| @param abstractionLayer the layer between the MMSTD and the world
    #| @return the next state after execution of current one
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        # Verify we can do something now
        if (len(self.getTransitions()) == 0):
            return None

        self.activate()
        self.log.debug("Execute state " + self.name + " as a master")

        # We open the connection
        abstractionLayer.connect()

        # given the current state, pick randomly a message and send it after having wait
        # the normal reaction time
        idRandom = random.randint(0, len(self.getTransitions()) - 1)
        pickedTransition = self.getTransitions()[idRandom]
        self.log.debug("Randomly picked the transition " + pickedTransition.getName())

        newState = pickedTransition.executeAsMaster(abstractionLayer)
        self.deactivate()
        return newState

    def save(self, root, namespace):
        xmlState = etree.SubElement(root, "{" + namespace + "}state")
        xmlState.set("id", str(self.getID()))
        xmlState.set("name", str(self.getName()))
        xmlState.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:StartState")

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        idState = xmlRoot.get("id")
        nameState = xmlRoot.get("name")

        state = StartState(idState, nameState)
        return state

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name
