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
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


class ReferencedVariable(Variable):
    """ReferencedVariable:
            A variable pointing to an other variable.
    """

    def __init__(self, id, name, variableID):
        """Constructor of a ReferencedVariable:
                @type variableID: string
                @param variableID: id of the pointed variable.
        """
        Variable.__init__(self, "ReferencedVariable", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable.py')
        self.varID = variableID

    def getPointedVariable(self, vocabulary):
        """getPointedVariable:

                @rtype: netzob.Common.MMSTD.Dictionary.Variable.Variable
                @return: the pointed variable.
        """
        return vocabulary.getVariableByID(self.varID)

#+---------------------------------------------------------------------------+
#| Functions Inherited from netzob.Common.MMSTD.Dictionary.Variable.Variable.|
#+---------------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        """getValue:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one else its NONE.
        """
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.getValue(negative, vocabulary, memory)

    def getValueToSend(self, negative, vocabulary, memory):
        """getValueToSend:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one or it generates one and save its value in memory.
        """
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.getValueToSend(negative, vocabulary, memory)

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        return "ReferencedVariable (" + self.varID + ")"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return "ReferencedVariable (" + self.varID + ")"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        return var.compare(value, indice, negative, vocabulary, memory)

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.
                Return the number of letters that matches, -1 if it does not match.
        """
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        self.log.info("Compare with a referenced variable")
        return var.learn(value, indice, negative, vocabulary, memory)

    def restore(self, vocabulary, memory):
        """restore:
                Restore learned value from the last execution of the variable.
        """
        var = vocabulary.getVariableByID(self.varID)
        if var == None:
            self.log.error("Impossible to retrieve the referenced variable which's ID = " + self.varID)
            return None
        self.log.info("Compare with a referenced variable")
        return var.restore(vocabulary, memory)

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        xmlWordVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlWordVariable.set("id", str(self.getID()))
        xmlWordVariable.set("name", str(self.getName()))

        xmlWordVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ReferencedVariable")

        # Definition of the referenced
        xmlWordVariableRef = etree.SubElement(xmlWordVariable, "{" + namespace + "}ref")
        xmlWordVariableRef.text = self.varID
        return xmlWordVariable

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Load a referenced variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            refVarId = xmlRoot.find("{" + namespace + "}ref").text
            return ReferencedVariable(varId, varName, refVarId)

        return None
