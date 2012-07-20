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
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.MMSTD.Dictionary.Type.AbstractType import AbstractType


class AbstractWordType(AbstractType):
    """AbstractWordType:
            A type represented by printable 8-bits strings.
    """

    def __init__(self):
        """Constructor of AbstractWordType:
        """
        AbstractType.__init__(self)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Type.AbstractWordType.py')

    def generateRandomString(self, stringType, minSize, maxSize):
        """generateRandomString:
                Generate a random string of the given size withen the given min and max size.

                @type stringType: integer
                @param stringType: a string type as string.digits, string.letters, string.printable...
                @type minSize: integer
                @param minSize: the minimum size of the generated string.
                @type maxSize: integer
                @param maxSize: the maximum size of the generated string.
                @rtype: string
                @return: the randomly generated string.
        """
        size = random.randint(minSize, maxSize)
        value = ""
        for i in range(size):
            value = value + random.choice(stringType)
        return value

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractType                                     |
#+---------------------------------------------------------------------------+
    def type2bin(self, typeValue):
        if typeValue is not None:
            return TypeConvertor.string2bin(typeValue)
        else:
            return None

    def getBitSize(self, typeValue):
        return (len(typeValue) * 8)

    def getMaxBitSize(self, nbChars):
        return (nbChars * 8)

    def getMinBitSize(self, nbChars):
        return (nbChars * 8)
