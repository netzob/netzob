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
from lxml import etree
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable


class AlternateVariable(Variable):
    """AlternateVariable:
            A node variable that makes an alternative of all its children.
    """

    def __init__(self, idVar, name, children):
        """Constructor of AlternateVariable:
                @type children: netzob.Common.MMSTD.Dictionary.Variable.Variable List
                @param children: the list of all its children.
        """
        Variable.__init__(self, "Alternate", idVar, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.AlternativeVariable.py')
        self.children = []
        if children != None:
            self.children.extend(children)

#+---------------------------------------------------------------------------+
#| Functions Inherited from netzob.Common.MMSTD.Dictionary.Variable.Variable.|
#+---------------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        """getValue:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one else its NONE.
        """
        self.log.info("getValue")
        for var in self.children:
            if var.getValue(negative, vocabulary, memory) != None:
                return var.getValue(negative, vocabulary, memory)
        return None
#        validVars = []
#        self.log.debug("Valid vars = " + str(validVars))
#        idRandom = random.randint(0, len(validVars) - 1)
#        picked = validVars[idRandom]
#        self.log.debug("Get value will return : " + str(picked))
#        return picked.getValue(negative, vocabulary, memory)

    def getValueToSend(self, negative, vocabulary, memory):
        """getValueToSend:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one or it generates one and save its value in memory.
        """
        self.log.info("getValueToSend")
        idRandom = random.randint(0, len(self.children) - 1)
        picked = self.children[idRandom]
        return picked.getValueToSend(negative, vocabulary, memory)
#        for var in self.children:
#            if var.getValue(negative, vocabulary, memory) != None:
#                return var.getValueToSend(negative, vocabulary, memory)
#        return None

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        values = []
        for var in self.children:
            values.append(var.getDescription(negative, vocabulary, memory))
        return "[ALT]" + str(self.getName()) + "= (" + " OR ".join(values) + ")"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        values = []
        for var in self.children:
            values.append(var.getUncontextualizedDescription())
        return "[ALT]" + str(self.getName()) + "= (" + " OR ".join(values) + ")"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        saved = indice
        for var in self.children:
            self.log.info("Indice = " + str(saved) + " : " + var.getDescription(negative, vocabulary, memory))
            result = var.compare(value, saved, negative, vocabulary, memory)
            if result != -1 and result != None:
                self.log.info("Compare successful")
                return result
        return -1

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.
                Return the number of letters that matches, -1 if it does not match.
        """
        saved = indice
        for var in self.children:
            self.log.info("Indice = " + str(saved) + " : " + var.getDescription(negative, vocabulary, memory))
            result = var.learn(value, saved, negative, vocabulary, memory)
            if result != -1 and result != None:
                self.log.info("Compare successful")
                return result
            else:
                var.restore(vocabulary, memory)

        return -1

    def restore(self, vocabulary, memory):
        """restore:
                Restore learned value from the last execution of the variable.
        """
        for var in self.children:
            var.restore(vocabulary, memory)

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AlternateVariable")

        # Definition of the variables
        for var in self.children:
            var.toXML(xmlVariable, namespace)

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getChildren(self):
        return self.children

    def addChild(self, child):
        self.children.append(child)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Load an alternate variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = Variable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)

            return AlternateVariable(varId, varName, children)
        return None
