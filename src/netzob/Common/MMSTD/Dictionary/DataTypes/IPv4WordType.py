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
import string

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractWordType import AbstractWordType


class IPv4WordType(AbstractWordType):
    """IPv4WordType:
            A type represented by IPv4 formatted 8-bits strings (192.168.10.100 or 0d.0d.0d.0d).
    """

    TYPE = "IPv4 Word"

    def __init__(self, sized, minChars=0, maxChars=0, delimiter=None):
        """Constructor of IPv4WordType:
        """
        AbstractWordType.__init__(self, True, 7, 15, None)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Types.IPv4WordType.py')

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
                mutNumbers = value.split('.')
                # We mutate by term.
                for i in range(len(mutNumbers)):
                    # We mutate by character.
                    for j in range(len(mutNumbers[i])):
                        dice = random.randint(0, 100)
                        if dice < mutationRate:
                            # We want to make valid IP address, so between 0 and 255.
                            if len(mutNumbers[i]) == 3:  # The critic size of three characters: 100-255
                                if j == 0:
                                    mutNumbers[i][j] = str(random.randint(0, 2))
                                elif j == 1:
                                    if mutNumbers[i][0] == '2':  # term = 2.. <= 255
                                        mutNumbers[i][j] = str(random.randint(0, 5))
                                    else:
                                        mutNumbers[i][j] = str(random.randint(0, 9))
                                elif j == 2:
                                    if mutNumbers[i][0] == '2' and mutNumbers[i][1] == '5':  # term = 25. <= 255
                                        mutNumbers[i][j] = str(random.randint(0, 5))
                                    else:
                                        mutNumbers[i][j] = str(random.randint(0, 9))
                            else:
                                mutNumbers[i][j] = str(random.randint(0, 9))
                mutatedValue = ".".join(mutNumbers)  # We do not mutate dots.
                break
            elif generationStrategy == "random hex":
                for i in range(4):
                    value = value + "." + self.mutateRandomlyAString(string.hexdigits, value, mutationRate, deletionRate, additionRate)
                value = value[1:]
        return self.str2bin(mutatedValue)

    def generateFixedSizeValue(self, generationStrategies, charSize):
        """generateFixedSizeValue:
                charSize is not used, IPv4 addresses have always the same format.
        """
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                for i in range(4):
                    value = value + "." + str(random.randint(0, 255))
                value = value[1:]
                break
            elif generationStrategy == "random hex":
                for i in range(4):
                    value = value + "." + self.generateRandomString(string.hexdigits, 2)
                value = value[1:]
                break
        return self.str2bin(value)

    def getType(self):
        return IPv4WordType.TYPE

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
        # An ipv4 is composed of four parts.
        if len(spip) != 4:
            return False

        # We search if the ip is in decimal format : 128.215.0.16
        decimalIP = True
        for i in range(len(spip)):
            # Each term cannot exceed 3 characters.
            if len(spip[i]) > 3:
                decimalIP = False
                break
            # Each term can contain only decimal characters.
            for char in spip[i]:
                if string.digits.find(char) == -1:
                    decimalIP = False
                    break
            # Can be seen as a second check.
            try:
                intspip = int(spip[i])
            except:
                decimalIP = False
                break
            # These terms can not exceed 255.
            if intspip > 255:
                decimalIP = False
                break

        # We search if the ip is in hex format : a0.bb.0.8f
        hexIP = True
        for i in range(len(spip)):
            # Each term cannot exceed 2 characters.
            if len(spip[i]) > 2:
                hexIP = False
                break
        return hexIP or decimalIP

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractWordType                                 |
#+---------------------------------------------------------------------------+
    def getMaxBitSize(self, nbChars):
        return (15 * 8)  # 100.100.100.100

    def getMinBitSize(self, nbChars):
        return (7 * 8)  # 1.1.1.1
