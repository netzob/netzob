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
import random
from bitarray import bitarray
from typing import Iterable

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary import partialclass
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize


class Integer(AbstractType):
    r"""This class defines an Integer type.

    The type Integer is a wrapper for the Python :class:`int` object
    with the capability to express more constraints regarding to the
    sign, endianness and unit size.

    The Integer constructor expects some parameters:

    :param value: The current value of the type instance.
    :param interval: The interval of permitted values for the Integer. This information will be used to compute the size of the Integer.
    :param nbUnits: The amount of permitted repetitions of the unit size of the Integer.
    :param unitSize: The unitsize of the current value. Values must be one of UnitSize.SIZE_* (see below for supported unit sizes). If None, the value is the default one.
    :param endianness: The endianness of the current value. Values must be Endianness.BIG or Endianness.LITTLE. If None, the value is the default one.
    :param sign: The sign of the current value. Values must be Sign.SIGNED or Sign.UNSIGNED. If None, the value is the default one.
    :type value: :class:`bitarray.bitarray`, optional
    :type interval: an :class:`int` or a tuple with the min and the max values specified as :class:`int`, optional
    :type unitSize: :class:`str`, optional
    :type endianness: :class:`Enum`, optional
    :type sign: :class:`Enum`, optional

    Netzob supports the following unit sizes:

    * UnitSize.SIZE_1
    * UnitSize.SIZE_4
    * UnitSize.SIZE_8 (default unit size)
    * UnitSize.SIZE_16
    * UnitSize.SIZE_24
    * UnitSize.SIZE_32
    * UnitSize.SIZE_64

    Netzob supports the following endianness:

    * Endianness.BIG (default endianness)
    * Endianness.LITTLE

    Netzob supports the following signs:

    * Sign.SIGNED (default sign)
    * Sign.UNSIGNED

    **Examples of Integer objects instantiations**

    The following example shows how to define an integer encoded in
    sequences of 8 bits and with a default value of 12 (thus producing
    ``\x0c``):

    >>> from netzob.all import *
    >>> f = Field(Integer(value=12, unitSize=UnitSize.SIZE_8))
    >>> f.specialize()
    b'\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits and with a default value of 12 (thus
    producing ``\x00\x00\x00\x0c``):

    >>> f = Field(Integer(value=12, unitSize=UnitSize.SIZE_32))
    >>> f.specialize()
    b'\x00\x00\x00\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits in little endian with a default value of 12
    (thus producing ``\x0c\x00\x00\x00``):

    >>> f = Field(Integer(value=12, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE))
    >>> f.specialize()
    b'\x0c\x00\x00\x00'

    The following example shows how to define a signed integer
    encoded in sequences of 16 bits with a default value of -12 (thus
    producing ``\xff\xf4``):

    >>> f = Field(Integer(value=-12, sign=Sign.SIGNED, unitSize=UnitSize.SIZE_16))
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
    (None, None)

    >>> dec = Integer(interval=(-120, 10))
    >>> print(dec.size)
    (-120, 10)


    **Examples of specific Integer types**

    By convenience, common specific integer types are also available, with
    pre-defined values of :attr:`unitSize`, :attr:`sign` and :attr:`endianness`
    attributes. They are used to shorten calls of singular definitions.

    By example, a *16-bit little-endian unsigned* Integer is classically defined
    like this:

    >>> f1 = Integer(42,
    ...              unitSize=UnitSize.SIZE_16,
    ...              sign=Sign.UNSIGNED,
    ...              endianness=Endianness.LITTLE)

    Could also be called in an equivalent form:

    >>> f2 = uint16le(42)

    There is an equivalence between these two fields, for every internal value
    of the type:

    >>> f1 = Integer(42,
    ...              unitSize=UnitSize.SIZE_16,
    ...              sign=Sign.UNSIGNED,
    ...              endianness=Endianness.LITTLE)
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
    Integer=42 ((None, None)) Integer=42 ((None, None))
    >>> f2 == f4
    False


    **Examples of conversions between Integer type objects**

    Conversion methods allow transforming encoded representation of
    objects from a source type to a destination type. The following
    examples show how to convert an integer respectively to 16 bits
    little endian, to 16 bits big endian, to 32 bits little endian and
    to 32 bits big endian:

    >>> Integer.decode(1234, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
    b'\xd2\x04'
    >>> Integer.decode(1234, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)
    b'\x04\xd2'
    >>> Integer.decode(1234, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE)
    b'\xd2\x04\x00\x00'
    >>> Integer.decode(1234, unitSize=UnitSize.SIZE_32, endianness=Endianness.BIG)
    b'\x00\x00\x04\xd2'


    **Representation of Integer type objects**

    The following examples show the representation of Integer objects
    with and without default value.

    >>> data = Integer(value=12, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE)
    >>> str(data)
    'Integer=12 ((None, None))'

    >>> data = Integer(unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
    >>> str(data)
    'Integer=None ((-32768, 32767))'


    **Encoding of Integer type objects**

    The following examples show the encoding of Integer objects with
    and without default value.

    >>> data = Integer(value=12, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE)
    >>> repr(data)
    '12'

    >>> data = Integer(unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
    >>> repr(data)
    'None'

    """

    def __init__(self,
                 value=None,
                 interval=None,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):

        # Convert value to bitarray
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray

            # Check if value is correct
            if not isinstance(value, int):
                raise ValueError("Input value shoud be a integer. Value received: '{}'".format(value))

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

        if value is None:
            interval = self._normalizeInterval(interval, unitSize, sign)
        else:
            interval = (None, None)

        super().__init__(
            self.__class__.__name__,
            value,
            interval,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def _normalizeInterval(self, interval, unitSize, sign):

        min_interval = None
        max_interval = None

        if interval is None:
            interval = (None, None)

        if not (isinstance(interval, tuple) and len(interval) == 2):
            raise ValueError("Input interval shoud be a tuple of two integers. Value received: '{}'".format(interval))

        # Handle min and max value if None is used in interval
        if unitSize == UnitSize.SIZE_1:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 1:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 1
        elif unitSize == UnitSize.SIZE_4:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 15:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 15
        elif unitSize == UnitSize.SIZE_8 and sign == Sign.SIGNED:
            if interval[0] is not None and interval[0] < -128:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 127:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = -128
            if interval[1] is None:
                max_interval = 127
        elif unitSize == UnitSize.SIZE_8 and sign == Sign.UNSIGNED:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 255:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 255
        elif unitSize == UnitSize.SIZE_16 and sign == Sign.SIGNED:
            if interval[0] is not None and interval[0] < -32767:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 32767:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = -32768
            if interval[1] is None:
                max_interval = 32767
        elif unitSize == UnitSize.SIZE_16 and sign == Sign.UNSIGNED:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 65535:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 65535
        elif unitSize == UnitSize.SIZE_24 and sign == Sign.SIGNED:
            if interval[0] is not None and interval[0] < -8388608:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 8388607:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = -8388608
            if interval[1] is None:
                max_interval = 8388607
        elif unitSize == UnitSize.SIZE_24 and sign == Sign.UNSIGNED:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 16777215:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 16777215
        elif unitSize == UnitSize.SIZE_32 and sign == Sign.SIGNED:
            if interval[0] is not None and interval[0] < -2147483648:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 2147483647:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = -2147483648
            if interval[1] is None:
                max_interval = 2147483647
        elif unitSize == UnitSize.SIZE_32 and sign == Sign.UNSIGNED:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 4294967295:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 4294967295
        elif unitSize == UnitSize.SIZE_64 and sign == Sign.SIGNED:
            if interval[0] is not None and interval[0] < -9223372036854775808:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 9223372036854775807:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = -9223372036854775808
            if interval[1] is None:
                max_interval = 9223372036854775807
        elif unitSize == UnitSize.SIZE_64 and sign == Sign.UNSIGNED:
            if interval[0] is not None and interval[0] < 0:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[1] is not None and interval[1] > 18446744073709551615:
                raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))
            if interval[0] is None:
                min_interval = 0
            if interval[1] is None:
                max_interval = 18446744073709551615

        if min_interval is None:
            min_interval = interval[0]
        if max_interval is None:
            max_interval = interval[1]

        return min_interval, max_interval

    def getMinValue(self):
        if self.value is None:
            return self.size[0]
        else:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            return TypeConverter.convert(self.value, BitArray, Integer, dst_unitSize=self.unitSize, dst_endianness=self.endianness, dst_sign=self.sign)

    def getMaxValue(self):
        if self.value is None:
            return self.size[1]
        else:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            return TypeConverter.convert(self.value, BitArray, Integer, dst_unitSize=self.unitSize, dst_endianness=self.endianness, dst_sign=self.sign)

    def getMinStorageValue(self):
        if self.sign == Sign.UNSIGNED:
            return 0
        else:
            return -int((2**int(self.unitSize.value))/2)

    def getMaxStorageValue(self):
        if self.sign == Sign.UNSIGNED:
            return 2**self.unitSize.value - 1
        else:
            return int((2**self.unitSize.value)/2) - 1

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """This method returns True if data is a Integer.
        For the moment its always true because we consider
        the integer type to be very similar to the raw type.

        :param data: the data to check
        :type data: python raw
        :return: True if data is can be parsed as a Integer
        :rtype: bool
        :raise: TypeError if the data is None


        >>> from netzob.all import *
        >>> Integer().canParse(10)
        True

        >>> Integer().canParse(TypeConverter.convert(10, Integer, BitArray))
        True

        >>> Integer(10).canParse(11)
        False

        By default, an Integer() with no parameter has a storage size
        of 8 bits:

        >>> Integer().canParse(-128)
        True

        >>> Integer().canParse(-129)
        Traceback (most recent call last):
        ...
        struct.error: byte format requires -128 <= number <= 127

        To specify a bigger storage, the unitSize should be used:

        >>> Integer(unitSize=UnitSize.SIZE_16).canParse(-129)
        True

        """

        if data is None:
            raise TypeError("data cannot be None")

        if not isinstance(data, int) and len(data) == 0:  # data cannot be an empty string
            return False

        # Convert data to bitarray
        if data is not None and not isinstance(data, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray

            # Check if data is correct
            if not isinstance(data, int):
                raise ValueError("Input data shoud be a integer. Data received: '{}'".format(data))

            data = TypeConverter.convert(
                data,
                Integer,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)

        # Compare with self.value if it is defined
        if self.value is not None:
            if self.value == data:
                return True
            else:
                return False

        # Else, compare with expected size
        if self.size is not None and isinstance(self.size, Iterable) and len(self.size) == 2:
            minSize = min(self.size)
            maxSize = max(self.size)

            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            data = TypeConverter.convert(data, BitArray, Integer, dst_unitSize=self.unitSize, dst_endianness=self.endianness, dst_sign=self.sign)

            if minSize <= data <= maxSize:
                return True
            else:
                return False
        else:
            raise Exception("Cannot parse this data '{}' because no domain is expected.".format(data))

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        r"""This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> print(Integer.decode(23))
        b'\x17'

        >>> print(Integer.decode(-1, sign=Sign.UNSIGNED))
        Traceback (most recent call last):
        ...
        struct.error: ubyte format requires 0 <= number <= 255

        >>> print(Integer.decode(-1, sign=Sign.SIGNED))
        b'\xff'

        >>> print(Integer.decode(2000000000000000))
        Traceback (most recent call last):
        ...
        struct.error: byte format requires -128 <= number <= 127

        >>> print(Integer.decode(2000000000000000, unitSize=UnitSize.SIZE_64))
        b'\x00\x07\x1a\xfdI\x8d\x00\x00'

        >>> print(Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE))
        b'\x19\x00'
        >>> print(Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG))
        b'\x00\x19'

        >>> val = 167749568
        >>> a = Integer.decode(val, unitSize=UnitSize.SIZE_32)
        >>> b = Integer.encode(a, unitSize=UnitSize.SIZE_32)
        >>> b == val
        True


        :param data: the data encoded in Integer which will be decoded in raw
        :type data: the current type
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

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
        r"""This method converts a python raw data to an Integer.

        >>> from netzob.all import *

        >>> raw = Integer.decode(23)
        >>> print(Integer.encode(raw))
        23

        >>> raw = Integer.decode(1200, unitSize=UnitSize.SIZE_16)
        >>> print(Integer.encode(raw, unitSize=UnitSize.SIZE_16))
        1200

        >>> raw = Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
        >>> print(repr(Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)))
        6400
        >>> print(repr(Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)))
        25

        >>> print(Integer.encode(b'\xcc\xac\x9c\x0c\x1c\xacL\x1c,\xac', unitSize=UnitSize.SIZE_8))
        -395865088909314208584756

        >>> raw = b'\xcc\xac\x9c'
        >>> print(Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG))
        10210476

        >>> print(Integer.encode(raw, unitSize=UnitSize.SIZE_32, endianness=Endianness.BIG))
        13413532

        >>> print(Integer.encode(raw, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE))
        10267852

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: :class:`Enum`
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: :class:`Enum`
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        perWordFormat = Integer.computeFormat(unitSize, endianness, sign)

        nbWords = int(len(data) * 8 / int(unitSize.value))

        # Check whether the input data matches unitSize. If not take 
        # precautions to able to pad it with null bytes later.
        padding_nullbytes = 0
        rest = (len(data) * 8) % int(unitSize.value)
        if rest != 0:
            nbWords += 1
            padding_nullbytes = (int(unitSize.value) - rest) / 8

        finalValue = 0

        iWord = 0
        start = 0
        end = nbWords
        inc = 1
        if endianness == Endianness.BIG:
            end = 0
            start = nbWords
            inc = -1

        for i in range(start, end, inc):
            # Extract the portion that represents the current word
            startPos = int(iWord * int(unitSize.value) / 8)
            endPos = int(iWord * int(unitSize.value) / 8 + int(unitSize.value) / 8)

            wordData = data[startPos:endPos]

            # Pad with null bytes to statisfy the unitSize.
            if padding_nullbytes > 0 and i == (end - inc):
                if endianness == Endianness.BIG:
                    wordData = b'\x00' * int(padding_nullbytes) + wordData
                elif endianness == Endianness.LITTLE:
                    wordData += b'\x00' * int(padding_nullbytes)
                else:
                    raise ValueError(
                        "Invalid endianness value: {0}".format(endianness))

            unpackedWord = struct.unpack(perWordFormat, wordData)[0]
            unpackedWord = unpackedWord << int(unitSize.value) * iWord

            finalValue = finalValue + unpackedWord

            iWord += 1

        return finalValue

    @staticmethod
    def computeFormat(unitSize, endianness, sign):
        # endian
        if endianness == Endianness.BIG:
            endianFormat = '>'
        elif endianness == Endianness.LITTLE:
            endianFormat = '<'
        else:
            raise ValueError(
                "Invalid endianness value: {0}".format(endianness))

        # unitSize
        if unitSize == UnitSize.SIZE_8:
            unitFormat = 'b'
        elif unitSize == UnitSize.SIZE_16:
            unitFormat = 'h'
        elif unitSize == UnitSize.SIZE_32:
            unitFormat = 'i'
        elif unitSize == UnitSize.SIZE_64:
            unitFormat = 'q'
        else:
            raise ValueError(
                "Only 8, 16, 32 and 64 bits unitsize are available for integers"
            )
        # sign
        if sign == Sign.UNSIGNED:
            unitFormat = unitFormat.upper()

        return endianFormat + unitFormat

    def generate(self):
        """Generates a random integer inside the given interval.

        >>> from netzob.all import *
        >>> v1 = Integer(interval=(-10, -1)).generate()
        >>> assert v1[0] is True  # sign bit (MSB) is set

        >>> v2 = Integer(42, sign=Sign.UNSIGNED)
        >>> v2.generate()
        bitarray('00101010')

        >>> v3 = uint16be(0xff00)
        >>> v3.generate()
        bitarray('1111111100000000')
        """
        if self.value is not None:
            return self.value
        elif self.size is not None and isinstance(self.size, Iterable) and len(self.size) == 2:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray

            # Size is interpreted here as an interval
            val = random.randint(min(self.size), max(self.size))
            return TypeConverter.convert(val, Integer, BitArray,
                                         src_sign=self.sign,
                                         src_unitSize=self.unitSize,
                                         src_endianness=self.endianness,
                                         dst_sign=self.sign,
                                         dst_unitSize=self.unitSize,
                                         dst_endianness=self.endianness)
        else:
            raise Exception("Cannot generate integer value, as nor constant value or interval is defined")

int8be   = partialclass(Integer,
                        unitSize=UnitSize.SIZE_8,
                        sign=Sign.SIGNED,
                        endianness=Endianness.BIG)
int8le   = partialclass(Integer,
                        unitSize=UnitSize.SIZE_8,
                        sign=Sign.SIGNED,
                        endianness=Endianness.LITTLE)
uint8be  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_8,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.BIG)
uint8le  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_8,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.LITTLE)
int16be  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_16,
                        sign=Sign.SIGNED,
                        endianness=Endianness.BIG)
int16le  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_16,
                        sign=Sign.SIGNED,
                        endianness=Endianness.LITTLE)
uint16be = partialclass(Integer,
                        unitSize=UnitSize.SIZE_16,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.BIG)
uint16le = partialclass(Integer,
                        unitSize=UnitSize.SIZE_16,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.LITTLE)
int32be  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_32,
                        sign=Sign.SIGNED,
                        endianness=Endianness.BIG)
int32le  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_32,
                        sign=Sign.SIGNED,
                        endianness=Endianness.LITTLE)
uint32be = partialclass(Integer,
                        unitSize=UnitSize.SIZE_32,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.BIG)
uint32le = partialclass(Integer,
                        unitSize=UnitSize.SIZE_32,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.LITTLE)
int64be  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_64,
                        sign=Sign.SIGNED,
                        endianness=Endianness.BIG)
int64le  = partialclass(Integer,
                        unitSize=UnitSize.SIZE_64,
                        sign=Sign.SIGNED,
                        endianness=Endianness.LITTLE)
uint64be = partialclass(Integer,
                        unitSize=UnitSize.SIZE_64,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.BIG)
uint64le = partialclass(Integer,
                        unitSize=UnitSize.SIZE_64,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.LITTLE)
int8, int16, int32, int64 = int8be, int16be, int32be, int64be
uint8, uint16, uint32, uint64 = uint8be, uint16be, uint32be, uint64be
