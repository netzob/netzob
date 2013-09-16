#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType


class Raw(AbstractType):

    def __init__(self, value=None, size=None):
        super(Raw, self).__init__(self.__class__.__name__, value, size)

    def buildDataRepresentation(self):
        from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data import Data
        (minSize, maxSize) = self.size
        if minSize is not None:
            minSize = minSize * 8
        if maxSize is not None:
            maxSize = maxSize * 8
        return Data(dataType=Raw, originalValue=self.value, size=(minSize, maxSize))

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        return data

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        return data

    @staticmethod
    def canParse(data):
        """Computes if specified data can be parsed as raw which is always the case if the data
        is at leats 1 length.

        >>> from netzob.all import *
        >>> Raw.canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        The ascii table is defined from 0 to 127:
        >>> Raw.canParse(TypeConverter.convert(128, Decimal, Raw, src_sign=AbstractType.SIGN_UNSIGNED))
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        return True
