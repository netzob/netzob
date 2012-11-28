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


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractTransition:
#|     Definition of a transition
#+---------------------------------------------------------------------------+
class AbstractTransition():

    #+-----------------------------------------------------------------------+
    #| WARNING:
    #|     it does not register the transition on the input state !!!!!!!
    #+-----------------------------------------------------------------------+
    def __init__(self, type, id, name, inputState, outputState):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.AbstractTransition.py')
        self.type = type
        self.id = id
        self.name = name
        self.outputState = outputState
        self.inputState = inputState
        self.active = False

    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Abstract method to compute if current transition is valid with
    #|     given input symbol
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def isValid(self, inputSymbol):
        self.log.error("The transition class doesn't support 'isValid'.")
        raise NotImplementedError("The transition class doesn't support 'isValid'.")

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Abstract method to execute the current transition as a client given the
    #|     the input and the output method access
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.log.error("The transition class doesn't support 'executeAsClient'.")
        raise NotImplementedError("The transition class doesn't support 'executeAsClient'.")

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Abstract method to execute the current transition as a server given the
    #|     the input and the output method access
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractLayer):
        self.log.error("The transition class doesn't support 'executeAsMaster'.")
        raise NotImplementedError("The transition class doesn't support 'executeAsMaster'.")

    #+-----------------------------------------------------------------------+
    #| getDescription
    #|     computes and return a description for the current transition
    #| @return a string composed of a description
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getDescription(self):
        self.log.error("The transition class doesn't support 'getDescription'.")
        raise NotImplementedError("The transition class doesn't support 'getDescription'.")

    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        self.log.error("The transition class doesn't support 'toXMLString'.")
        raise NotImplementedError("The transition class doesn't support 'toXMLString'.")

    #+-----------------------------------------------------------------------+
    #| active
    #|    active the current state
    #+-----------------------------------------------------------------------+
    def activate(self):
        self.active = True

    #+-----------------------------------------------------------------------+
    #| deactivate
    #|    deactivate the current state
    #+-----------------------------------------------------------------------+
    def deactivate(self):
        self.active = False

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getOutputState(self):
        return self.outputState

    def getInputState(self):
        return self.inputState

    def isActive(self):
        return self.active

    def getType(self):
        return self.type

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setOutputState(self, outputState):
        self.outputState = outputState

    def setInputState(self, inputState):
        self.inputState = inputState

    @staticmethod
    def loadFromXML(states, vocabulary, xmlRoot, namespace, version):
        if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:OpenChannelTransition":
            from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition
            return OpenChannelTransition.loadFromXML(states, xmlRoot, namespace, version)
        elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:CloseChannelTransition":
            from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import CloseChannelTransition
            return CloseChannelTransition.loadFromXML(states, xmlRoot, namespace, version)
        elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:SimpleTransition":
            from netzob.Common.MMSTD.Transitions.impl.SimpleTransition import SimpleTransition
            return SimpleTransition.loadFromXML(states, xmlRoot, namespace, version)
        elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:SemiStochasticTransition":
            from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition
            return SemiStochasticTransition.loadFromXML(states, vocabulary, xmlRoot, namespace, version)
        else:
            raise NameError("The parsed xml doesn't represent a valid type message (" + xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") + ").")
            return None
