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
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Types.AbstractType import AbstractType


class IntegerType(AbstractType):
    """IntegerType:
            A type represented by numbers (integers).
    """

    TYPE = "Integer"

    def __init__(self):
        """Constructor of IntegerType:
        """
        AbstractType.__init__(self)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.IntegerType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def generateValue(self, generationStrategies, minSize, maxSize):
        value = 0
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                value = random.randint(10 ** (minSize - 1), (10 ** maxSize) - 1)
                break
        return self.str2bin(value)

    def str2bin(self, stri):
        if stri is not None:
            bina = bitarray(bin(stri)[2:])
            return bina
        else:
            return None

    def bin2str(self, bina):
        if bina is not None:
            return str(int(bina.to01(), 2))  # Transform from a base 2 to a base 10 integer and then translate it in string.
        else:
            return None

    def getBitSize(self, typeValue):
        return typeValue.bit_length()

    def getMaxBitSize(self, nbChars):
        return self.getBitSize((10 ** nbChars) - 1)

    def getMinBitSize(self, nbChars):
        return self.getBitSize(10 ** (nbChars - 1))

    def getType(self):
        return IntegerType.TYPE

    def suitsBinary(self, bina):
        return True
