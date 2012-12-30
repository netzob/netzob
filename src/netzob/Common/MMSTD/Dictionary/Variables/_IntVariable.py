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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| IntVariable:
#|     Definition of an int variable defined in a dictionary
#+---------------------------------------------------------------------------+
class IntVariable(Variable):

    def __init__(self, id, name, size, value):
        Variable.__init__(self, id, name, "INT")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.value = value

        self.size = size
        self.min = -1
        self.max = -1
        self.reset = "normal"
        if self.value is not None:
            self.binValue = TypeConvertor.int2bin(self.value, self.size)
            self.strValue = TypeConvertor.int2string(self.value)
        else:
            self.binValue = None
            self.strValue = None

        self.binValueBeforeLearning = None
        self.strValueBeforeLearning = None

        self.log.debug("Bin-value = " + str(self.binValue) + ", str-value = " + str(self.strValue))

    def restore(self):
        self.log.debug("Restore ...")
        if self.binValueBeforeLearning is not None and self.strValueBeforeLearning is not None:
            self.log.debug("Restore the previsouly learned value")
            self.binValue = self.binValueBeforeLearning
            self.strValue = self.strValueBeforeLearning

    def getValue(self, negative, dictionary):
        return (self.binValue, self.strValue)

    def generateValue(self, negative, dictionary):
        self.log.debug("Generate value of hex")
        if self.min != -1 and self.max != -1:
            # generate a value in int
            r = random.randint(self.min, self.max)
            self.log.debug("Generating hex of value : " + str(r))
            self.binValue = TypeConvertor.int2bin(r, self.size)
            self.strValue = TypeConvertor.int2string(r)

    def learn(self, val, indice, isForced, dictionary):
        self.log.debug("Learn on " + str(indice) + " : " + str(val[indice:]))
        if self.binValue is not None and not isForced:
            self.log.debug("Won't learn the hex value (" + self.name + ") since it already has one is not forced to (return " + str(len(self.binValue)) + ")")
            return indice + len(self.binValue)

        tmp = val[indice:]
        self.log.debug("Learn hex given its size: " + str(self.size) + " from " + str(tmp))
        if len(tmp) >= self.size:

            self.binValueBeforeLearning = self.binValue
            self.strValueBeforeLearning = self.strValue

            self.binValue = val[indice:indice + self.size]
            self.strValue = str(TypeConvertor.bin2int(self.binValue))

            self.log.debug("learning value: " + str(self.binValue))
            self.log.debug("learning value: " + self.strValue)

            return indice + self.size
        else:
            return -1

    def setReset(self, reset):
        self.reset = reset

    def setSize(self, size):
        self.size = size

    def setMin(self, min):
        self.min = int(min)

    def setMax(self, max):
        self.max = int(max)
