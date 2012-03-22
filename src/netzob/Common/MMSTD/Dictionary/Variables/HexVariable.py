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
import random
from bitarray import bitarray
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| HexVariable:
#|     Definition of an hex variable
#+---------------------------------------------------------------------------+
class HexVariable(Variable):

    # OriginalValue : must be a "string" which describes the hexadecimal (e5f026..)
    # min : nb of hex minimum
    # max : nb of hex maximum
    def __init__(self, id, name, originalValue, minHex, maxHex):
        Variable.__init__(self, "Hexadecimal", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.originalValue = originalValue
        self.minHex = minHex
        self.maxHex = maxHex

        # Set the current value
        self.computeCurrentValue(self.originalValue)

    #+-----------------------------------------------------------------------+
    #| computeCurrentValue :
    #|     Transform and save the provided (ef56d2...) as current value
    #+-----------------------------------------------------------------------+
    def computeCurrentValue(self, strValue):
        if strValue != None:
            strCurrentValue = strValue
            binCurrentValue = TypeConvertor.netzobRawToBitArray(strValue)
            self.currentValue = (binCurrentValue, strCurrentValue)
        else:
            self.currentValue = None

    #+-----------------------------------------------------------------------+
    #| generateValue :
    #|     Generate a valid value for the variable (ef56d2...)
    #+-----------------------------------------------------------------------+
    def generateValue(self):
        nbHex = random.randint(self.minHex, self.maxHex)
        creationArray = []
        for i in range(0, nbHex):
            valInt = random.randint(0, 15)
            creationArray.append(str(hex(valInt))[2:])

        return ''.join(creationArray)

    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        if self.getCurrentValue() != None:
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            return memory.recall(self)

        return None

    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        if self.getCurrentValue() != None:
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            return memory.recall(self)

        # We generate a new value
        self.computeCurrentValue(self.generateValue())

        # We save in memory the current value
        memory.memorize(self, self.getCurrentValue())

        # We return the newly generated and memorized value
        return self.getCurrentValue()

    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+
    def getUncontextualizedDescription(self):
        return "[HEX]" + str(self.getName()) + "= (orig=" + str(self.getOriginalValue()) + ")"

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        return "[HEX]" + str(self.getName()) + "= (getVlue=" + str(self.getValue(negative, vocabulary, memory)) + ")"

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        localValue = self.getValue(negative, vocabulary, memory)
        # In case we can't compare with a known value, we compare only the possibility to learn it afterward
        if localValue == None:
            self.log.debug("We compare the format (will we be able to learn it afterwards ?")
            return self.compareFormat(value, indice, negative, vocabulary, memory)
        else:
            (binVal, strVal) = localValue
            self.log.info("Compare received : '" + str(value[indice:]) + "' with '" + str(binVal) + "' ")
            tmp = value[indice:]
            if len(tmp) >= len(binVal):
                if tmp[:len(binVal)] == binVal:
                    self.log.info("Compare successful")
                    return indice + len(binVal)
                else:
                    self.log.info("error in the comparison")
                    return -1
            else:
                self.log.info("Compare fail")
                return -1

    def compareFormat(self, value, indice, negative, vocabulary, memory):
        tmp = value[indice:]
        self.log.debug("Compare format is " + str(len(value)) + " >= " + str(self.minBits))
        if len(tmp) >= self.minBits:
            return min(len(value), self.maxBits)
        else:
            return -1

    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        return self.compare(value, indice, negative, vocabulary, memory)

    #+-----------------------------------------------------------------------+
    #| restore :
    #|     Restore learnt value from the last execution of the variable
    #+-----------------------------------------------------------------------+
    def restore(self, vocabulary, memory):
        memory.restore(self)

    def getCurrentValue(self):
        return self.currentValue

    def getOriginalValue(self):
        return self.originalValue

    def getMinHexs(self):
        return self.minHex

    def getMaxHexs(self):
        return self.maxHex

    #+-----------------------------------------------------------------------+
    #| toXML :
    #|     Returns the XML description of the variable
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:HexVariable")

        # Original Value
        if self.getOriginalValue() != None:
            xmlHexVariableOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlHexVariableOriginalValue.text = self.getOriginalValue()

        # Minimum hex
        xmlHexVariableStartValue = etree.SubElement(xmlVariable, "{" + namespace + "}minHexs")
        xmlHexVariableStartValue.text = str(self.getMinHexs())

        # Maximum hex
        xmlHexVariableEndValue = etree.SubElement(xmlVariable, "{" + namespace + "}maxHexs")
        xmlHexVariableEndValue.text = str(self.getMaxHexs())

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            xmlHexVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlHexVariableOriginalValue != None:
                originalValue = xmlHexVariableOriginalValue.text
            else:
                originalValue = None

            xmlHexVariableStartValue = xmlRoot.find("{" + namespace + "}minHexs")
            minHexs = int(xmlHexVariableStartValue.text)

            xmlHexVariableEndValue = xmlRoot.find("{" + namespace + "}maxHexs")
            maxHexs = int(xmlHexVariableEndValue.text)

            return HexVariable(varId, varName, originalValue, minHexs, maxHexs)
        return None
