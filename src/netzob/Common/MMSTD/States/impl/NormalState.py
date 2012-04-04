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
#| NormalState:
#|     Definition of a normal state
#+---------------------------------------------------------------------------+
class NormalState(AbstractState):

    def __init__(self, id, name):
        AbstractState.__init__(self, "NormalState", id, name)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.States.impl.NormalState.py')
        self.transitions = []

    #+-----------------------------------------------------------------------+
    #| getTransitions
    #|     Return the associated transitions
    #| @return the transitions
    #+-----------------------------------------------------------------------+
    def getTransitions(self):
        return self.transitions

    #+-----------------------------------------------------------------------+
    #| unregisterTransition
    #|     Remove from the associate transitions the specified one
    #| @param transition the transition to unregister
    #+-----------------------------------------------------------------------+
    def unregisterTransition(self, transition):
        if transition in self.transitions:
            self.transitions.remove(transition)

    #+-----------------------------------------------------------------------+
    #| registerTransition
    #|     Associate a new transition to the current state
    #| @param transition the transition to associate
    #+-----------------------------------------------------------------------+
    def registerTransition(self, transition):
        if transition.getType() == "SemiStochastic":
            inputSymbol = transition.getInputSymbol()
            found = False
            for t in self.transitions:
                if t.getType() == "SemiStochastic" and t.getInputSymbol().getID() == inputSymbol.getID():
                    self.log.warn("Symbol = " + str(inputSymbol) + " == " + str(t.getInputSymbol()))
                    found = True
                else:
                    self.log.debug("Symbol = " + str(inputSymbol) + " != " + str(t.getInputSymbol()))
            if not found:
                self.transitions.append(transition)
            else:
                self.log.warn("OUPS, impossible to register the provided transition")
        else:
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
            self.log.warn("The current state has no transitions available.")
            return None

        # If there is a "special" transition we execute them
        for transition in self.getTransitions():
            if transition.getType() == "OpenChannel" or transition.getType() == "CloseChannel":
                newState = transition.executeAsClient(abstractionLayer)
                return newState

        self.activate()
        # Wait for a message

        tupleReception = abstractionLayer.receiveSymbolWithTimeout(5)
        if tupleReception == (None, None):
            self.log.warn("Warning the abstraction layer returns null")
            return None

        (receivedSymbol, message) = tupleReception
        if not receivedSymbol == None:
            self.log.debug("The following symbol has been received : " + str(receivedSymbol))
            # Now we verify this symbol is an accepted one
            for transition in self.getTransitions():
                if transition.isValid(receivedSymbol):
                    self.log.debug("Received data '" + str(message) + "' is valid for transition " + str(transition.getID()))
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
        self.activate()
        self.log.debug("Execute state " + self.name + " as a master")

        # Verify we can do something now
        if (len(self.getTransitions()) == 0):
            return None

        # given the current state, pick randomly a message and send it after having wait
        # the normal reaction time
        idRandom = random.randint(0, len(self.getTransitions()) - 1)
        pickedTransition = self.getTransitions()[idRandom]
        self.log.info("Randomly picked the transition " + pickedTransition.getName())

        newState = pickedTransition.executeAsMaster(abstractionLayer)

        # in case an error occured while executing the transition
        if newState == None:
            self.log.debug("The state has detected an error while executing the transition and consider it !")
            self.deactivate()
            return None

        self.deactivate()
        return newState

    def save(self, root, namespace):
        xmlState = etree.SubElement(root, "{" + namespace + "}state")
        xmlState.set("id", str(self.getID()))
        xmlState.set("name", str(self.getName()))
        xmlState.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:NormalState")

        # Save MemOpex
        if len(self.getMemOpexs()) > 0:
            xmlMemOpexs = etree.SubElement(xmlState, "{" + namespace + "}memopexs")
            for memOpex in self.getMemOpexs():
                memOpex.save(xmlMemOpexs, namespace)

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        idState = xmlRoot.get("id")
        nameState = xmlRoot.get("name")

        state = NormalState(idState, nameState)
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
