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
from lxml import etree
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from bitarray import bitarray


#+---------------------------------------------------------------------------+
#| AggregrateVariable:
#|     Definition of an aggregation of variables defined in a dictionary
#+---------------------------------------------------------------------------+
class AggregateVariable(Variable):
    """AggregateVariable:
            Aggregation of variables defined in a dictionary.
    """

    def __init__(self, idVar, name, children=None):
        """Constructor of AggregateVariable:
                @type children: netzob.Common.MMSTD.Dictionary.Variable.Variable List
                @param children: the list of all its children.
        """
        Variable.__init__(self, "Aggregate", idVar, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.py')
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
        binResult = bitarray()
        strResult = ""
        for var in self.children:
            (b, s) = var.getValue(negative, vocabulary, memory)
            self.log.debug("getValue : " + str(b))
            binResult += b
            strResult = strResult + s
        return (binResult, strResult)

    def getValueToSend(self, negative, vocabulary, memory):
        """getValueToSend:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one or it generates one and save its value in memory.
        """
        binResult = bitarray()
        strResult = ""
        for var in self.children:
            (b, s) = var.getValueToSend(negative, vocabulary, memory)
            self.log.debug("getValueToSend : " + str(b))
            binResult += b
            strResult = strResult + s
        return (binResult, strResult)

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        values = []
        for var in self.children:
            values.append(var.getDescription(negative, vocabulary, memory))
        return "[AGG]" + str(self.getName()) + "= (" + " AND ".join(values) + ")"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        values = []
        for var in self.children:
            values.append(var.getUncontextualizedDescription())
        return "[AGG]" + str(self.getName()) + "= (" + " AND ".join(values) + ")"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        result = indice
        for var in self.children:
            self.log.debug("Indice = " + str(result) + " : " + var.getDescription(negative, vocabulary, memory))
            self.log.debug("=> " + str(value[result:]))
            result = var.compare(value, result, negative, vocabulary, memory)
            if result == -1 or result == None:
                self.log.debug("Compare fail")
                return result
            else:
                self.log.debug("Compare successful")
        return result

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.
                Return the number of letters that matches, -1 if it does not match.
        """
        status = True
        toBeRestored = []
        result = indice

        for var in self.children:
            self.log.debug("Indice = " + str(result) + " : " + var.getDescription(negative, vocabulary, memory))
            result = var.learn(value, result, negative, vocabulary, memory)
            toBeRestored.append(var)
            if result == -1 or result == None:
                self.log.debug("Compare fail")
                status = False
                break
            else:
                self.log.debug("Compare successful")

        # If it has failed we restore every executed vars
        if not status:
            for var in toBeRestored:
                var.restore(vocabulary, memory)
        return result

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
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")
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
                Load an aggregate variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = Variable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AggregateVariable(varId, varName, children)
        return None
