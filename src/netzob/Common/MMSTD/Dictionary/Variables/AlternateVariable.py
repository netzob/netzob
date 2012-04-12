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
import random
from lxml import etree
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable


#+---------------------------------------------------------------------------+
#| AlternateVariable:
#|     Definition of an alternative of variables defined in a dictionary
#+---------------------------------------------------------------------------+
class AlternateVariable(Variable):

    TYPE = "Alternate"

    def __init__(self, idVar, name, vars):
        Variable.__init__(self, AlternateVariable.TYPE, idVar, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.AlternativeVariable.py')
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
        self.log.info("getValue")
        validVars = []
        for var in self.vars:
            if var.getValue(negative, vocabulary, memory) != None:
                return var.getValue(negative, vocabulary, memory)
        return None
#        self.log.debug("Valid vars = " + str(validVars))
#        idRandom = random.randint(0, len(validVars) - 1)
#        picked = validVars[idRandom]
#        self.log.debug("Get value will return : " + str(picked))
#        return picked.getValue(negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        self.log.info("getValueToSend")
        """
        for var in self.vars:
            if var.getValue(negative, vocabulary, memory) != None:
                return var.getValueToSend(negative, vocabulary, memory)
        return None
        """

        idRandom = random.randint(0, len(self.vars) - 1)
        picked = self.vars[idRandom]
        return picked.getValueToSend(negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+
    def getUncontextualizedDescription(self):
        values = []
        for var in self.vars:
            values.append(var.getUncontextualizedDescription())
        return "[ALT]" + str(self.getName()) + "= (" + " OR ".join(values) + ")"

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        values = []
        for var in self.vars:
            values.append(var.getDescription(negative, vocabulary, memory))
        return "[ALT]" + str(self.getName()) + "= (" + " OR ".join(values) + ")"

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        saved = indice
        for var in self.vars:
            self.log.info("Indice = " + str(saved) + " : " + var.getDescription(negative, vocabulary, memory))
            result = var.compare(value, saved, negative, vocabulary, memory)
            if result != -1 and result != None:
                self.log.info("Compare successful")
                return result
        return -1

    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        saved = indice
        for var in self.vars:
            self.log.info("Indice = " + str(saved) + " : " + var.getDescription(negative, vocabulary, memory))
            result = var.learn(value, saved, negative, vocabulary, memory)
            if result != -1 and result != None:
                self.log.info("Compare successful")
                return result
            else:
                var.restore(vocabulary, memory)

        return -1

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
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AlternateVariable")

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

            return AlternateVariable(varId, varName, children)
        return None
