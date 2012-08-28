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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractType import AbstractType
from netzob.Common.Type.TypeConvertor import TypeConvertor


class BinaryType(AbstractType):
    """BinaryType:
            A type represented by a bitarray.
    """

    TYPE = "Binary"

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of BinaryType:
        """
        AbstractType.__init__(self, sized, minChars, maxChars, delimiter)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.BinaryType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def mutateValue(self, generationStrategies, value, mutationRate=10, deletionRate=5, additionRate=5):
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                mutatedValue = self.bin2str(value)
                # First pass : deleting characters.
                lgth = len(mutatedValue)
                for i in range(lgth):
                    dice = random.randint(0, 100)
                    if dice < deletionRate:
                        mutatedValue = mutatedValue[:i] + mutatedValue[i + 1:]

                # Second pass : mutating characters.
                for i in range(len(mutatedValue)):
                    dice = random.randint(0, 100)
                    if dice < mutationRate:
                        if mutatedValue[i] == '0':  # Bit flip.
                            mutatedValue[i] = '1'
                        else:
                            mutatedValue[i] = '0'

                # Third pass : adding characters.
                lgth = len(mutatedValue)
                for i in range(lgth):
                    dice = random.randint(0, 100)
                    if dice < additionRate:
                        if random.randint(0, 1) == 1:
                            addedBit = '1'
                        else:
                            addedBit = '0'
                        mutatedValue = mutatedValue[:i] + addedBit + mutatedValue[i:]
                return self.str2bin(mutatedValue)
        return value  # Default case : we do not mutate.

    def generateFixedSizeValue(self, generationStrategies, charSize):
        value = []
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                for i in range(charSize):
                    if random.randint(0, 1) == 1:
                        value.append(True)
                    else:
                        value.append(False)
                break
        return self.str2bin(value)

    def str2bin(self, stri):
        return TypeConvertor.binstring2bin(stri)

    def bin2str(self, bina):
        return TypeConvertor.bin2binstring(bina)

    def getBitSize(self, typeValue):
        return len(typeValue)

    def getMaxBitSize(self, nbChars):
        return nbChars

    def getMinBitSize(self, nbChars):
        return nbChars

    def getType(self):
        return BinaryType.TYPE

    def suitsBinary(self, bina):
        return True
