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
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractWordType import AbstractWordType


class WordType(AbstractWordType):
    """WordType:
            A type represented by printable 8-bits strings.
    """

    TYPE = "Word"

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of WordType:
        """
        AbstractWordType.__init__(self, sized, minChars, maxChars, delimiter)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.WordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def mutateValue(self, generationStrategies, value, mutationRate=10, deletionRate=5, additionRate=5):
        mutatedValue = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                mutatedValue = self.mutateRandomlyAString(string.printable, self.bin2str(value), mutationRate, deletionRate, additionRate)
                break
        return self.str2bin(mutatedValue)

    def generateFixedSizeValue(self, generationStrategies, charSize):
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                value = self.generateRandomString(string.printable, charSize)
                break
        return self.str2bin(value)

    def getType(self):
        return WordType.TYPE

    def suitsBinary(self, bina):
        byteset = bina.tobytes()
        for byte in byteset:
            # We naively try to decode in ascii the binary.
            try:
                byte.decode('ascii')
            except:
                return False
        return True
