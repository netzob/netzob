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
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.TypeIdentifier import TypeIdentifier


class DecimalWordVariable(Variable):
    """DecimalWordVariable:
            A decimal word is an ASCII set of characters in string.numbers.
            (0-9)*
    """

    # OriginalValue : must be a decimal ASCII word
    def __init__(self, id, name, originalValue):
        """Constructor of DecimalWordVariable:
                @type originalValue: string
                @param originalValue: a decimal ASCII word (set of characters in string.numbers) which will be the originalValue of this variable.
        """
        Variable.__init__(self, "DecimalWord", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.DecimalVariable.py')
        self.originalValue = originalValue

        # Set the original value (in bitarray)
        self.computeCurrentValue(self.originalValue)

    def computeCurrentValue(self, strValue):
        """computeCurrentValue:
                Compute a couple of binary and string values for the current variable.

                @type strValue: string
                @param strValue: a string value proposed as default value for this variable.
        """
        if strValue is not None:
            strCurrentValue = strValue
            binCurrentValue = TypeConvertor.string2bin(strValue)
            self.currentValue = (binCurrentValue, strCurrentValue)
        else:
            self.currentValue = None

    #+-----------------------------------------------------------------------+
    #| generateValue :
    #|     Generate a valid value for the variable ('babar'...)
    #+-----------------------------------------------------------------------+
    def generateValue(self):
        """generateValue:
                Generate a valid value for the variable.
        """
        # todo
        self.log.debug("Generating value ")
        return '1000'
# Generate a WORD value
#        nb_letter = random.randint(0, 10)
#        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
#        self.binVal = self.string2bin(self.strVal)
#        self.log.debug("Generated : " + self.strVal)
#        self.log.debug("Generated -bin)= " + str(self.binVal))

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
        size = len(tmp)
        if size <= 8:
            self.log.debug("Too small, not even 8 bits available (1 number)")
            return -1
        for i in range(size, 8, -1):
            subValue = value[indice:indice + i - 1]
            strVal = TypeConvertor.bin2string(TypeConvertor.strBitarray2Bitarray(subValue))
            typeIdentifier = TypeIdentifier()
            if typeIdentifier.isAscii(strVal):
                if (strVal.isdigit()):
                    self.log.debug("Its a numeric : (" + str(strVal) + ")")
                    return i + indice - 1
        self.log.debug("the value " + str(TypeConvertor.bin2string(TypeConvertor.strBitarray2Bitarray(tmp))) + " cannot be parsed as a decimalWord")
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
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            return memory.recall(self)

        # We generate a new value
        strValue = self.generateValue()
        binValue = TypeConvertor.string2bin(strValue)

        # We save in memory the current value
        memory.memorize(self, (binValue, strValue))

        # We return the newly generated and memorized value
        return (binValue, strValue)

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return "[DECIMALWORD]" + str(self.getName()) + "= (orig=" + str(self.getOriginalValue()) + ")"

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        return "[DECIMALWORD]" + str(self.getName()) + "= (getValue=" + str(self.getValue(negative, vocabulary, memory)) + ")"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        localValue = self.getValue(negative, vocabulary, memory)
        # In case we can't compare with a known value, we compare only the possibility to learn it afterward
        if localValue is None or self.isMutable():
            self.log.debug("We compare the format (will we be able to learn it afterwards ?")
            return self.compareFormat(value, indice, negative, vocabulary, memory)
        else:
            (binVal, strVal) = localValue
            self.log.info("Compare received : '" + str(value[indice:]) + "' with '" + strVal + "' ")
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
        # First we retrieve the size of the value to memorize
        size = self.compare(value, indice, negative, vocabulary, memory)
        if size > 0:
            # memorize
            self.log.debug("Memorize : " + str(value[indice:size]))
            memory.memorize(self, (value[indice:size], TypeConvertor.bin2string(TypeConvertor.strBitarray2Bitarray(value[indice:size]))))
            return size
        else:
            self.log.debug("Incompatible for learning")
            return -1

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
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:DecimalWordVariable")

        # Original Value
        if self.getOriginalValue() is not None:
            xmlHexVariableOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlHexVariableOriginalValue.text = self.getOriginalValue()

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getCurrentValue(self):
        return self.currentValue

    def getOriginalValue(self):
        return self.originalValue

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Load a decimal word variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            xmlWordVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlWordVariableOriginalValue is not None:
                originalValue = xmlWordVariableOriginalValue.text
            else:
                originalValue = None

            return DecimalWordVariable(varId, varName, originalValue)
        return None
