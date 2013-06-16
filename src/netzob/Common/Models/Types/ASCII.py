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
import struct

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType


class ASCII(AbstractType):

    def __init__(self, value=None, size=(None, None)):
        super(ASCII, self).__init__(self.__class__.__name__, value, size)

    def buildDataRepresentation(self):
        """Overwrite :class:`netzob.Common.Models.Types.AbstractType.AbstractType`"""

        minSize, maxSize = self.size
        if minSize is not None:
            minSize = minSize * 8
        if maxSize is not None:
            maxSize = maxSize * 8
        bitSize = (minSize, maxSize)
        from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data import Data
        return Data(dataType=ASCII, originalValue=self.value, size=bitSize)

    @staticmethod
    def canParse(data):
        """This method returns True if data is an ASCII

        >>> from netzob import *
        >>> ASCII.canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        The ascii table is defined from 0 to 127:
        >>> ASCII.canParse(TypeConverter.convert(128, Decimal, Raw, src_sign=AbstractType.SIGN_UNSIGNED))
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as an ASCII
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        for byte in data:
            # We naively try to decode in ascii the binary.
            try:
                byte.decode('ascii')
            except:
                return False
        return True

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob import *
        >>> ASCII.decode("hello")
        'hello'
        >>> ASCII.decode('\x5a\x6f\x62\x79\x20\x69\x73\x20\x64\x61\x20\x70\x6c\x61\x63\x65\x20\x21')
        'Zoby is da place !'
        >>> ASCII.decode(1021)
        '1021'

        :param data: the data encoded in ASCII which will be decoded in raw
        :type data: the current type
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        data = str(data)
        f = "{0}s".format(len(data))

        return struct.pack(f, data)

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the ASCII.

        >>> from netzob import *
        >>> raw = ASCII.decode("hello zoby!")
        >>> print ASCII.encode(raw)
        hello zoby!

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        return str(data)
