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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from bitarray import bitarray
from gettext import gettext as _
from lxml import etree
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractLeafVariable import \
    AbstractLeafVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.Type.TypeConvertor import TypeConvertor


class DataVariable(AbstractLeafVariable):
    """DataVariable:
            A data variable defined in a dictionary which is a leaf in the global variable tree and contains data of a certain type.
    """

    MAX_BITS = 1024
    TYPE = "Data Variable"

    def __init__(self, _id, name, mutable, learnable, _type, originalValue):
        """Constructor of DataVariable:
                Most of attribute are checked to not be None.

                @type type: string
                @param typeVariable: the type of the variable being constructed.
                @type originalValue: linked to type.
                @param originalValue: the original value of the variable.
        """
        AbstractLeafVariable.__init__(self, _id, name, mutable, learnable)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.DataVariable.py')
        self.setType(_type)
        self.setOriginalValue(originalValue)
        self.currentValue = self.originalValue

    def toString(self):
        """toString:
                For debugging purpose.
        """
        # We simply avoid to print unreadable binary.
        if self.type.getType() == BinaryType.TYPE:
            readableValue = TypeConvertor.bin2strhex(self.originalValue)
        else:
            readableValue = self.bin2str(self.originalValue)

        return "[Data] {0}, type: {1}, original value: {2}".format(AbstractVariable.toString(self), self.type.toString(), readableValue)

    def getValue(self, processingToken):
        """getValue:
                Return the current or memorized value.
        """
        if self.getCurrentValue() is not None:
            return self.getCurrentValue()
        else:
            return processingToken.getMemory().recall(self)

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def bin2str(self, bina):
        """bin2str:
                Transform a bitarray in a well-formatted string according to the type of the variable.

                @type bina: bitarray
                @param bina: a binary value.
                @rtype: string
                @return: a type-formatted string.
        """
        if bina is not None:
            return self.type.bin2str(bina)
        else:
            return None

    def getVariableType(self):
        """getVariableType:
        """
        return DataVariable.TYPE

    def getDescription(self, writingToken):
        """getDescription:
                Get the full description of the variable.
        """
        # We simply avoid to print unreadable binary.
        if self.type.getType() == BinaryType.TYPE:
            readableValue = TypeConvertor.bin2strhex(self.getValue(writingToken))
        else:
            readableValue = str(self.bin2str(self.getValue(writingToken)))

        return "{0}, value: {1}".format(self.toString(), readableValue)

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return self.toString()

    def isDefined(self, processingToken):
        """isDefined:
                If the leaf has no values, it is not defined.
        """
        return self.getValue(processingToken) is not None

    def getDictOfValues(self, processingToken):
        """getDictOfValues:
                Simply return a dict that contains the value associated to the ID of the variable.
        """
        dictOfValues = dict()
        dictOfValues[self.getID()] = self.getValue(processingToken)
        # self.log.debug("- Dict of values: {0}.".format(str(dictOfValues)))
        return dictOfValues

    def restore(self, processingToken):
        """restore:
        """
        self.log.debug("- {0}: memorized value is restored.".format(self.toString()))
        processingToken.getMemory().restore(self)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
        """
        self.log.debug("- {0}: toXML:".format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:DataVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # sized
        xmlSized = etree.SubElement(xmlVariable, "{" + namespace + "}sized")
        xmlSized.text = str(self.type.isSized())

        # type
        xmlType = etree.SubElement(xmlVariable, "{" + namespace + "}type")
        xmlType.text = self.type.getType()

        # originalValue (can be None)
        if self.originalValue is not None:
            xmlOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            # We memorize the current value as the future original value.
            # I assume that the user want the last current value (that he may have hand-edited) of the variable to be memorized.
            xmlOriginalValue.text = self.type.bin2str(self.currentValue)

        # minChars
        xmlMinChars = etree.SubElement(xmlVariable, "{" + namespace + "}minChars")
        xmlMinChars.text = str(self.type.getMinChars())

        # maxBits
        xmlMaxChars = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxChars.text = str(self.type.getMaxChars())

        # delimiter
        xmlDelimiter = etree.SubElement(xmlVariable, "{" + namespace + "}delimiter")
        xmlDelimiter.text = str(TypeConvertor.bin2hexstring(self.type.getDelimiter()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractLeafVariable                             |
#+---------------------------------------------------------------------------+
    def forget(self, processingToken):
        """forget:
                The variable forgets its value.
        """
        self.log.debug("- {0}: value is forgotten.".format(self.toString()))
        processingToken.getMemory().forget(self)  # We remove the memorized value.
        self.setCurrentValue(None)  # We remove the local value.

    def recall(self, processingToken):
        """recall:
                The variable recall its memorized value.
        """
        self.log.debug("- {0}: value is recalled.".format(self.toString()))
        self.setCurrentValue(processingToken.getMemory().recall(self))

    def memorize(self, processingToken):
        """memorize:
                The variable memorizes its value.
        """
        self.log.debug("- {0}: value is memorized.".format(self.toString()))
        processingToken.getMemory().memorize(self)

    def compareFormat(self, readingToken):
        """compareFormat:
                The variable checks if its format complies with the read value's format.
        """
        self.log.debug("- [ {0}: compareFormat.".format(self.toString()))

        self.type.compareFormat(readingToken)

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def learn(self, readingToken):
        """learn:
        """
        self.log.debug("- [ {0}: learn.".format(self.toString()))
        if readingToken.isOk():  # A format comparison had been executed before, its result must be "OK".
            tmp = readingToken.getValue()[readingToken.getIndex():]

            # If the type has a definite size.
            if self.type.isSized():
                maxBits = self.type.getMaxBits()
                # Length comparison. (len(tmp) >= minBits is implicit as the readingToken is OK.)
                if len(tmp) <= maxBits:
                    self.setCurrentValue(tmp)
                    readingToken.incrementIndex(len(tmp))

                else:  # len(tmp) > self.maxBits
                    # We learn as much as we can.
                    self.setCurrentValue(tmp[:maxBits])
                    readingToken.incrementIndex(maxBits)

            # If the type is delimited from 0 to a delimiter.
            else:
                endi = 0
                for i in range(len(tmp)):
                    if self.type.endsHere(tmp[i:]):
                        endi = i
                        break
                # We learn from the beginning to the delimiter.
                self.setCurrentValue(tmp[:endi + len(self.type.getDelimiter())])  # The delimiter token is a part of the variable.
                readingToken.incrementIndex(endi + len(self.type.getDelimiter()))

            self.log.info("Learning done.")
        else:
            self.log.info("Learning abort because the previous format comparison failed.")

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.
        """
        self.log.debug("- [ {0}: compare.".format(self.toString()))
        localValue = self.getValue(readingToken)
        tmp = readingToken.getValue()[readingToken.getIndex():]

        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self.log.debug("Comparison successful.")
                readingToken.incrementIndex(len(localValue))
                readingToken.setOk(True)
            else:
                readingToken.setOk(False)
                self.log.debug("Comparison failed: wrong value.")
        else:
            readingToken.setOk(False)
            self.log.debug("Comparison failed: wrong size.")
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def mutate(self, writingToken):
        """mutate:
                The current value is mutated according to the given generation strategy.
        """
        self.log.debug("- {0}: mutate.".format(self.toString()))
        self.setCurrentValue(self.type.mutateValue(writingToken.getGenerationStrategy(), self.getValue()))

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug("- {0}: generate.".format(self.toString()))
        self.setCurrentValue(self.type.generateValue(writingToken.getGenerationStrategy()))

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug("- [ {0}: writeValue.".format(self.toString()))
        value = bitarray()
        value.extend(self.getValue(writingToken))
        if not self.type.isSized():
            # Do not forget to write the delimiter if the variable has one
            value.extend(self.getType().getDelimiter())
        writingToken.write(self, value)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getOriginalValue(self):
        return self.originalValue

    def getCurrentValue(self):
        return self.currentValue

    def setType(self, _type):
        if type is not None:
            self.type = _type
        else:
            # Default type is Binary.
            self.log.info("Variable {0} (Data): type undefined.".format(self.getName()))
            self.type = BinaryType()

    def setOriginalValue(self, originalValue):
        if originalValue is not None:
            if self.type.isSized():
                size = self.type.getBitSize(originalValue)
                if size >= self.type.getMinBits() and size <= self.type.getMaxBits():
                    self.originalValue = self.type.str2bin(originalValue)
                else:
                    self.originalValue = None
                    self.log.info("Variable {0} (Data): The given original value has an inappropriate size.".format(self.getName()))
            else:
                self.originalValue = self.type.str2bin(originalValue)

        else:
            self.originalValue = None
            self.log.info("Variable {0} (Data): The given original value is None.".format(self.getName()))

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads a data variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        logging.debug("[ DataVariable: loadFromXML:")
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            # originalValue
            xmlOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlOriginalValue is not None and xmlOriginalValue.text != "None":
                originalValue = xmlOriginalValue.text
            else:
                originalValue = None

            # sized
            xmlSized = xmlRoot.find("{" + namespace + "}sized")
            if xmlSized is not None and xmlSized.text != "None":
                sized = xmlSized.text == 'True'
            else:
                sized = True

            # minChars
            xmlMinChars = xmlRoot.find("{" + namespace + "}minChars")
            if xmlMinChars is not None and xmlMinChars.text != "None":
                minChars = int(xmlMinChars.text)
            else:
                minChars = 0

            # maxChars
            xmlMaxChars = xmlRoot.find("{" + namespace + "}maxChars")
            if xmlMaxChars is not None and xmlMaxChars.text != "None":
                maxChars = int(xmlMaxChars.text)
            else:
                maxChars = minChars

            # delimiter
            xmlDelimiter = xmlRoot.find("{" + namespace + "}delimiter")
            if xmlDelimiter is not None and xmlDelimiter.text != "None":
                delimiter = xmlDelimiter.text
            else:
                delimiter = None

            # type
            _type = None
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                _type = AbstractType.makeType(xmlType.text, sized, minChars, maxChars, delimiter)
                if type is None:
                    return None
            else:
                logging.error("No type specified for this variable in the xml file.")
                return None

            result = DataVariable(xmlID, xmlName, xmlMutable, xmlLearnable, _type, originalValue)
            logging.debug("DataVariable: loadFromXML successes: {0} ]".format(result.toString()))
            return result
        logging.debug("DataVariable: loadFromXML fails")
        return None
