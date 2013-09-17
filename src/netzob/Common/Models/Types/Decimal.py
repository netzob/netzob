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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType


class Decimal(AbstractType):

    def __init__(self, value=None, size=None):
        super(Decimal, self).__init__(self.__class__.__name__, value, size)

    def buildDataRepresentation(self):
        from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data import Data
        from netzob.Common.Models.Types.TypeConverter import TypeConverter
        from netzob.Common.Models.Types.BitArray import BitArray
        (minSize, maxSize) = self.size
        if minSize is not None:
            minSize = minSize * 8
        if maxSize is not None:
            maxSize = maxSize * 8
        if self.value is not None:
            originalValue = TypeConverter.convert(self.value, Decimal, BitArray)
        else:
            originalValue = None

        return Data(dataType=Decimal, originalValue=originalValue, size=(minSize, maxSize))

    @staticmethod
    def canParse(data):
        """This method returns True if data is a Decimal.
        For the moment its always true because we consider
        the decimal type to be very similar to the raw type.

        >>> from netzob.all import *
        >>> Decimal.canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data is can be parsed as a Decimal
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        return True

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> print Decimal.decode(23)
        \x17

        >>> print Decimal.decode(-1, sign=AbstractType.SIGN_UNSIGNED)
        Traceback (most recent call last):
        ...
        error: ubyte format requires 0 <= number <= 255

        >>> print Decimal.decode(-1, sign=AbstractType.SIGN_SIGNED)
        \xff

        >>> print Decimal.decode(2000000000000000)
        Traceback (most recent call last):
        ...
        error: byte format requires -128 <= number <= 127

        >>> print Decimal.decode(2000000000000000, unitSize=AbstractType.UNITSIZE_64)
        \x00\x00\x8dI\xfd\x1a\x07\x00

        >>> print Decimal.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
        \x19\x00
        >>> print Decimal.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG)
        \x00\x19

        :param data: the data encoded in Decimal which will be decoded in raw
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

        f = Decimal.computeFormat(unitSize, endianness, sign)
        return struct.pack(f, int(data))

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the Decimal.

        >>> from netzob.all import *

        >>> raw = Decimal.decode(23)
        >>> print Decimal.encode(raw)
        23

        >>> raw = Decimal.decode(1200, unitSize=AbstractType.UNITSIZE_16)
        >>> print Decimal.encode(raw, unitSize=AbstractType.UNITSIZE_16)
        1200

        >>> raw = Decimal.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
        >>> print repr(Decimal.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG))
        6400
        >>> print repr(Decimal.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE))
        25

        >>> print Decimal.encode('\xcc\xac\x9c\x0c\x1c\xacL\x1c,\xac', unitSize=AbstractType.UNITSIZE_8)
        -395865088909314208584756

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

        perWordFormat = Decimal.computeFormat(unitSize, endianness, sign)

        nbWords = (len(data) * 8 / int(unitSize))

        finalValue = 0

        iWord = 0
        start = 0
        end = nbWords
        inc = 1
        if endianness == AbstractType.ENDIAN_BIG:
            end = 0
            start = nbWords
            inc = -1

        for i in range(start, end, inc):
            # Extract the portion that represents the current word
            startPos = iWord * int(unitSize) / 8
            endPos = iWord * int(unitSize) / 8 + int(unitSize) / 8

            wordData = data[startPos:endPos]
            unpackedWord = struct.unpack(perWordFormat, wordData)[0]

            unpackedWord = unpackedWord << int(unitSize) * iWord
            finalValue = finalValue + unpackedWord

            iWord += 1

        return finalValue

    @staticmethod
    def computeFormat(unitSize, endianness, sign):
        # endian
        if endianness == AbstractType.ENDIAN_BIG:
            endianFormat = '>'
        elif endianness == AbstractType.ENDIAN_LITTLE:
            endianFormat = '<'
        else:
            raise ValueError("Invalid endianness value: {0}".format(endianness))

        # unitSize
        if unitSize == AbstractType.UNITSIZE_8:
            unitFormat = 'b'
        elif unitSize == AbstractType.UNITSIZE_16:
            unitFormat = 'h'
        elif unitSize == AbstractType.UNITSIZE_32:
            unitFormat = 'i'
        elif unitSize == AbstractType.UNITSIZE_64:
            unitFormat = 'q'
        else:
            raise ValueError("Only 8, 16, 32 and 64 bits unitsize are available for decimals")
        # sign
        if sign == AbstractType.SIGN_UNSIGNED:
            unitFormat = unitFormat.upper()

        return endianFormat + unitFormat
