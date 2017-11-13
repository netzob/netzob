# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import struct
import math
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class Integer(AbstractType):
    """The netzob type Integer, a wrapper for the "int" object (with unitSize).
    Some constraints can be defined and they participate in the definition of the size.

    The following constraints can be defined:
    - a static value (for instance 20) with a specific unitSize and a sign definition
    - an interval of value (positive and/or negative), this way the size is automaticaly computed in terms of
    number of unitSize required given the sign
    - a number of unitSize

    >>> from netzob.all import *
    >>> cDec = Integer(20)
    >>> print(repr(cDec))
    20
    >>> print(cDec.typeName)
    Integer
    >>> print(cDec.value)
    bitarray('00010100')

    The required size in bits is automaticaly computed following the specifications:
    >>> dec = Integer(10)
    >>> print(dec.size)
    (8, 8)

    >>> dec = Integer(interval=(-130, 10), sign=AbstractType.SIGN_SIGNED)
    >>> print(dec.size)
    (16, 16)

    Use the convert function to convert the current type to any other netzob type
    >>> dec = Integer(10)
    >>> raw = dec.convertValue(Raw, dst_endianness=AbstractType.ENDIAN_BIG)
    >>> print(raw)
    Raw=b'\\n' ((0, 8))

    It is not possible to convert if the object has not value
    >>> a = Integer()
    >>> a.convertValue(Raw)
    Traceback (most recent call last):
    ...
    TypeError: Data cannot be None

    """
    def __init__(self,
                 value=None,
                 interval=None,
                 unitSize=None,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):

        if unitSize is None:
            if interval is None:  # value handling
                if value is None:
                    unitSize = AbstractType.defaultUnitSize()
                else:
                    unitSize = Integer.checkUnitSizeForValue(value, sign)
            else:  # interval handling
                if isinstance(interval, int):
                    unitSize = Integer.checkUnitSizeForValue(interval, sign)
                elif len(interval) == 2:
                    unitSizeA = Integer.checkUnitSizeForValue(interval[0], sign)
                    unitSizeB = Integer.checkUnitSizeForValue(interval[1], sign)
                    unitSize = max(unitSizeA, unitSizeB)
                else:  # shouldn't happen, since _checkUnitSizeForValue raises an exception before
                    unitSize = AbstractType.defaultUnitSize()

        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray

            value = TypeConverter.convert(
                value,
                Integer,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        if interval is not None:
            nbBits = int(self._computeNbUnitSizeForInterval(interval, unitSize, sign)) * int(unitSize)
        else:
            nbBits = int(unitSize)

        super(Integer, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def _computeNbUnitSizeForInterval(self, interval, unitSize, sign):
        if isinstance(interval, int):
            # the interval is a single value
            # bspec = ⌊log2(n)⌋ + 1 (+1 for signed)
            return self._computeNbUnitSizeForVal(interval, unitSize, sign)
        elif len(interval) == 2:
            minVal = min(interval[0], interval[1])
            maxVal = max(interval[0], interval[1])

            minNbUnit = self._computeNbUnitSizeForVal(minVal, unitSize, sign)
            maxNbUnit = self._computeNbUnitSizeForVal(maxVal, unitSize, sign)

            return max(minNbUnit, maxNbUnit)

    def _computeNbUnitSizeForVal(self, val, unitSize, sign):
        # the interval is a single value
        # bspec = ⌊log2(n)⌋ + 1 (+1 for signed)
        val = abs(val)
        if val != 0:
            if sign == AbstractType.SIGN_UNSIGNED:
                return math.floor(
                    (math.floor(math.log(val, 2)) + 1) / int(unitSize)) + 1
            else:
                return math.floor(
                    (math.floor(math.log(val, 2)) + 2) / int(unitSize)) + 1

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """This method returns True if data is a Integer.
        For the moment its always true because we consider
        the integer type to be very similar to the raw type.

        >>> from netzob.all import *
        >>> Integer().canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data is can be parsed as a Integer
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        return True

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> print(Integer.decode(23))
        b'\\x17'

        >>> print(Integer.decode(-1, sign=AbstractType.SIGN_UNSIGNED))
        Traceback (most recent call last):
        ...
        struct.error: ubyte format requires 0 <= number <= 255

        >>> print(Integer.decode(-1, sign=AbstractType.SIGN_SIGNED))
        b'\\xff'

        >>> print(Integer.decode(2000000000000000))
        Traceback (most recent call last):
        ...
        struct.error: ubyte format requires 0 <= number <= 255

        >>> print(Integer.decode(2000000000000000, unitSize=AbstractType.UNITSIZE_64))
        b'\\x00\\x07\\x1a\\xfdI\\x8d\\x00\\x00'

        >>> print(Integer.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE))
        b'\\x19\\x00'
        >>> print(Integer.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG))
        b'\\x00\\x19'

        >>> val = 167749568
        >>> a = Integer.decode(val, unitSize=AbstractType.UNITSIZE_32)
        >>> b = Integer.encode(a, unitSize=AbstractType.UNITSIZE_32)
        >>> b == val
        True


        :param data: the data encoded in Integer which will be decoded in raw
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

        f = Integer.computeFormat(unitSize, endianness, sign)

        return struct.pack(f, int(data))

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the Integer.

        >>> from netzob.all import *

        >>> raw = Integer.decode(23)
        >>> print(Integer.encode(raw))
        23

        >>> raw = Integer.decode(1200, unitSize=AbstractType.UNITSIZE_16)
        >>> print(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_16))
        1200

        >>> raw = Integer.decode(25, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
        >>> print(repr(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG)))
        6400
        >>> print(repr(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)))
        25

        >>> print(Integer.encode(b'\\xcc\\xac\\x9c\\x0c\\x1c\\xacL\\x1c,\\xac', unitSize=AbstractType.UNITSIZE_8, sign=AbstractType.SIGN_SIGNED))
        -247119785962690400474196

        # raw is interpreted as b'\xcc\xac\x00\x9c' by encode and
        # as big endian with unit size 16 as (0x009c << 16) + 0xccac = 10276012
        >>> raw = b'\\xcc\\xac\\x9c'
        >>> print(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG))
        13413532

        >>> print(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_BIG))
        13413532

        >>> print(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE))
        10267852

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

        perWordFormat = Integer.computeFormat(unitSize, endianness, sign)

        nbWords = int(len(data) * 8 / int(unitSize))

        # Check whether the input data matches unitSize. If not take 
        # precautions to able to pad it with null bytes to statisfy the unitSize.
        padding_nullbytes = 0
        rest = (len(data) * 8) % int(unitSize)
        if rest != 0:
            nbWords += 1
            padding_nullbytes = (int(unitSize) - rest) / 8
            if endianness == AbstractType.ENDIAN_BIG:
                data = b'\x00' * int(padding_nullbytes) + data
            elif endianness == AbstractType.ENDIAN_LITTLE:
                data += b'\x00' * int(padding_nullbytes)
            else:
                raise ValueError(
                    "Invalid endianness value: {0}".format(endianness))

        finalValue = 0

        start = 0
        end = nbWords
        for i in range(start, end):
            # Extract the portion that represents the current word
            startPos = i * int(unitSize) // 8
            endPos = startPos + int(unitSize) // 8
            wordData = data[startPos:endPos]

            unpackedWord = struct.unpack(perWordFormat, wordData)[0]
            if endianness == AbstractType.ENDIAN_LITTLE:
                wordShift = i
            else:
                wordShift = nbWords - i - 1
            unpackedWord = unpackedWord << (int(unitSize) * wordShift)

            finalValue = finalValue + unpackedWord

        return finalValue

    @staticmethod
    def computeFormat(unitSize, endianness, sign):
        # endian
        if endianness == AbstractType.ENDIAN_BIG:
            endianFormat = '>'
        elif endianness == AbstractType.ENDIAN_LITTLE:
            endianFormat = '<'
        else:
            raise ValueError(
                "Invalid endianness value: {0}".format(endianness))

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
            raise ValueError(
                "Only 8, 16, 32 and 64 bits unitsize are available for integers"
            )
        # sign
        if sign == AbstractType.SIGN_UNSIGNED:
            unitFormat = unitFormat.upper()

        return endianFormat + unitFormat

    @staticmethod
    def checkUnitSizeForValue(value, sign):
        """
        >>> Integer.checkUnitSizeForValue(-1, AbstractType.SIGN_SIGNED) == AbstractType.UNITSIZE_8
        True
        >>> Integer.checkUnitSizeForValue(-1, AbstractType.SIGN_UNSIGNED)
        Traceback (most recent call last):
        ...
        ValueError: Value is out of unsigned 64bit Integer range.
        >>> Integer.checkUnitSizeForValue(-130, AbstractType.SIGN_SIGNED) == AbstractType.UNITSIZE_16
        True
        >>> Integer.checkUnitSizeForValue(260, AbstractType.SIGN_UNSIGNED) == AbstractType.UNITSIZE_16
        True
        >>> Integer.checkUnitSizeForValue(2147483647, AbstractType.SIGN_SIGNED) == AbstractType.UNITSIZE_32
        True
        >>> Integer.checkUnitSizeForValue(4294967295, AbstractType.SIGN_UNSIGNED) == AbstractType.UNITSIZE_32
        True
        >>> Integer.checkUnitSizeForValue(-9223372036854775808, AbstractType.SIGN_SIGNED) == AbstractType.UNITSIZE_64
        True
        >>> Integer.checkUnitSizeForValue(18446744073709551615, AbstractType.SIGN_UNSIGNED) == AbstractType.UNITSIZE_64
        True
        >>> Integer.checkUnitSizeForValue(18446744073709551615, AbstractType.SIGN_SIGNED)
        Traceback (most recent call last):
        ...
        ValueError: Value is out of signed 64bit Integer range.


        :param value: The value to get an unitSize for
        :param sign: The desired sign for the value
        :returns: The unitsize that can hold "value".
        :raises ValueError: There is no unit size of Integer (max 64 bits) that can hold "value"
        """

        if sign is AbstractType.SIGN_SIGNED:
            if -0x80 <= value <= 0x7f:
                return AbstractType.UNITSIZE_8
            elif -0x8000 <= value <= 0x7fff:
                return AbstractType.UNITSIZE_16
            elif -0x80000000 <= value <= 0x7fffffff:
                return AbstractType.UNITSIZE_32
            elif -0x8000000000000000 <= value <= 0x7fffffffffffffff:
                return AbstractType.UNITSIZE_64
            else:
                raise ValueError("Value is out of signed 64bit Integer range.")
        if sign is AbstractType.SIGN_UNSIGNED:
            if 0x00 <= value <= 0xff:
                return AbstractType.UNITSIZE_8
            elif 0x00 <= value <= 0xffff:
                return AbstractType.UNITSIZE_16
            elif 0x00 <= value <= 0xffffffff:
                return AbstractType.UNITSIZE_32
            elif 0x00 <= value <= 0xffffffffffffffff:
                return AbstractType.UNITSIZE_64
            else:
                raise ValueError("Value is out of unsigned 64bit Integer range.")