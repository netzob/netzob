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
import logging
import string

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractWordType import \
    AbstractWordType
from netzob.Common.Type.TypeConvertor import TypeConvertor


class HexWordType(AbstractWordType):
    """HexWordType:
            A type represented by hexadecimal 8-bits strings.
    """

    TYPE = "Hex Word"

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of HexWordType:
        """
        AbstractWordType.__init__(self, sized, minChars, maxChars, delimiter)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.HexWordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def mutateValue(self, generationStrategies, value, mutationRate=10, deletionRate=5, additionRate=5):
        mutatedValue = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                mutatedValue = self.mutateRandomlyAString(string.hexdigits, self.bin2str(value), mutationRate, deletionRate, additionRate)
                break
        return self.str2bin(mutatedValue)

    def generateFixedSizeValue(self, generationStrategies, charSize):
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                value = self.generateRandomString(string.hexdigits, charSize)
                break
        return self.str2bin(value)

    def str2bin(self, stri):
        return TypeConvertor.hexstring2bin(stri)

    def bin2str(self, bina):
        return TypeConvertor.bin2hexstring(bina)

    def getBitSize(self, typeValue):
        return (len(typeValue) * 4)

    def getMaxBitSize(self, nbChars):
        return (nbChars * 4)

    def getMinBitSize(self, nbChars):
        return (nbChars * 4)

    def getType(self):
        return HexWordType.TYPE

    def suitsBinary(self, bina):
        # We naively try to decode in ascii the binary.
        try:
            str(hex(int(bina.to01(), 2)))
        except:
            return False
        return True
