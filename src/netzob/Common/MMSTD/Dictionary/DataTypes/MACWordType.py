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


class MACWordType(AbstractWordType):
    """MACWordType:
            A type represented by MAC address in 8-bits strings (0d:0d:0d:0d:0d:0d).
    """

    TYPE = "MAC Word"

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of MACWordType:
        """
        AbstractWordType.__init__(self, True, 17, 17, None)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.MACWordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def mutateValue(self, generationStrategies, value, mutationRate=10, deletionRate=5, additionRate=5):
        """mutateValue:
                We mutate only, we do not delete or add new characters, so deletionRate and additionRate are useless.
        """
        mutatedValue = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                for i in range(6):
                    value = value + "." + self.mutateRandomlyAString(string.hexdigits, self.bin2str(value), mutationRate, deletionRate=0, additionRate=0)
                value = value[1:]
                break
        return self.str2bin(mutatedValue)

    def generateFixedSizeValue(self, generationStrategies, charSize):
        """generateFixedSizeValue:
                charSize is not used, MAC addresses have always the same format.
        """
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                for i in range(6):
                    value = value + "." + self.generateRandomString(string.hexdigits, 2)
                value = value[1:]
                break
        return self.str2bin(value)

    def getType(self):
        return MACWordType.TYPE

    def suitsBinary(self, bina):
        byteset = bina.tobytes()
        stri = ''
        ip = ''
        for byte in byteset:
            # We naively try to decode in ascii the binary.
            try:
                stri = byte.decode('ascii')
                # We search if each character is in string.hexdigits or is a dot.
                if string.hexdigits.find(stri) == -1:
                    if stri != '.':
                        return False
                ip += stri
            except:
                return False
        spip = ip.split('.')
        # A MAC address is composed of six parts.
        if len(spip) != 6:
            return False

        # We search if the MAX is in hex format : a0.bb.0.8f.54.a0
        for i in range(len(spip)):
            # Each term cannot exceed 2 characters.
            if len(spip[i]) > 2:
                return False
        return True

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractWordType                                 |
#+---------------------------------------------------------------------------+
    def getMaxBitSize(self, nbChars):
        return (17 * 8)

    def getMinBitSize(self, nbChars):
        return (17 * 8)
