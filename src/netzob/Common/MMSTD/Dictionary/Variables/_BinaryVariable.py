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
import random
from bitarray import bitarray
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


class BinaryVariable(Variable):
    """BinaryVariable:
            A variable which contains binary data.
    """

    TYPE = "Binary"

    # OriginalValue : must be a "real" bitarray (a binary one)
    # min : nb of bits minimum
    # max : nb of bits maximum
    def __init__(self, id, name, originalValue, minBits, maxBits):
        """Constructor of BinaryVariable:

                @type originalValue: bitarray.bitarray
                @param originalValue: the initial value of this variable.
                @type minBits: integer
                @param minBits: the minimum number of bits in the variable value.
                @type maxBits: integer
                @param maxBits: the maximum number of bits in the variable value.
        """
        Variable.__init__(self, BinaryVariable.TYPE, id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable.py')
        self.originalValue = originalValue
        self.minBits = minBits
        self.maxBits = maxBits

        # Set the current value
        self.computeCurrentValue(self.originalValue)

    def computeCurrentValue(self, binValue):
        """computeCurrentValue:
                Compute a couple of binary and string values for the current variable.

                @type strValue: string
                @param strValue: a string value proposed as default value for this variable.
        """
        if binValue is not None:
            strCurrentValue = TypeConvertor.bitarray2StrBitarray(binValue)
            binCurrentValue = binValue
            self.currentValue = (binCurrentValue, strCurrentValue)
        else:
            self.currentValue = None

    def generateValue(self):
        """generateValue:
                Generate a valid value for the variable.
        """
        nbBits = random.randint(self.minBits, self.maxBits)
        creationArray = []
        for i in range(0, nbBits):
            if random.randint(0, 10) >= 6:
                creationArray.append(True)
            else:
                creationArray.append(False)

        return bitarray(creationArray)

    def compareFormat(self, value, indice, negative, vocabulary, memory):
        """compareFormat:
                Compute if the provided data is "format-compliant" and return the size of the biggest compliant data.

                @type value: bitarray.bitarray
                @param value: a bit array a subarray of which we compare to the current variable binray value.
                @type indice: integer
                @param indice: the starting point of comparison in value.
                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: integer
                @return: the size of the biggest compliant data, -1 if it does not comply.
        """
        tmp = value[indice:]
        self.log.debug("Compare format is " + str(len(value)) + " >= " + str(self.minBits))
        if len(tmp) >= self.minBits:
            return min(len(value), self.maxBits)
        else:
            return -1

#+---------------------------------------------------------------------------+
#| Functions Inherited from netzob.Common.MMSTD.Dictionary.Variable.Variable.|
#+---------------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        """getValue:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one else its NONE.
        """
        if self.getCurrentValue() is not None:
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            return memory.recall(self)

        return None

    def getValueToSend(self, negative, vocabulary, memory):
        """getValueToSend:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one or it generates one and save its value in memory.
        """
        if self.getCurrentValue() is not None:
            self.log.debug("BINARY : HAS CURRENT VALUE")
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            self.log.debug("BINARY : HAS NO CURRENT VALUE BUT HAS MEMORY")
            return memory.recall(self)

        # We generate a new value
        binNewValue = self.generateValue()
        strNewValue = TypeConvertor.bitarray2StrBitarray(self.generateValue())
        newValue = (binNewValue, strNewValue)

        # We save in memory the current value
        memory.memorize(self, newValue)

        # We return the newly generated and memorized value
        return newValue

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        return "[BIN]" + str(self.getName()) + "= (getVlue=" + str(self.getValue(negative, vocabulary, memory)) + ")"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return "[BIN]" + str(self.getName()) + "= (orig=" + str(self.getOriginalValue()) + ")"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        localValue = self.getValue(negative, vocabulary, memory)
        self.log.debug("Receive : " + str(value[indice:]))
        # In case we can't compare with a known value, we compare only the possibility to learn it afterward
        if localValue is None:
            self.log.debug("We compare the format (will we be able to learn it afterwards ?")
            return self.compareFormat(value, indice, negative, vocabulary, memory)
        else:
            (binVal, strVal) = localValue
            self.log.info("Compare : '" + str(value[indice:]) + "' with '" + str(binVal) + "' ")
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

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.
                Return the number of letters that matches, -1 if it does not match.
        """
        return self.compare(value, indice, negative, vocabulary, memory)

    def restore(self, vocabulary, memory):
        """restore:
                Restore learned value from the last execution of the variable.
        """
        memory.restore(self)

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:BinaryVariable")

        # Original Value
        if self.getOriginalValue() is not None:
            xmlBinaryVariableOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlBinaryVariableOriginalValue.text = TypeConvertor.bitarray2StrBitarray(self.getOriginalValue())

        # Minimum bits
        xmlBinaryVariableStartValue = etree.SubElement(xmlVariable, "{" + namespace + "}minBits")
        xmlBinaryVariableStartValue.text = str(self.getMinBits())

        # Maximum bits
        xmlBinaryVariableEndValue = etree.SubElement(xmlVariable, "{" + namespace + "}maxBits")
        xmlBinaryVariableEndValue.text = str(self.getMaxBits())

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getCurrentValue(self):
        return self.currentValue

    def getOriginalValue(self):
        return self.originalValue

    def getMinBits(self):
        return self.minBits

    def getMaxBits(self):
        return self.maxBits

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Load a binary variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            xmlBinaryVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlBinaryVariableOriginalValue is not None:
                originalValue = TypeConvertor.strBitarray2Bitarray(xmlBinaryVariableOriginalValue.text)
            else:
                originalValue = None

            xmlBinaryVariableStartValue = xmlRoot.find("{" + namespace + "}minBits")
            minBits = int(xmlBinaryVariableStartValue.text)

            xmlBinaryVariableEndValue = xmlRoot.find("{" + namespace + "}maxBits")
            maxBits = int(xmlBinaryVariableEndValue.text)

            return BinaryVariable(varId, varName, originalValue, minBits, maxBits)
        return None
