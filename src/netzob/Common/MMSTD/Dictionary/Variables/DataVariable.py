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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AbstractLeafVariable import AbstractLeafVariable


class DataVariable(AbstractLeafVariable):
    """DataVariable:
            A data variable defined in a dictionary which is a leaf in the global variable tree and contains data of a certain type.
    """

    MAX_BITS = 1024

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
        self.setCurrentValue(originalValue)

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def forget(self, processingToken):
        """forget:
                The variable forgets its value.
        """
        self.log.debug(_("The value of variable {0} is forgotten.").format(self.getName()))
        processingToken.getMemory().forget(self)  # We remove the memorized value.
        self.setCurrentValue(None)  # We remove the local value.

    def recall(self, processingToken):
        """recall:
                The variable recall its memorized value.
        """
        self.log.debug(_("The value of variable {0} is recalled.").format(self.getName()))
        self.setCurrentValue(processingToken.getMemory().recall(self))

    def memorize(self, processingToken):
        """memorize:
                The variable memorizes its value.
        """
        self.log.debug(_("The value of variable {0} is memorized.").format(self.getName()))
        processingToken.getMemory().memorize(self)

    def learn(self, readingToken):
        """learn:
                The variable checks if its format complies with the read value's format. If it matches, the variable learns, else it returns NOk.
        """
        self.log.debug(_("Variable {0} learns {1} (if their format are compatible) starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
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

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.
        """
        self.log.debug(_("Variable {0} compares its current value to {1} starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
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
                    break
            self.log.debug(_("Comparison failed."))
            readingToken.setOk(False)

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug(_("Variable {0} generates a value.").format(self.getName()))
        self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))

    def getValue(self, writingToken):
        """getValue:
                Returns the variable value if it has one, else it returns the memorized value.
        """
        self.log.debug(_("Variable {0} gets its value.").format(self.getName()))
        if self.getCurrentValue() is not None:
            value = self.getCurrentValue()
        else:
            value = writingToken.getMemory().recall(self)
        writingToken.appendValue(value)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:DataVariable")

        # originalValue (can be None)
        if self.originalValue is not None:
            xmlOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlOriginalValue.text = self.originalValue

        # minBits
        xmlMinBits = etree.SubElement(xmlVariable, "{" + namespace + "}minBits")
        xmlMinBits.text = self.minBits

        # maxBits
        xmlMaxBits = etree.SubElement(xmlVariable, "{" + namespace + "}maxBits")
        xmlMaxBits.text = self.maxBits

        # type
        xmlType = etree.SubElement(xmlVariable, "{" + namespace + "}type")
        xmlType.text = self.type.toString()

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getOriginalValue(self):
        return self.originalValue

    def getCurrentValue(self):
        if self.isRandom():
            self.setCurrentValue(self.getType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))
        return self.currentValue

    def setType(self, type):
        if type is not None:
            self.type = type
        else:
            # Default type is Binary.
            log.debug(_("Construction of DataVariable: type undefined."))
            from netzob.Common.MMSTD.Dictionary.Type.BinaryType import BinaryType
            type = BinaryType()

    def setNumberBitsAndNumberChars(self, minChars, maxChars):
        if minChars is not None and minChars >= 0:
            self.minBits = self.type.getMinBitSize(minChars)
            self.minChars = minChars
        else:
            log.debug(_("Construction of DataVariable: minChars undefined or < 0. MinBits value is fixed to 0."))
            self.minBits = 0
            self.minChars = 0
        if maxChars is not None and maxChars >= minChars:
            self.maxBits = self.type.getMaxBitSize(maxChars)
            self.maxChars = maxChars
        else:
            log.debug(_("Construction of DataVariable: maxChars undefined or < minChars. MaxBits value is fixed to minBits."))
            self.maxBits = self.minBits
            self.maxChars = self.minChars

    def setOriginalValue(self, originalValue):
        if originalValue is not None:
            size = self.type.getBitSize(originalValue)
            if size >= self.minBits and size <= self.maxBits:
                self.originalValue = self.type.type2bin(originalValue)
            else:
                self.originalValue = None
                self.debug(_("The given original value has an inappropriate size."))
        else:
            self.debug(_("The given original value is None."))

    def setCurrentValue(self, currentValue):
        valueSet = False
        if currentValue is not None:
            size = self.type.getBitSize(currentValue)
            if size >= self.minBits and size <= self.maxBits:
                self.currentValue = self.type.type2bin(currentValue)
                self.setDefined(True)
                valueSet = True
            else:
                self.debug(_("The given current value has an inappropriate size."))
        else:
            self.debug(_("The given current value is None."))
        if not valueSet:
            self.currentValue = None
            self.setDefined(False)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a data variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")

            # originalValue
            xmlOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlOriginalValue is not None:
                originalValue = xmlOriginalValue.text
            else:
                originalValue = None

            # minBits
            xmlMinBits = xmlRoot.find("{" + namespace + "}minBits")
            if xmlMinBits is not None:
                minBits = int(xmlMinBits.text)
            else:
                minBits = 0

            # maxBits
            xmlMaxBits = xmlRoot.find("{" + namespace + "}maxBits")
            if xmlMaxBits is not None:
                maxBits = int(xmlMaxBits.text)
            else:
                maxBits = MAX_BITS

            # type
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                type = AbstractType.makeType(xmlType.text)
                if type is None:
                    return None
            else:
                log.error(_("No type specified for this variable in the xml file."))
                return None

            return DataVariable(id, name, originalValue, type, minBits, maxBits)
        return None
