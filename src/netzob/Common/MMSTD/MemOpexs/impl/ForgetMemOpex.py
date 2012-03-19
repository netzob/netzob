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
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.MemOpexs.MemOpex import MemOpex


#+---------------------------------------------------------------------------+
#| ForgetMemOpex:
#|     Definition of a forget memory operation (reset the value if memory)
#+---------------------------------------------------------------------------+
class ForgetMemOpex(MemOpex):

    def __init__(self, id, transitionId, variableId):
        MemOpex.__init__(self, "ForgetMemOpex", id, transitionId)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.MemOpex.impl.ForgetMemOpex.py')
        self.variableId = variableId

    def save(self, root, namespace):
        xmlForgetMemOpex = etree.SubElement(root, "{" + namespace + "}memopex")
        xmlForgetMemOpex.set("id", str(self.getID()))
        xmlForgetMemOpex.set("transitionId", str(self.getTransitionID()))

        # variableID
        xmlForgetMemOpexVariable = etree.SubElement(xmlForgetMemOpex, "{" + namespace + "}variableId")
        xmlForgetMemOpexVariable.text = str(self.getVariableID())

        xmlForgetMemOpex.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ForgetMemOpex")

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        idMemOpex = xmlRoot.get("id")
        idTransition = xmlRoot.get("transitionId")

        xmlForgetVariable = xmlRoot.find("{" + namespace + "}variableId")
        variableID = xmlForgetVariable.text

        memOpex = ForgetMemOpex(idMemOpex, idTransition, variableID)
        return memOpex

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getVariableID(self):
        return self.variableId

    def setVariableID(self, variableID):
        self.variableId = variableID
