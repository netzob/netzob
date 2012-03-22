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
from lxml import etree
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from bitarray import bitarray


#+---------------------------------------------------------------------------+
#| AggregrateVariable:
#|     Definition of an aggregation of variables defined in a dictionary
#+---------------------------------------------------------------------------+
class AggregateVariable(Variable):

    TYPE = "Aggregate"

    def __init__(self, idVar, name, vars=None):
        Variable.__init__(self, AggregateVariable.TYPE, idVar, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.py')
        self.vars = []
        if vars != None:
            self.vars.extend(vars)

    def addChild(self, variable):
        self.vars.append(variable)

    def getChildren(self):
        return self.vars

    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        binResult = bitarray()
        strResult = ""
        for var in self.vars:
            (b, s) = var.getValue(negative, vocabulary, memory)
            self.log.debug("getValue : " + str(b))
            binResult += b
            strResult = strResult + s
        return (binResult, strResult)

    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        binResult = bitarray()
        strResult = ""
        for var in self.vars:
            (b, s) = var.getValueToSend(negative, vocabulary, memory)
            self.log.debug("getValueToSend : " + str(b))
            binResult += b
            strResult = strResult + s
        return (binResult, strResult)

    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+
    def getUncontextualizedDescription(self):
        values = []
        for var in self.vars:
            values.append(var.getUncontextualizedDescription())
        return "[AGG]" + str(self.getName()) + "= (" + " AND ".join(values) + ")"

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        values = []
        for var in self.vars:
            values.append(var.getDescription(negative, vocabulary, memory))
        return "[AGG]" + str(self.getName()) + "= (" + " AND ".join(values) + ")"

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        result = indice
        for var in self.vars:
            self.log.debug("Indice = " + str(result) + " : " + var.getDescription(negative, vocabulary, memory))
            self.log.debug("=> " + str(value[result:]))
            result = var.compare(value, result, negative, vocabulary, memory)
            if result == -1 or result == None:
                self.log.debug("Compare fail")
                return result
            else:
                self.log.debug("Compare successful")
        return result

    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        status = True
        toBeRestored = []
        result = indice

        for var in self.vars:
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

    #+-----------------------------------------------------------------------+
    #| restore :
    #|     Restore learnt value from the last execution of the variable
    #+-----------------------------------------------------------------------+
    def restore(self, vocabulary, memory):
        for var in self.vars:
            var.restore(vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| toXML
    #|     Returns the XML description of the variable
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")
        # Definition of the variables
        for var in self.vars:
            var.toXML(xmlVariable, namespace)

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = Variable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AggregateVariable(varId, varName, children)
        return None
