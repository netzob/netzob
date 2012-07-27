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
from netzob.Common.MMSTD.Dictionary.Types.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractLeafVariable import \
    AbstractLeafVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class DataVariable(AbstractLeafVariable):
    """DataVariable:
            A data variable defined in a dictionary which is a leaf in the global variable tree and contains data of a certain type.
    """

    MAX_BITS = 1024
    TYPE = "Data Variable"

    def __init__(self, id, name, mutable, random, type, originalValue, minChars, maxChars):
        """Constructor of DataVariable:
                Most of type are checked to not be None.

                @type type: string
                @param typeVariable: the type of the variable being constructed.
                @type originalValue: linked to type.
                @param originalValue: the original value of the variable.
                @type minChars: integer
                @param minChars: the minimum number of elementary character the value of this variable can have.
                @type maxChars: integer
                @param maxChars: the maximum number of elementary character the value of this variable can have.
        """
        AbstractLeafVariable.__init__(self, id, name, mutable, random)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.DataVariable.py')
        self.setType(type)
        self.setNumberBitsAndNumberChars(minChars, maxChars)
        self.setOriginalValue(originalValue)
        self.currentValue = self.originalValue

    def toString(self):
        """toString:
                For debugging purpose.
        """
        return _("[Data] {0}, type: {1}, bits: ({2}, {3}), chars: ({4}, {5}), original value: {6}").format(AbstractVariable.toString(self), self.type.getType(), str(self.minBits), str(self.maxBits), str(self.minChars), str(self.maxChars), str(self.bin2str(self.originalValue)))

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
        return self.type.bin2str(bina)

    def getVariableType(self):
        """getVariableType:
        """
        return DataVariable.TYPE

    def getDescription(self, writingToken):
        """getDescription:
                Get the full description of the variable.
        """
        return _("{0}, value: {1}").format(self.toString(), self.getValue(writingToken))

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return self.toString()

    def forget(self, processingToken):
        """forget:
                The variable forgets its value.
        """
        self.log.debug(_("- {0}: value is forgotten.").format(self.toString()))
        processingToken.getMemory().forget(self)  # We remove the memorized value.
        self.setCurrentValue(None)  # We remove the local value.

    def recall(self, processingToken):
        """recall:
                The variable recall its memorized value.
        """
        self.log.debug(_("- {0}: value is recalled.").format(self.toString()))
        self.setCurrentValue(processingToken.getMemory().recall(self))

    def memorize(self, processingToken):
        """memorize:
                The variable memorizes its value.
        """
        self.log.debug(_("- {0}: value is memorized.").format(self.toString()))
        processingToken.getMemory().memorize(self)

    def learn(self, readingToken):
        """learn:
                The variable checks if its format complies with the read value's format.
                If it matches, the variable learns, else it returns NOk.
        """
        self.log.debug(_("-[ {0}: learn.").format(self.toString()))
        tmp = readingToken.getValue()[readingToken.getIndex():]
        if len(tmp) >= self.minBits:
            if len(tmp) <= self.maxBits:
                self.setCurrentValue(tmp[:self.maxBits])
                readingToken.incrementIndex(self.maxBits)
            else:
                self.setCurrentValue(tmp)
                readingToken.incrementIndex(len(tmp))
            self.log.info(_("Format comparison successful."))
            self.setDefined(True)
        else:
            self.log.info(_("Format comparison failed."))
            readingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]-").format(self.getName(), readingToken.toString()))

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.
        """
        self.log.debug(_("-[ {0}: compare.").format(self.toString()))
        if self.random:
            # A random variable's value can not be compared to a static value.
            self.log.debug(_("Variable is random."))
            readingToken.setOk(False)
        else:
            localValue = self.getValue(readingToken)
            tmp = readingToken.getValue()[readingToken.getIndex():]
            if len(tmp) >= len(localValue):
                if tmp[:len(localValue)] == localValue:
                    self.log.debug(_("Comparison successful."))
                    readingToken.incrementIndex(len(localValue))
                else:
                    self.log.debug(_("Comparison failed."))
            else:
                self.log.debug(_("Comparison failed."))
            readingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]-").format(self.getName(), readingToken.toString()))

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug(_("-[ {0}: generate.").format(self.toString()))
        self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))

    def getValue(self, writingToken):
        """getValue:
                Returns the variable value if it has one, else it returns the memorized value.
        """
        self.log.debug(_("-[ {0}: getValue.").format(self.toString()))
        if self.isRandom():
            self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))
        if self.getCurrentValue() is not None:
            value = self.getCurrentValue()
        else:
            value = writingToken.getMemory().recall(self)
        writingToken.appendValue(value)
        self.log.debug(_("Variable {0}: {1}. ]-").format(self.getName(), writingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
        """
        self.log.debug(_("- {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:DataVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("random", str(self.isRandom()))

        # type
        xmlType = etree.SubElement(xmlVariable, "{" + namespace + "}type")
        xmlType.text = self.type.getType()

        # originalValue (can be None)
        if self.originalValue is not None:
            xmlOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlOriginalValue.text = self.type.bin2str(self.originalValue)

        # minBits
        xmlMinBits = etree.SubElement(xmlVariable, "{" + namespace + "}minChars")
        xmlMinBits.text = str(self.minBits)

        # maxBits
        xmlMaxBits = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxBits.text = str(self.maxBits)

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getOriginalValue(self):
        return self.originalValue

    def getCurrentValue(self):
        return self.currentValue

    def getMinChars(self):
        return self.minChars

    def getMaxChars(self):
        return self.maxChars

    def setType(self, type):
        if type is not None:
            self.type = type
        else:
            # Default type is Binary.
            self.log.info(_("Variable {0} (Data): type undefined.").format(self.getName()))
            from netzob.Common.MMSTD.Dictionary.Types.BinaryType import BinaryType
            self.type = BinaryType()

    def setNumberBitsAndNumberChars(self, minChars, maxChars):
        if minChars is not None and minChars >= 0:
            self.minBits = self.type.getMinBitSize(minChars)
            self.minChars = minChars
        else:
            self.log.info(_("Variable {0} (Data): minChars undefined or < 0. MinBits value is fixed to 0.").format(self.getName()))
            self.minBits = 0
            self.minChars = 0
        if maxChars is not None and maxChars >= minChars:
            self.maxBits = self.type.getMaxBitSize(maxChars)
            self.maxChars = maxChars
        else:
            self.log.info(_("Variable {0} (Data): maxChars undefined or < minChars. MaxBits value is fixed to minBits.").format(self.getName()))
            self.maxBits = self.minBits
            self.maxChars = self.minChars

    def setOriginalValue(self, originalValue):
        if originalValue is not None:
            size = self.type.getBitSize(originalValue)
            if size >= self.minBits and size <= self.maxBits:
                self.originalValue = self.type.str2bin(originalValue)
            else:
                self.originalValue = None
                self.log.info(_("Variable {0} (Data): The given original value has an inappropriate size.").format(self.getName()))
        else:
            self.log.info(_("Variable {0} (Data): The given original value is None.").format(self.getName()))

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a data variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        logging.debug(_("[ DataVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlRandom = xmlRoot.get("random") == "True"

            # type
            type = None
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                type = AbstractType.makeType(xmlType.text)
                if type is None:
                    return None
            else:
                logging.error(_("No type specified for this variable in the xml file."))
                return None

            # originalValue
            xmlOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlOriginalValue is not None:
                originalValue = xmlOriginalValue.text
            else:
                originalValue = None

            # minChars
            xmlMinChars = xmlRoot.find("{" + namespace + "}minChars")
            if xmlMinChars is not None:
                minChars = int(xmlMinChars.text)
            else:
                minChars = 0

            # maxChars
            xmlMaxChars = xmlRoot.find("{" + namespace + "}maxChars")
            if xmlMaxChars is not None:
                maxChars = int(xmlMaxChars.text)
            else:
                maxChars = DataVariable.MAX_BITS

            result = DataVariable(xmlID, xmlName, xmlMutable, xmlRandom, type, originalValue, minChars, maxChars)
            logging.debug(_("DataVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("DataVariable: loadFromXML fails"))
        return None
