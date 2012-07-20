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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Type.AbstractWordType import AbstractWordType


class IPv4WordType(AbstractWordType):
    """IPv4WordType:
            A type represented by IPv4 formatted 8-bits strings (192.168.10.100).
    """

    def __init__(self):
        """Constructor of IPv4WordType:
        """
        AbstractWordType.__init__(self, 7 * 8)  # Atomic size = 11 bytes * 8 bits.
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.IPv4WordType.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def generateValue(self, generationStrategy, minSize, maxSize):
        # minSize and maxSize are not used.
        value = ""
        if generationStrategy == "random integer":
            for i in range(4):
                value = value + "." + str(random.randint(0, 255))
            value = value[1:]
        elif generationStrategy == "random hex":
            for i in range(4):
                value = value + "." + self.generateRandomString(string.hexdigits, 2, 2)
            value = value[1:]
        return self.type2bin(value)
