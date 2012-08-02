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
from gettext import gettext as _
from lxml import etree
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Types.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.Types.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractLeafVariable import \
    AbstractLeafVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class DataVariable(AbstractLeafVariable):
    """DataVariable:
            A data variable defined in a dictionary which is a leaf in the global variable tree and contains data of a certain type.
    """

    MAX_BITS = 1024
    TYPE = "Data Variable"

    def __init__(self, _id, name, mutable, random, _type, originalValue, minChars, maxChars):
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
        AbstractLeafVariable.__init__(self, _id, name, mutable, random)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.DataVariable.py')
        self.setType(_type)
        self.setNumberBitsAndNumberChars(minChars, maxChars)
        self.setOriginalValue(originalValue)
        self.currentValue = self.originalValue

    def toString(self):
        """toString:
                For debugging purpose.
        """
        # We simply avoid to print unreadable binary.
        if self.getType().getType() == BinaryType.TYPE:
            readableValue = TypeConvertor.bin2strhex(self.originalValue)
        else:
            readableValue = self.bin2str(self.originalValue)

        return _("[Data] {0}, type: {1}, bits: ({2}, {3}), chars: ({4}, {5}), original value: {6}").format(AbstractVariable.toString(self), self.type.getType(), str(self.minBits), str(self.maxBits), str(self.minChars), str(self.maxChars), readableValue)

    def getValue(self, processingToken):
        """getValue:
                Return the current value if it has one, a memorized value in other cases.
                If the variable is random, its value is not modified each time (many) the getValue is called. It is modified when it has to be written.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
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
        if self.getType().getType() == BinaryType.TYPE:
            readableValue = TypeConvertor.bin2strhex(self.getValue(writingToken))
        else:
            readableValue = str(self.bin2str(self.getValue(writingToken)))

        return _("{0}, value: {1}").format(self.toString(), readableValue)

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).
        """
        return self.toString()

    def isDefined(self, processingToken):
        """isDefined:
                If the leaf is random or has no values, it is not defined.
        """
        return (not self.isRandom()) and self.getValue(processingToken) is not None

    def getDictOfValues(self, processingToken):
        """getDictOfValues:
                This function is called for saving the value of the variable.
        """
        # A random variable does not need to be saved.
        if self.isRandom():
            return dict()

        dictOfValues = dict()
        dictOfValues[self.getID()] = self.getValue(processingToken)
        # self.log.debug(_("- Dict of values: {0}.").format(str(dictOfValues)))
        return dictOfValues

    def restore(self, processingToken):
        """restore:
        """
        self.log.debug(_("- {0}: memorized value is restored.").format(self.toString()))
        processingToken.getMemory().restore(self)

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
            # We memorize the current value as the future original value.
            # I assume that the user want the last current value (that he may have hand-edited) of the variable to be memorized.
            xmlOriginalValue.text = self.type.bin2str(self.currentValue)

        # minChars
        xmlMinChars = etree.SubElement(xmlVariable, "{" + namespace + "}minChars")
        xmlMinChars.text = str(self.minChars)

        # maxBits
        xmlMaxChars = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxChars.text = str(self.maxChars)

#+---------------------------------------------------------------------------+
#| Visitor abstract subFunctions                                             |
#+---------------------------------------------------------------------------+
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
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))
        tmp = readingToken.getValue()[readingToken.getIndex():]
        # Length comparison.
        if len(tmp) >= self.minBits:
            if len(tmp) <= self.maxBits:
                # Format comparison.
                if self.type.suitsBinary(tmp[:self.maxBits]):
                    # We learn as much as we can.
                    self.setCurrentValue(tmp[:self.maxBits])
                    readingToken.incrementIndex(self.maxBits)
                    readingToken.setOk(True)
                    self.log.info(_("Format comparison successful."))
                else:
                    readingToken.setOk(False)
                    self.log.info(_("Format comparison failed: wrong format."))
            else:
                # Format comparison.
                if self.type.suitsBinary(tmp):
                    # We learn everything that last.
                    self.setCurrentValue(tmp)
                    readingToken.incrementIndex(len(tmp))
                    readingToken.setOk(True)
                    self.log.info(_("Format comparison successful."))
                else:
                    readingToken.setOk(False)
                    self.log.info(_("Format comparison failed: wrong format."))
        else:
            readingToken.setOk(False)
            self.log.info(_("Format comparison failed: wrong size."))
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.
        """
        self.log.debug(_("- [ {0}: compare.").format(self.toString()))
        if self.isRandom():
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
                    readingToken.setOk(True)
                else:
                    readingToken.setOk(False)
                    self.log.debug(_("Comparison failed: wrong value."))
            else:
                readingToken.setOk(False)
                self.log.debug(_("Comparison failed: wrong size."))
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug(_("-[ {0}: generate.").format(self.toString()))
        self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug(_("- [ {0}: writeValue.").format(self.toString()))
        if self.isRandom():
            self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))
        value = self.getValue(writingToken)
        writingToken.appendValue(value)
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

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

    def setType(self, _type):
        if type is not None:
            self.type = _type
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
            self.originalValue = None
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
            _type = None
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                _type = AbstractType.makeType(xmlType.text)
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

            result = DataVariable(xmlID, xmlName, xmlMutable, xmlRandom, _type, originalValue, minChars, maxChars)
            logging.debug(_("DataVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("DataVariable: loadFromXML fails"))
        return None
