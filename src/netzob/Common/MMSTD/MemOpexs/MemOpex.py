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
#| MemOpex:
#|     Definition of a Memory Operation (must be subclassed to be useful)
#+---------------------------------------------------------------------------+
class MemOpex():

    def __init__(self, type, id, transitionId):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.MemOpexs.MemOpex.py')
        self.id = id
        self.transitionId = transitionId
        self.type = type

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getTransitionID(self):
        return self.transitionId

    def getType(self):
        return self.type

    def setID(self, id):
        self.id = id

    def setTransitionID(self, transitionID):
        self.transitionId = transitionID

    #+-----------------------------------------------------------------------+
    #| save
    #|     Abstract method to retrieve the XML definition of current MemOpex
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        self.log.error("The MemOpex class doesn't support 'save'.")
        raise NotImplementedError("The state MemOpex doesn't support 'save'.")

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ForgetMemOpex":
            from netzob.Common.MMSTD.MemOpexs.impl.ForgetMemOpex import ForgetMemOpex
            return ForgetMemOpex.loadFromXML(xmlRoot, namespace, version)
        else:
            raise NameError("The parsed xml doesn't represent a valid type of MemOpex.")
            return None
