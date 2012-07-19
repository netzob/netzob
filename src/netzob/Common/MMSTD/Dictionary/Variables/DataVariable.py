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

    def __init__(self, id, name, type, originalValue, minChar, maxChar):
        """Constructor of DataVariable:

                @type type: string
                @param typeVariable: the type of the variable being constructed.
                @type originalValue: linked to type.
                @param originalValue: the original value of the variable.
                @type minChar: integer
                @param minChar: the minimum number of elementary character the value of this variable can have.
                @type maxChar: integer
                @param maxChar: the maximum number of elementary character the value of this variable can have.
        """
        AbstractLeafVariable.__init__(self, id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.DataVariable.py')
        self.type = type
        self.originalValue = self.type.type2bin(originalValue)
        self.currentValue = None
        self.minBits = minChar * type.getAtomicSize()
        self.maxBits = minChar * type.getAtomicSize()

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def learn(self, readingToken):
        self.log.debug(_("Variable {0} learn {1} (if their format are compatible) starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        tmp = readingToken.getValue()[readingToken.getIndex():]
        if len(tmp) >= self.minBits:
            if len(tmp) >= self.maxBits:
                self.currentValue = tmp[:self.maxBits]
                readingToken.incrementIndex(self.maxBits)
            else:
                self.currentValue = tmp
                readingToken.incrementIndex(len(tmp))
            self.log.info(_("Format comparison successful."))
        else:
            self.log.info(_("Format comparison failed."))
            readingToken.setOk(False)

    def compare(self, readingToken):
        self.log.debug(_("Variable {0} compare its current value to {1} starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        localValue = self.getValue(readingToken)
        tmp = readingToken.getValue()[readingToken.getIndex():]
        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self.log.info(_("Comparison successful."))
                readingToken.incrementIndex(len(localValue))
                break
        self.log.info(_("Comparison failed."))
        readingToken.setOk(False)

    def generate(self, writingToken):
        self.log.debug(_("Variable {0} generate a value.").format(self.getName()))
        self.currentValue = self.getType().generateValue(writingToken.getGenerationStrategy(), self.minBits / self.getType().getAtomicSize(), self.maxBits / self.getType().getAtomicSize())

    def getValue(self, writingToken):
        self.log.debug(_("Variable {0} get its value.").format(self.getName()))
        if self.currentValue is not None:
            value = self.currentValue
        else:
            value = writingToken.getMemory().recall(self)
        writingToken.setValue(value)

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getOriginalValue(self):
        return originalValue

    def getCurrentValue(self):
        return currentValue

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue
