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
from netzob.Common.MMSTD.Dictionary.AbstractLeafVariable import AbstractLeafVariable


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
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.DataVariable.py')
        self.type = type
        self.originalValue = self.type.type2bin(originalValue)
        self.currentValue = None
        self.minBits = minChar * type.getAtomicSize()
        self.maxBits = minChar * type.getAtomicSize()

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, vmt):
        self.log.debug(_("Variable {0} learn {1} (if their format are compatible) starting at {2}.").format(self.getName(), str(value), str(indice)))

        tmp = value[indice:]
        if len(tmp) >= self.minBits:
            if len(tmp) >= self.maxBits:
                self.currentValue = tmp[:self.maxBits]
                vmt.addEatenBits(self.maxBits)
            else:
                self.currentValue = tmp
                vmt.addEatenBits(len(tmp))
            self.log.info(_("Format comparison successful."))
        else:
            self.log.info(_("Format comparison failed."))
            vmt.setOk(False)

    def compare(self, value, indice, negative, vocabulary, memory, vmt):
        self.log.debug(_("Variable {0} compare its current value to {1} starting at {2}.").format(self.getName(), str(value), str(indice)))

        localValue = self.getValue(negative, vocabulary, memory)
        if localValue is not None:
            (binVal, strVal) = localValue
            tmp = value[indice:]
            if len(tmp) >= len(binVal):
                if tmp[:len(binVal)] == binVal:
                    self.log.info(_("Comparison successful."))
                    vmt.addEatenBits(len(binVal))
                    break
        self.log.info(_("Comparison failed."))
        vmt.setOk(False)

    def generate(self, negative, vocabulary, generationStrategy):
        self.log.debug(_("Variable {0} generate a value.").format(self.getName()))

        self.currentValue = self.getType().generateValue(generationStrategy, self.minBits / self.getType().getAtomicSize(), self.maxBits / self.getType().getAtomicSize())

    def getValue(self, negative, vocabulary, memory):
        self.log.debug(_("Variable {0} get its value.").format(self.getName()))

        if self.currentValue is not None:
            return self.currentValue
        else:
            return memory.recall(self)

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
