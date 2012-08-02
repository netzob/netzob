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
import string

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Types.AbstractWordType import \
    AbstractWordType


class HexWordType(AbstractWordType):
    """HexWordType:
            A type represented by hexadecimal 8-bits strings.
    """

    TYPE = "Hex Word"

    def __init__(self):
        """Constructor of HexWordType:
        """
        AbstractWordType.__init__(self)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.HexWordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def str2bin(self, stri):
        if stri is not None:
            # bitarray(bin(int(stri, 16))[2:]) : remove (int) all left-sided useful '0's.*

            sbin = ''
            for char in stri:
                # We translate half-byte by half-byte.
                onecharbin = bin(int(char, 16))[2:]  # We translate a character into binary.
                for i in range(4 - len(onecharbin)):
                    sbin += '0'  # We prepend '0's to match the format: one hex char = 4 binary chars.
                sbin += onecharbin  # We append a new character's translation.
            return bitarray(sbin)
        else:
            return None

    def bin2str(self, bina):
        if bina is not None:
            # str(hex(int(bina.to01(), 2))) : remove (int) all left-sided useful '0's.

            sbin = bina.to01()  # We retrieve a string with the '0's and '1's of the binary.
            stri = ''
            for start in xrange(0, len(sbin), 4):
                # We translate half-byte by half-byte.
                stri += str(hex(int(sbin[start:start + 4], 2)))[2:]
            return stri
        else:
            return None

    def generateValue(self, generationStrategies, minSize, maxSize):
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                value = self.generateRandomString(string.hexdigits, minSize, maxSize)
                break
        return self.str2bin(value)

    def getType(self):
        return HexWordType.TYPE

    def suitsBinary(self, bina):
        byteset = bina.tobyte()
        stri = ''
        for byte in byteset:
            # We naively try to decode in ascii the binary.
            try:
                stri = byte.decode('ascii')
                # We search if each character is in string.hexdigits
                if string.hexdigits.find(stri) == -1:
                    return False
            except:
                return False
        return True
