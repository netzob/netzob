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
from gettext import gettext as _
import logging
import string

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Types.AbstractWordType import AbstractWordType


class MACWordType(AbstractWordType):
    """MACWordType:
            A type represented by MAC address in 8-bits strings (0d:0d:0d:0d:0d:0d).
    """

    def __init__(self):
        """Constructor of MACWordType:
        """
        AbstractWordType.__init__(self)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.MACWordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def generateValue(self, generationStrategies, minSize, maxSize):
        # minSize and maxSize are not used.
        value = ""
        for generationStrategy in generationStrategies:
            if generationStrategy == "random":
                for i in range(6):
                    value = value + "." + self.generateRandomString(string.hexdigits, 2, 2)
                value = value[1:]
                break
        return self.type2bin(value)

    def toString(self):
        return "MACWord"

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractWordType                                 |
#+---------------------------------------------------------------------------+
    def getMaxBitSize(self, nbChars):
        return (17 * 8)

    def getMinBitSize(self, nbChars):
        return (17 * 8)
