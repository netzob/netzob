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

    def __init__(self, id, name, variableID):
        Variable.__init__(self, "ReferencedVariable", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable.py')
        self.varID = variableID

    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.getValue(negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.getValueToSend(negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        return "ReferencedVariable (" + self.varID + ")"

    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+
    def getUncontextualizedDescription(self):
        return "ReferencedVariable (" + self.varID + ")"

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.compare(value, indice, negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        self.log.info("Compare with a referenced variable")
        return var.learn(value, indice, negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| restore :
    #|     Restore learnt value from the last execution of the variable
    #+-----------------------------------------------------------------------+
    def restore(self, vocabulary, memory):
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        self.log.info("Compare with a referenced variable")
        return var.restore(vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| toXML
    #|     Returns the XML description of the variable
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        xmlWordVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlWordVariable.set("id", str(self.getID()))
        xmlWordVariable.set("name", str(self.getName()))

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

            refVarId = xmlRoot.find("{" + namespace + "}ref").text
            return ReferencedVariable(varId, varName, refVarId)

        return None
