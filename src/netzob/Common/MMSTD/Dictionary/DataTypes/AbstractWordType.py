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


class AbstractWordType(AbstractType):
    """AbstractWordType:
            A type represented by printable 8-bits strings.
    """

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of AbstractWordType:
        """
        AbstractType.__init__(self, sized, minChars, maxChars, delimiter)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.AbstractWordType.py')

    def generateRandomString(self, stringType, charSize):
        """generateRandomString:
                Generate a random string of the given size.

                @type stringType: integer
                @param stringType: a string type as string.digits, string.letters, string.printable...
                @type charSize: integer
                @param charSize: the size of the generated string.
                @rtype: string
                @return: the randomly generated string.
        """
        value = ""
        for i in range(charSize):
            value = value + random.choice(stringType)
        return value

    def mutateRandomlyAString(self, stringType, value, mutationRate, deletionRate, additionRate):
        """mutateRandomlyAString:
                Mutate the given string value according to the generationStrategy specification.

                @type generationStrategies: string List
                @param generationStrategies: a list of strategy ("random" for instance) that defines the way the value will be generated. The first allowed strategy is used.
                @type value: string
                @param value: the value before mutation.
                @rtype: string
                @return: the value after mutation.
        """
        mutatedValue = value

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
                mutatedValue[i] = random.choice(stringType)

        # Third pass : adding characters.
        lgth = len(mutatedValue)
        for i in range(lgth):
            dice = random.randint(0, 100)
            if dice < additionRate:
                mutatedValue = mutatedValue[:i] + random.choice(stringType) + mutatedValue[i:]
        return mutatedValue

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def str2bin(self, stri):
        return TypeConvertor.stringB2bin(stri)

    def bin2str(self, bina):
        return TypeConvertor.binB2string(bina)

    def getBitSize(self, typeValue):
        return (len(typeValue) * 8)

    def getMaxBitSize(self, nbChars):
        return (nbChars * 8)

    def getMinBitSize(self, nbChars):
        return (nbChars * 8)
