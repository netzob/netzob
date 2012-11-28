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
from netzob.Common.Type.Format import Format
import re


class IPv4Variable(Variable):
    """IPv4Variable:
            IPv4 variable defined in a dictionary.
    """

    def __init__(self, id, name, originalValue, startValue, endValue, format):
        """Constructor of IPv4Variable:

            @type originalValue: string
            @param originalValue: the original value of the variable, must be a "real" ip address declared in ASCII like : "192.168.0.10".
            @type startValue: string
            @param startValue: the first value of the IP range contained by the variable, must be a "real" ip address declared in ASCII like : "192.168.0.10"
            @type endValue: string
            @param endValue: the last value of the IP range contained by the variable, must be a "real" ip address declared in ASCII like : "192.168.0.10"
            @type format: string
            @param format: the format of the given IO, either "hex" or "ascii".
        """
        Variable.__init__(self, "IPv4Variable", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.IP4Variable.py')

        # Save initial informations
        self.format = format
        self.startValue = startValue
        self.endValue = endValue
        self.originalValue = originalValue

        # Set the current value
        self.computeCurrentValue(self.originalValue)

    def computeCurrentValue(self, strValue):
        """computeCurrentValue:
                Compute a couple of binary and string values for the current variable.

                @type strValue: string
                @param strValue: a string value proposed as default value for this variable, must be a "real" ip address declared in ASCII like : "192.168.0.10".
        """
        if strValue is not None:
            if self.format == Format.ASCII:
                strCurrentValue = str(strValue)
                binCurrentValue = TypeConvertor.string2bin(strValue, 'big')
            elif self.format == Format.HEX:
                hexVal = TypeConvertor.ipToNetzobRaw(strValue)
                if hexVal is not None:
                    strCurrentValue = str(strValue)
                    binCurrentValue = TypeConvertor.netzobRawToBitArray(hexVal)
                else:
                    strCurrentValue = str("None:Error")
                    binCurrentValue = None
            self.currentValue = (binCurrentValue, strCurrentValue)
        else:
            self.currentValue = None

    #+-----------------------------------------------------------------------+
    #| generateValue :
    #|     Generate a valid value for the variable
    #+-----------------------------------------------------------------------+
    def generateValue(self):
        """generateValue:
                Generate a valid value for the variable.
        """
        if self.format == Format.ASCII:

            ip1 = random.randint(0, 255)
            ip2 = random.randint(0, 255)
            ip3 = random.randint(0, 255)
            ip4 = random.randint(0, 255)

            generatedIP = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
            return generatedIP

        else:
            self.log.error("Error, the current variable (IPv4Variable) doesn't support function generateValue when its an HEX")
            raise NotImplementedError("The current variable doesn't support 'generateValue' when its an HEX.")

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
        if self.format == Format.ASCII:
            currentContent = TypeConvertor.bin2string(value[indice:])
            IPRegex = re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
            hasMatched = False
            for t in range(min(len(currentContent), 15), 7, -1):
                currentPossibleIP = currentContent[:t]
                result = IPRegex.match(currentPossibleIP)
                if result != None:
                    hasMatched = True
                elif hasMatched:
                    break

            if hasMatched:
                result = currentContent[:t + 2]
                self.log.debug("Compare on format was successfull : " + str(result))
                return len(TypeConvertor.string2bin(result, 'big'))
            else:
                self.log.debug("Compare on format was not successfull")
                return -1
        else:
            raise NotImplementedError("Error, the current variable (IPv4Variable) doesn't support function compareFormat in this case")

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
            self.log.debug("getValueToSend (getCurrentValue): " + str(self.getCurrentValue()))
            return self.getCurrentValue()

        if memory.hasMemorized(self):
            val = memory.recall(self)
            self.log.debug("getValueToSend (from memory) :" + str(val))
            self.currentValue = val
            return val

        # We generate a new value
        generatedValue = self.generateValue()
        self.log.debug("getValueToSend (generation of a value) : " + str(generatedValue))
        self.computeCurrentValue(generatedValue)

        # We save in memory the current value
        self.log.debug("getValueToSend (memorize)")
        memory.memorize(self, self.getCurrentValue())

        self.log.debug("getValueToSend : " + str(self.getCurrentValue()))
        # We return the newly generated and memorized value
        return self.getCurrentValue()

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.
        """
        return "IPv4Variable [getValue = " + str(self.getValue(negative, vocabulary, memory)) + "]"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return "IPv4Variable [originalValue = " + str(self.getOriginalValue()) + "]"

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Return the number of letters that matches, -1 if it does not match.
        """
        localValue = self.getValue(negative, vocabulary, memory)
        # In case we can't compare with a known value, we compare only the possibility to learn it afterward
        if localValue is None:
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

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.
                Return the number of letters that matches, -1 if it does not match.
        """
        if self.format == Format.ASCII:
            currentContent = TypeConvertor.bin2string(value[indice:])
            IPRegex = re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
            hasMatched = False
            for t in range(min(len(currentContent), 15), 7, -1):
                currentPossibleIP = currentContent[:t]
                result = IPRegex.match(currentPossibleIP)
                if result is not None:
                    hasMatched = True
                elif hasMatched:
                    break

            if hasMatched:
                result = currentContent[:t + 2]
                self.log.debug("Learn from received message : " + str(result))

                strCurrentValue = str(result)
                binCurrentValue = TypeConvertor.string2bin(result, 'big')
                memory.memorize(self, (binCurrentValue, strCurrentValue))

                return len(TypeConvertor.string2bin(result, 'big'))
            else:
                self.log.debug("Compare on format was not successfull")
                return -1
        else:
            raise NotImplementedError("Error, the current variable (IPv4Variable) doesn't support function compareFormat in this case")

    def restore(self, vocabulary, memory):
        """restore:
                Restore learned value from the last execution of the variable.
        """
        memory.restore(self)

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        xmlIPv4Variable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlIPv4Variable.set("id", str(self.getID()))
        xmlIPv4Variable.set("name", str(self.getName()))

        xmlIPv4Variable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:IPv4Variable")

        # Original Value
        if self.getOriginalValue() is not None:
            xmlIPVariableOriginalValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}originalValue")
            xmlIPVariableOriginalValue.text = str(self.getOriginalValue())

        # Starting Value
        xmlIPVariableStartValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}startValue")
        xmlIPVariableStartValue.text = str(self.getStartValue())

        # Ending Value
        xmlIPVariableEndValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}endValue")
        xmlIPVariableEndValue.text = str(self.getEndValue())

        # Format
        xmlIPVariableFormatValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}format")
        xmlIPVariableFormatValue.text = str(self.getFormat())

        return xmlIPv4Variable

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getCurrentValue(self):
        return self.currentValue

    def getOriginalValue(self):
        return self.originalValue

    def getStartValue(self):
        return self.startValue

    def getEndValue(self):
        return self.endValue

    def getFormat(self):
        return self.format

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Load an IPv4 variable from an XML definition.
        """
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            xmlIPVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlIPVariableOriginalValue is not None:
                originalValue = xmlIPVariableOriginalValue.text
            else:
                originalValue = None

            xmlIPVariableStartValue = xmlRoot.find("{" + namespace + "}startValue")
            startValue = xmlIPVariableStartValue.text

            xmlIPVariableEndValue = xmlRoot.find("{" + namespace + "}endValue")
            endValue = xmlIPVariableEndValue.text

            xmlIPVariablePaddingValue = xmlRoot.find("{" + namespace + "}format")
            format = str(xmlIPVariablePaddingValue.text)

            return IPv4Variable(varId, varName, originalValue, startValue, endValue, format)

        return None
