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
import binascii
import random
import string
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| ReferencedVariable:
#|     Definition of a referenced variable
#+---------------------------------------------------------------------------+
class ReferencedVariable(Variable):

    def __init__(self, id, name, mutable, variableID):
        Variable.__init__(self, "ReferencedVariable", id, name, mutable)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable.py')
        self.varID = variableID

    def compare(self, value, indice, negative, memory):
        var = memory.getVariableByID(self.varID)
        self.log.info("Compare with a referenced variable")
        return var.compare(value, indice, negative, memory)

    def send(self, negative, memory):
        var = memory.getVariableByID(self.varID)
        return var.send(negative, memory)

    def getValue(self, negative, memory):
        var = memory.getVariableByID(self.varID)
        return var.getValue(negative, memory)

    def getDescription(self):
        return "ReferencedVariable (" + self.varID + ")"

    def save(self, root, namespace):
        xmlWordVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlWordVariable.set("id", str(self.getID()))
        xmlWordVariable.set("name", str(self.getName()))
        xmlWordVariable.set("mutable", TypeConvertor.bool2str(self.isMutable()))

        xmlWordVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ReferencedVariable")

        # Definition of the referenced
        xmlWordVariableRef = etree.SubElement(xmlWordVariable, "{" + namespace + "}ref")
        xmlWordVariableRef.text = self.varID
        return xmlWordVariable

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            varIsMutable = TypeConvertor.str2bool(xmlRoot.get("mutable"))

            refVarId = xmlRoot.find("{" + namespace + "}ref").text
            return ReferencedVariable(varId, varName, varIsMutable, refVarId)

        return None

