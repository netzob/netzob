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


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| AbstractState:
#|     Definition of a state
#+---------------------------------------------------------------------------+
class AbstractState():

    def __init__(self, type, id, name):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.States.AbstractState.py')
        self.id = id
        self.name = name
        self.type = type
        self.active = False
        self.memOpexs = []

    #+-----------------------------------------------------------------------+
    #| getTransitions
    #|     Abstract method to retrieve the associated transitions
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getTransitions(self):
        self.log.error("The state class doesn't support 'getTransitions'.")
        raise NotImplementedError("The state class doesn't support 'getTransitions'.")

    #+-----------------------------------------------------------------------+
    #| registerTransition
    #|     Abstract method to register a new transition to current state
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def registerTransition(self, transition):
        self.log.error("The state class doesn't support 'registerTransition'.")
        raise NotImplementedError("The state class doesn't support 'registerTransition'.")

    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Abstract method to execute the current state as a client given the
    #|     the input and the output method access
    #| @param abstractionLayer the layer between the MMSTD and the world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.log.error("The state class doesn't support 'executeAsClient'.")
        raise NotImplementedError("The state class doesn't support 'executeAsClient'.")

    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Abstract method to execute the current state as a master given the
    #|     the input and the output method access
    #| @param abstractionLayer the layer between the MMSTD and the world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        self.log.error("The state class doesn't support 'executeAsMaster'.")
        raise NotImplementedError("The state class doesn't support 'executeAsMaster'.")

    #+-----------------------------------------------------------------------+
    #| save
    #|     Abstract method to retrieve the XML definition of current state
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        self.log.error("The state class doesn't support 'save'.")
        raise NotImplementedError("The state class doesn't support 'save'.")

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
    #| getMemOpexs
    #|    returns the memory operations associated with current state
    #+-----------------------------------------------------------------------+
    def getMemOpexs(self):
        return self.memOpexs

    #+-----------------------------------------------------------------------+
    #| addMemOpex
    #|    register a memory operation on current state
    #+-----------------------------------------------------------------------+
    def addMemOpex(self, memOpex):
        self.memOpexs.append(memOpex)

    #+-----------------------------------------------------------------------+
    #| removeMemOpex
    #|    unregister the provided memory operation from current state
    #+-----------------------------------------------------------------------+
    def removeMemOpex(self, memOpex):
        self.memOpexs.remove(memOpex)

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def isActive(self):
        return self.active

    def getType(self):
        return self.type

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:NormalState":
            from netzob.Common.MMSTD.States.impl.NormalState import NormalState
            return NormalState.loadFromXML(xmlRoot, namespace, version)
        else:
            raise NameError("The parsed xml doesn't represent a valid type message.")
            return None
