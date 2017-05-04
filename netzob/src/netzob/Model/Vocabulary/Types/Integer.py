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
from netzob.Model.Vocabulary import partialclass
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class Integer(AbstractType):
    r"""This class defines an Integer type.

    The type Integer is a wrapper for the Python :class:`int` object
    with the capability to express more constraints regarding to the
    sign, endianness and unit size.

    The Integer constructor expects some parameters:

    :param value: The current value of the type instance.
    :param interval: The interval of permitted values for the Integer. This information will be used to compute the size of the Integer.
    :param nbUnits: The amount of permitted repetitions of the unit size of the Integer.
    :param unitSize: The unitsize of the current value. Values must be one of AbstractType.UNITSIZE_* (see below for supported unit sizes). If None, the value is the default one.
    :param endianness: The endianness of the current value. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE. If None, the value is the default one.
    :param sign: The sign of the current value. Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED. If None, the value is the default one.
    :type value: :class:`bitarray.bitarray`, optional
    :type interval: an :class:`int` or a tuple with the min and the max values specified as :class:`int`, optional
    :type unitSize: :class:`str`, optional
    :type endianness: :class:`str`, optional
    :type sign: :class:`str`, optional

    Netzob support the following unit sizes:

    * AbstractType.UNITSIZE_1
    * AbstractType.UNITSIZE_4
    * AbstractType.UNITSIZE_8 (default unit size)
    * AbstractType.UNITSIZE_16
    * AbstractType.UNITSIZE_24
    * AbstractType.UNITSIZE_32
    * AbstractType.UNITSIZE_64

    Netzob support the following endianness:

    * AbstractType.ENDIAN_BIG (default endianness)
    * AbstractType.ENDIAN_LITTLE

    Netzob support the following signs:

    * AbstractType.SIGN_SIGNED (default sign)
    * AbstractType.SIGN_UNSIGNED

    **Examples of Integer objects instantiations**

    The following example shows how to define an integer encoded in
    sequences of 8 bits and with a default value of 12 (thus producing
    ``\x0c``):

    >>> from netzob.all import *
    >>> f = Field(Integer(value=12, unitSize=AbstractType.UNITSIZE_8))
    >>> f.specialize()
    b'\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits and with a default value of 12 (thus
    producing ``\x00\x00\x00\x0c``):

    >>> f = Field(Integer(value=12, unitSize=AbstractType.UNITSIZE_32))
    >>> f.specialize()
    b'\x00\x00\x00\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits in little endian with a default value of 12
    (thus producing ``\x0c\x00\x00\x00``):

    >>> f = Field(Integer(value=12, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE))
    >>> f.specialize()
    b'\x0c\x00\x00\x00'

    The following example shows how to define a signed integer
    encoded in sequences of 16 bits with a default value of -12 (thus
    producing ``\xff\xf4``):

    >>> f = Field(Integer(value=-12, sign=AbstractType.SIGN_SIGNED, unitSize=AbstractType.UNITSIZE_16))
    >>> f.specialize()
    b'\xff\xf4'


    **Examples of Integer internal attributes access**

    >>> from netzob.all import *
    >>> cDec = Integer(20)
    >>> print(repr(cDec))
    20
    >>> print(cDec.typeName)
    Integer
    >>> print(cDec.value)
    bitarray('00010100')

    The required size in bits is automatically computed following the specifications:

    >>> dec = Integer(10)
    >>> print(dec.size)
    (8, 8)

    >>> dec = Integer(interval=(-120, 10))
    >>> print(dec.size)
    (16, 16)


    **Examples of specific Integer types**

    By convenience, common specific integer types are also available, with
    pre-defined values of :attr:`unitSize`, :attr:`sign` and :attr:`endianness`
    attributes. They are used to shorten calls of singular definitions.

    By example, a *16-bit little-endian unsigned* Integer is classicaly defined
    like this:

    >>> f1 = Integer(42,
    ...              unitSize=AbstractType.UNITSIZE_16,
    ...              sign=AbstractType.SIGN_UNSIGNED,
    ...              endianness=AbstractType.ENDIAN_LITTLE)

    Could also be called in an equivalent form:

    >>> f2 = uint16le(42)

    There is an equivalence between these two fields, for every internal value
    of the type:

    >>> f1 = Integer(42,
    ...              unitSize=AbstractType.UNITSIZE_16,
    ...              sign=AbstractType.SIGN_UNSIGNED,
    ...              endianness=AbstractType.ENDIAN_LITTLE)
    >>> f2 = uint16le(42)
    >>> f1, f2
    (42, 42)
    >>> f1 == f2
    True

    But a comparison between two specific integers of different kind will
    always fail, even if their value looks equivalent:

    >>> f2 = uint16le(42)
    >>> f3 = uint32le(42)
    >>> f2 == f3
    False

    And even when the concrete value seems identical, fields are not:

    >>> f2 = uint16le(42)
    >>> f4 = int16le(42)
    >>> f2, f4
    (42, 42)
    >>> print(f2, f4)
    Integer=42 ((16, 16)) Integer=42 ((16, 16))
    >>> f2 == f4
    False


    **Examples of conversions between Integer type objects**

    Conversion methods allow transforming encoded representation of
    objects from a source type to a destination type. The following
    examples show how to convert an integer respectively to 16 bits
    little endian, to 16 bits big endian, to 32 bits little endian and
    to 32 bits big endian:

    >>> Integer.decode(1234, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
    b'\xd2\x04'
    >>> Integer.decode(1234, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG)
    b'\x04\xd2'
    >>> Integer.decode(1234, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE)
    b'\xd2\x04\x00\x00'
    >>> Integer.decode(1234, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_BIG)
    b'\x00\x00\x04\xd2'


    **Representation of Integer type objects**

    The following examples show the representation of Integer objects
    with and without default value.

    >>> data = Integer(value=12, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE)
    >>> str(data)
    'Integer=12 ((32, 32))'

    >>> data = Integer(unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
    >>> str(data)
    'Integer=None ((16, 16))'


    **Encoding of Integer type objects**

    The following examples show the encoding of Integer objects with
    and without default value.

    >>> data = Integer(value=12, unitSize=AbstractType.UNITSIZE_32, endianness=AbstractType.ENDIAN_LITTLE)
    >>> repr(data)
    '12'

    >>> data = Integer(unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_LITTLE)
    >>> repr(data)
    'None'

    """

    def __init__(self,
                 value=None,
                 interval=None,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            interval = value
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
        else:
            value = None

        if interval is not None:
            nbBits = int(
                self._computeNbUnitSizeForInterval(interval, unitSize,
                                                   sign)) * int(unitSize)
        else:
            nbBits = int(unitSize)

        super().__init__(
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
        >>> Integer().canParse(TypeConverter.convert("hello netzob", String, Raw))
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
        struct.error: byte format requires -128 <= number <= 127

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
        """This method converts a python raw data to an Integer.

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

        >>> print(Integer.encode(b'\\xcc\\xac\\x9c\\x0c\\x1c\\xacL\\x1c,\\xac', unitSize=AbstractType.UNITSIZE_8))
        -395865088909314208584756

        >>> raw = b'\\xcc\\xac\\x9c'
        >>> print(Integer.encode(raw, unitSize=AbstractType.UNITSIZE_16, endianness=AbstractType.ENDIAN_BIG))
        10210476

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
        # precautions to able to pad it with null bytes later.
        padding_nullbytes = 0
        rest = (len(data) * 8) % int(unitSize)
        if rest != 0:
            nbWords += 1
            padding_nullbytes = (int(unitSize) - rest) / 8

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
            startPos = int(iWord * int(unitSize) / 8)
            endPos = int(iWord * int(unitSize) / 8 + int(unitSize) / 8)

            wordData = data[startPos:endPos]

            # Pad with null bytes to statisfy the unitSize.
            if padding_nullbytes > 0 and i == (end - inc):
                if endianness == AbstractType.ENDIAN_BIG:
                    wordData = b'\x00' * int(padding_nullbytes) + wordData
                elif endianness == AbstractType.ENDIAN_LITTLE:
                    wordData += b'\x00' * int(padding_nullbytes)
                else:
                    raise ValueError(
                        "Invalid endianness value: {0}".format(endianness))

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


int8be   = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_8,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
int8le   = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_8,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
uint8be  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_8,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
uint8le  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_8,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
int16be  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_16,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
int16le  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_16,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
uint16be = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_16,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
uint16le = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_16,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
int32be  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_32,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
int32le  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_32,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
uint32be = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_32,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
uint32le = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_32,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
int64be  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_64,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
int64le  = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_64,
                        sign=AbstractType.SIGN_SIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
uint64be = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_64,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_BIG)
uint64le = partialclass(Integer,
                        unitSize=AbstractType.UNITSIZE_64,
                        sign=AbstractType.SIGN_UNSIGNED,
                        endianness=AbstractType.ENDIAN_LITTLE)
int8, int16, int32, int64 = int8be, int16be, int32be, int64be
uint8, uint16, uint32, uint64 = uint8be, uint16be, uint32be, uint64be
