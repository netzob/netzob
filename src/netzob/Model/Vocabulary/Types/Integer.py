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
from netzob.Common.Utils.Decorators import public_api


class Integer(AbstractType):
    r"""The Integer class represents an integer, with the
    capability to express constraints regarding the sign, the
    endianness and the unit size.

    The Integer constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains a fixed integer. If None, the constructed Integer will represent an interval of values (see :attr:`interval` parameter).
    :type value: :class:`bitarray` or :class:`int`, optional
    :param interval: This parameter is used to describe a domain that contains an interval of permitted values. This information is used to compute the storage size of the Integer. If None, the interval will range from the minimum value to the maximum value that an integer can encode, according to its unit size, endianness and sign attributes.
    :type interval: a tuple with the min and the max values specified as :class:`int`, optional
    :param unitSize: The unitsize, in bits, of the storage area used to encode the integer. Values must be one of UnitSize.SIZE_*.

      The following unit sizes are available:

      * UnitSize.SIZE_8
      * UnitSize.SIZE_16 (default unit size)
      * UnitSize.SIZE_24
      * UnitSize.SIZE_32
      * UnitSize.SIZE_64

    :type unitSize: :class:`UnitSize <netzob.Model.Vocabulary.Types.AbstractType.UnitSize>`, optional

    :param endianness: The endianness of the value.

      The following endiannesses are available:

      * Endianness.BIG (default endianness)
      * Endianness.LITTLE

    :type endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`, optional

    :param sign: The sign of the value.

      The following signs are available:

      * Sign.SIGNED (default sign)
      * Sign.UNSIGNED

    :type sign: :class:`Sign <netzob.Model.Vocabulary.Types.AbstractType.Sign>`, optional
    :param default: This parameter is the default value used in specialization.
    :type default: :class:`bitarray` or :class:`int`, optional

    .. note::
       :attr:`value` and :attr:`interval` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.

       :attr:`value` and :attr:`default` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The Integer class provides the following public variables:

    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size of the expected data type defined by a tuple (min integer, max integer).
               Instead of a tuple, an integer can be used to represent both min and max values.
    :var unitSize: The unitSize of the current value.
    :var endianness: The endianness of the current value.
    :var sign: The sign of the current value.
    :var default: The default value used in specialization.
    :vartype value: :class:`bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`
    :vartype unitSize: :class:`str`
    :vartype endianness: :class:`str`
    :vartype sign: :class:`str`
    :vartype default: :class:`bitarray`

    **Examples of Integer object instantiations**

    The creation of an Integer with no parameter will create a signed,
    big-endian integer of 16 bits:

    >>> from netzob.all import *
    >>> i = Integer()
    >>> i.generate().tobytes()  # doctest: +SKIP
    b'\x94\xba'

    The following example shows how to define an integer encoded in
    sequences of 8 bits and with a constant value of 12 (thus producing
    ``\x0c``):

    >>> from netzob.all import *
    >>> i = Integer(12, unitSize=UnitSize.SIZE_8)
    >>> i.generate().tobytes()
    b'\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits and with a constant value of 12 (thus
    producing ``\x00\x00\x00\x0c``):

    >>> from netzob.all import *
    >>> i = Integer(12, unitSize=UnitSize.SIZE_32)
    >>> i.generate().tobytes()
    b'\x00\x00\x00\x0c'

    The following example shows how to define an integer encoded in
    sequences of 32 bits in little endian with a constant value of 12
    (thus producing ``\x0c\x00\x00\x00``):

    >>> from netzob.all import *
    >>> i = Integer(12, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE)
    >>> i.generate().tobytes()
    b'\x0c\x00\x00\x00'

    The following example shows how to define a signed integer
    encoded in sequences of 16 bits with a constant value of -12 (thus
    producing ``\xff\xf4``):

    >>> from netzob.all import *
    >>> i = Integer(-12, sign=Sign.SIGNED, unitSize=UnitSize.SIZE_16)
    >>> i.generate().tobytes()
    b'\xff\xf4'


    **Examples of pre-defined Integer types**

    For convenience, common specific integer types are also available, with
    pre-defined values of :attr:`unitSize`, :attr:`sign` and :attr:`endianness`
    attributes. They are used to shorten calls of singular definitions.

    Available big-endian pre-defined Integer types are:

    * int8be (or int8)
    * int16be (or int16)
    * int24be (or int24)
    * int32be (or int32)
    * int64be (or int64)
    * uint8be (or uint8)
    * uint16be (or uint16)
    * uint24be (or uint24)
    * uint32be (or uint32)
    * uint64be (or uint64)

    Available little-endian pre-defined Integer types are:

    * int8le
    * int16le
    * int24le
    * int32le
    * int64le
    * uint8le
    * uint16le
    * uint24le
    * uint32le
    * uint64le

    For example, a *16-bit little-endian unsigned* Integer is classically defined
    like this:

    >>> from netzob.all import *
    >>> i = Integer(42,
    ...             unitSize=UnitSize.SIZE_16,
    ...             sign=Sign.UNSIGNED,
    ...             endianness=Endianness.LITTLE)

    Could also be called in an equivalent form:

    >>> from netzob.all import *
    >>> i = uint16le(42)

    There is an equivalence between these two integers, for every
    internal value of the type:

    >>> from netzob.all import *
    >>> i1 = Integer(42,
    ...              unitSize=UnitSize.SIZE_16,
    ...              sign=Sign.UNSIGNED,
    ...              endianness=Endianness.LITTLE)
    >>> i2 = uint16le(42)
    >>> i1, i2
    (42, 42)
    >>> i1 == i2
    True

    But a comparison between two specific integers of different kinds will
    always fail, even if their values look equivalent:

    >>> from netzob.all import *
    >>> i1 = uint16le(42)
    >>> i2 = uint32le(42)
    >>> i1 == i2
    False

    And even when the concrete value seems identical, the integer
    objects are not:

    >>> from netzob.all import *
    >>> i1 = uint16le(42)
    >>> i2 = int16le(42)
    >>> i1, i2
    (42, 42)
    >>> print(i1, i2)
    Integer(42) Integer(42)
    >>> i1 == i2
    False


    **Integer raw representations**

    The following examples show how to create integers with different
    raw representation, depending on data type attributes. In these
    examples, we create a 16-bit little endian, a 16-bit big endian,
    a 32-bit little endian and a 32-bit big endian:

    >>> from netzob.all import *
    >>> int16le(1234).value.tobytes()
    b'\xd2\x04'
    >>> int16be(1234).value.tobytes()
    b'\x04\xd2'
    >>> int32le(1234).value.tobytes()
    b'\xd2\x04\x00\x00'
    >>> int32be(1234).value.tobytes()
    b'\x00\x00\x04\xd2'


    **Representation of Integer type objects**

    The following examples show the representation of Integer objects
    with and without a constant value.

    >>> from netzob.all import *
    >>> i = int16le(12)
    >>> print(i)
    Integer(12)

    >>> from netzob.all import *
    >>> i = int16le()
    >>> print(i)
    Integer(-32768,32767)


    **Encoding of Integer type objects**

    The following examples show the encoding of Integer objects with
    and without a constant value.

    >>> from netzob.all import *
    >>> i = int32le(12)
    >>> repr(i)
    '12'

    >>> from netzob.all import *
    >>> i = int32le()
    >>> repr(i)
    'None'


    **Using a default value**

    This next example shows the usage of a default value:

    >>> from netzob.all import *
    >>> t = uint8(default=3)
    >>> t.generate().tobytes()
    b'\x03'

    >>> from netzob.all import *
    >>> t = Integer(interval=(1, 4), default=4)
    >>> t.generate().tobytes()
    b'\x00\x04'

    """

    @public_api
    def __init__(self,
                 value=None,
                 interval=None,
                 unitSize=UnitSize.SIZE_16,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign(),
                 default=None):

        if value is not None and interval is not None:
            raise ValueError("An Integer should have either its value or its interval set, but not both")

        if value is not None and default is not None:
            raise ValueError("An Integer should have either its constant value or its default value set, but not both")

        # Validate uniSize
        valid_unitSizes = [UnitSize.SIZE_8, UnitSize.SIZE_16, UnitSize.SIZE_24, UnitSize.SIZE_32, UnitSize.SIZE_64]
        if unitSize not in valid_unitSizes:
            raise ValueError("unitSize parameter should be one of '{}', but not '{}'".format(valid_unitSizes, str(unitSize)))

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

        # Convert default value to bitarray
        if default is not None and not isinstance(default, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray

            # Check if default value is correct
            if not isinstance(default, int):
                raise ValueError("Input default value shoud be a integer. Default value received: '{}'".format(default))

            default = TypeConverter.convert(
                default,
                Integer,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        # Handle interval
        if unitSize is None:
            raise TypeError("unitSize cannot be None")
        if sign is None:
            raise TypeError("sign cannot be None")
        if endianness is None:
            raise TypeError("endianness cannot be None")
        interval = self._normalizeInterval(interval, unitSize, sign)

        super().__init__(
            self.__class__.__name__,
            value,
            interval,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign,
            default=default)

    def __str__(self):
        if self.value is not None:
            return "{}({})".format(self.typeName, Integer.encode(self.value.tobytes(), unitSize=self.unitSize, endianness=self.endianness, sign=self.sign))
        else:
            if self.size[0] == self.size[1]:
                self._logger.fatal("PAN")
                return "{}(interval={})".format(self.typeName, self.size[0])
            else:
                return "{}({},{})".format(self.typeName, self.size[0], self.size[1])

    def _normalizeInterval(self, interval, unitSize, sign):

        if interval is None:
            interval = (None, None)
        elif isinstance(interval, int):
            interval = (interval, interval)
        else:
            if not (isinstance(interval, tuple) and len(interval) == 2):
                raise ValueError("Input interval shoud be a tuple of two integers. Value received: '{}'".format(interval))

            if not isinstance(interval[0], int):
                raise TypeError("First element of interval should be an integer")
            if not isinstance(interval[1], int):
                raise TypeError("Second element of interval should be an integer")

            if interval[0] == interval[1] == 0:
                raise TypeError("Interval must be defined with a tuple of integers, and cannot be both equal to zero")

            if interval[1] < interval[0]:
                ValueError("Internal must be defined with a tuple of integers, where the second value is greater than the first value")

        # Compute min and max values
        min_interval = getMinStorageValue(unitSize=unitSize, sign=sign)
        max_interval = getMaxStorageValue(unitSize=unitSize, sign=sign)

        if ((interval[0] is not None and interval[0] < min_interval) or
            (interval[1] is not None and interval[1] > max_interval)):
            raise ValueError("Specified interval '{}' does not fit in specified unitSize '{}'".format(interval, unitSize))

        # Reset min and max values if a valid interval is provided
        if interval[0] is not None:
            min_interval = interval[0]
        if interval[1] is not None:
            max_interval = interval[1]

        return min_interval, max_interval

    @public_api
    def count(self):
        r"""

        >>> from netzob.all import *
        >>> Integer().count()
        65536

        >>> Integer(4).count()
        1

        >>> Integer(interval=(1, 10)).count()
        10

        >>> uint8(interval=(1, 10)).count()
        10

        >>> uint8().count()
        256

        """

        if self.value is not None:
            return 1
        else:
            return self.getMaxValue() - self.getMinValue() + 1

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
        return getMinStorageValue(self.unitSize, self.sign)

    def getMaxStorageValue(self):
        return getMaxStorageValue(self.unitSize, self.sign)

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
        >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        >>> Integer().canParse(10)
        True

        >>> Integer(10).canParse(11)
        False

        By default, an Integer() with no parameter has a storage size
        of 8 bits:

        >>> Integer().canParse(-128)
        True

        >>> Integer().canParse(32768)
        Traceback (most recent call last):
        ...
        struct.error: 'h' format requires -32768 <= number <= 32767

        To specify a bigger storage, the unitSize should be used:

        >>> Integer(unitSize=UnitSize.SIZE_32).canParse(32768)
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
            return self.value == data

        # Else, compare with expected size
        if self.size is not None and isinstance(self.size, Iterable) and len(self.size) == 2:

            if len(data) != self.unitSize.value:
                return False

            minSize = min(self.size)
            maxSize = max(self.size)

            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            int_data = TypeConverter.convert(data, BitArray, Integer,
                                             dst_unitSize=self.unitSize,
                                             dst_endianness=self.endianness,
                                             dst_sign=self.sign)

            return minSize <= int_data <= maxSize

        raise Exception("Cannot parse this data '{}' because no domain is "
                        "expected.".format(data))

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        r"""This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> Integer.decode(23)
        b'\x17'

        >>> Integer.decode(-1, sign=Sign.UNSIGNED)
        Traceback (most recent call last):
        ...
        struct.error: ubyte format requires 0 <= number <= 255

        >>> Integer.decode(-1, sign=Sign.SIGNED)
        b'\xff'

        >>> Integer.decode(2000000000000000)
        Traceback (most recent call last):
        ...
        struct.error: byte format requires -128 <= number <= 127

        >>> Integer.decode(2000000000000000, unitSize=UnitSize.SIZE_64)
        b'\x00\x07\x1a\xfdI\x8d\x00\x00'

        >>> Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
        b'\x19\x00'
        >>> Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)
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

        data = struct.pack(f, int(data))

        # Special case for 24 bits integers
        if unitSize == UnitSize.SIZE_24:
            if endianness == Endianness.BIG:
                data = data[1:]
            else:
                data = data[:-1]

        return data

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        r"""This method converts a python raw data to an Integer.

        >>> from netzob.all import *

        >>> raw = Integer.decode(23)
        >>> Integer.encode(raw)
        23

        >>> raw = Integer.decode(1200, unitSize=UnitSize.SIZE_16)
        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_16)
        1200

        >>> raw = Integer.decode(25, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)
        6400
        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.LITTLE)
        25

        >>> Integer.encode(b'\xcc\xac\x9c\x0c\x1c\xacL\x1c,\xac', unitSize=UnitSize.SIZE_8)
        -395865088909314208584756

        >>> raw = b'\xcc\xac\x9c'
        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_16, endianness=Endianness.BIG)
        10210476

        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_32, endianness=Endianness.BIG)
        13413532

        >>> Integer.encode(raw, unitSize=UnitSize.SIZE_32, endianness=Endianness.LITTLE)
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

            # Special case for 24 bits integers
            if unitSize == UnitSize.SIZE_24:
                if endianness == Endianness.BIG:
                    wordData = b'\x00' + wordData
                else:
                    wordData = wordData + b'\x00'

            unpackedWord = struct.unpack(perWordFormat, wordData)[0]

            # Special case for 24 bits integers
            if unitSize == UnitSize.SIZE_24 and sign == Sign.SIGNED:
                unpackedWord = unpackedWord if not (unpackedWord & 0x800000) else unpackedWord - 0x1000000

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
        if unitSize == UnitSize.SIZE_8 or unitSize == UnitSize.SIZE_4:
            unitFormat = 'b'
        elif unitSize == UnitSize.SIZE_16:
            unitFormat = 'h'
        elif unitSize == UnitSize.SIZE_24:
            unitFormat = 'i'
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
        >>> v1[0] is True  # sign bit (MSB) is set
        True
        >>> v1
        bitarray('1111111111111111')

        >>> v2 = Integer(42, sign=Sign.UNSIGNED)
        >>> v2.generate()
        bitarray('0000000000101010')

        >>> v3 = uint16be(0xff00)
        >>> v3.generate()
        bitarray('1111111100000000')
        """
        if self.value is not None:
            return self.value
        elif self.default is not None:
            return self.default
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

    def getFixedBitSize(self):
        self._logger.debug("Determine the deterministic size of the value of "
                           "the type")
        return self.unitSize.value


def getMinStorageValue(unitSize, sign):
    if sign == Sign.UNSIGNED:
        return 0
    else:
        return -int((2**int(unitSize.value)) / 2)


def getMaxStorageValue(unitSize, sign):
    if sign == Sign.UNSIGNED:
        d = (1 << unitSize.value) - 1
    else:
        d = int((1 << unitSize.value) / 2) - 1
    return d


int8be = partialclass(Integer,
                      unitSize=UnitSize.SIZE_8,
                      sign=Sign.SIGNED,
                      endianness=Endianness.BIG)
int8le = partialclass(Integer,
                      unitSize=UnitSize.SIZE_8,
                      sign=Sign.SIGNED,
                      endianness=Endianness.LITTLE)
uint8be = partialclass(Integer,
                       unitSize=UnitSize.SIZE_8,
                       sign=Sign.UNSIGNED,
                       endianness=Endianness.BIG)
uint8le = partialclass(Integer,
                       unitSize=UnitSize.SIZE_8,
                       sign=Sign.UNSIGNED,
                       endianness=Endianness.LITTLE)
int16be = partialclass(Integer,
                       unitSize=UnitSize.SIZE_16,
                       sign=Sign.SIGNED,
                       endianness=Endianness.BIG)
int16le = partialclass(Integer,
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
int24be = partialclass(Integer,
                       unitSize=UnitSize.SIZE_24,
                       sign=Sign.SIGNED,
                       endianness=Endianness.BIG)
int24le = partialclass(Integer,
                       unitSize=UnitSize.SIZE_24,
                       sign=Sign.SIGNED,
                       endianness=Endianness.LITTLE)
uint24be = partialclass(Integer,
                        unitSize=UnitSize.SIZE_24,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.BIG)
uint24le = partialclass(Integer,
                        unitSize=UnitSize.SIZE_24,
                        sign=Sign.UNSIGNED,
                        endianness=Endianness.LITTLE)
int32be = partialclass(Integer,
                       unitSize=UnitSize.SIZE_32,
                       sign=Sign.SIGNED,
                       endianness=Endianness.BIG)
int32le = partialclass(Integer,
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
int64be = partialclass(Integer,
                       unitSize=UnitSize.SIZE_64,
                       sign=Sign.SIGNED,
                       endianness=Endianness.BIG)
int64le = partialclass(Integer,
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
int8, int16, int24, int32, int64 = int8be, int16be, int24be, int32be, int64be
uint8, uint16, uint24, uint32, uint64 = uint8be, uint16be, uint24be, uint32be, uint64be


def _test():
    r"""

    >>> from netzob.all import *
    >>> t = Integer()
    >>> print(t)
    Integer(-32768,32767)
    >>> t.size
    (-32768, 32767)
    >>> t.unitSize
    UnitSize.SIZE_16

    >>> t = Integer(interval=(4, 16))
    >>> print(t)
    Integer(4,16)

    >>> t = Integer(4)
    >>> print(t)
    Integer(4)


    Examples of Integer internal attribute access

    >>> from netzob.all import *
    >>> cDec = Integer(20)
    >>> print(repr(cDec))
    20
    >>> cDec.typeName
    'Integer'
    >>> cDec.value
    bitarray('0000000000010100')

    The required size in bits is automatically computed following the specifications:

    >>> dec = Integer(10)
    >>> dec.size
    (-32768, 32767)

    >>> dec = Integer(interval=(-120, 10))
    >>> dec.size
    (-120, 10)

    Symbol abstraction:

    >>> from netzob.all import Field, Symbol
    >>> domains = [
    ...     uint16(1), int8le(), int32be(0x007F0041), uint16le(2)
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(next(f.specialize()) for f in symbol.fields)
    >>> symbol.abstract(data)  #doctest: +ELLIPSIS
    OrderedDict([('0', b'\x00\x01'), ('1', b'...'), ('2', b'\x00\x7f\x00A'), ('3', b'\x02\x00')])


    # Verify that you cannot create an Integer with a value AND an interval:

    >>> i = Integer(2, interval=(2, 10))
    Traceback (most recent call last):
    ...
    ValueError: An Integer should have either its value or its interval set, but not both

    """


def _test_24_bits_integers():
    r"""

    >>> from netzob.all import *
    >>> t = Integer(unitSize=UnitSize.SIZE_24)
    >>> len(t.generate().tobytes())
    3

    >>> t = Integer(unitSize=UnitSize.SIZE_24, endianness=Endianness.LITTLE)
    >>> len(t.generate().tobytes())
    3

    >>> raw = b'\xff\xff\xff'
    >>> Integer.encode(raw, unitSize=UnitSize.SIZE_24, endianness=Endianness.BIG, sign=Sign.UNSIGNED)
    16777215

    >>> Integer.encode(raw, unitSize=UnitSize.SIZE_24, endianness=Endianness.LITTLE, sign=Sign.UNSIGNED)
    16777215

    >>> Integer.encode(raw, unitSize=UnitSize.SIZE_24, endianness=Endianness.BIG, sign=Sign.SIGNED)
    -1

    >>> Integer.encode(raw, unitSize=UnitSize.SIZE_24, endianness=Endianness.LITTLE, sign=Sign.SIGNED)
    -1

    """


def _test_weird_size():
    r"""

    >>> from netzob.all import *

    # This test should trigger an exception

    >>> domain = Integer(value=bitarray('10001001000011001001101'), unitSize=UnitSize.SIZE_24, endianness=Endianness.LITTLE, sign=Sign.UNSIGNED)
    >>> f       = Field(domain=domain, name="field")
    >>> symbol  = Symbol(fields=[f])
    >>> data    = next(symbol.specialize())
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.GenerationException: specialize() produced 23 bits, which is not aligned on 8 bits. You should review the symbol model.


    # This test should work

    >>> domain = Integer(value=bitarray('010001001000011001001101'), unitSize=UnitSize.SIZE_24, endianness=Endianness.LITTLE, sign=Sign.UNSIGNED)
    >>> f       = Field(domain=domain, name="field")
    >>> symbol  = Symbol(fields=[f])
    >>> data    = next(symbol.specialize())
    >>> data
    b'D\x86M'

    """

def _test_int_endianness():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> f1 = Field(domain=Raw(nbBytes=2), name="f1")
    >>> f2 = Field(name="f2")
    >>> f2.domain = Size([f1, f2], dataType=uint16le())
    >>> f1.domain.dataType.endianness
    Endianness.BIG
    >>> f2.domain.dataType.endianness
    Endianness.LITTLE
    >>> s0 = Symbol([f2, f1])
    >>> s1 = Symbol([f1, f2])
    >>> print(next(s0.specialize()).hex() + ' - ' + next(s1.specialize()).hex())
    0400f707 - ecfb0400

    """


def _test_specialize_abstract():
    r"""
    >>> from netzob.all import *
    >>> from collections import OrderedDict
    >>> Conf.apply()
    >>> from netzob.Model.Vocabulary.Types.AbstractType import test_type_one_parameter, test_type_multiple_parameters, test_type_specialize_abstract

    >>> data_type = Integer

    >>> possible_parameters = OrderedDict()
    >>> possible_parameters["value"] = [0, 42, -5, 24242]
    >>> possible_parameters["interval"] = [None, 3, (4, 10), (-10, 10), (20, 257)]
    >>> possible_parameters["unitSize"] = [UnitSize.SIZE_8, UnitSize.SIZE_16, UnitSize.SIZE_24, UnitSize.SIZE_32, UnitSize.SIZE_64]
    >>> possible_parameters["endianness"] = [Endianness.LITTLE, Endianness.BIG]
    >>> possible_parameters["sign"] = [Sign.SIGNED, Sign.UNSIGNED]
    >>> possible_parameters["default"] = [None, 0, 44, -10]

    >>> test_type_one_parameter(data_type, possible_parameters)

    >>> possible_parameters = OrderedDict()
    >>> possible_parameters["value"] = [0, 42]
    >>> possible_parameters["interval"] = [None, (4, 10), (-10, 10), (20, 257)]
    >>> possible_parameters["unitSize"] = [UnitSize.SIZE_8, UnitSize.SIZE_16, UnitSize.SIZE_24, UnitSize.SIZE_32, UnitSize.SIZE_64]
    >>> possible_parameters["endianness"] = [Endianness.LITTLE, Endianness.BIG]
    >>> possible_parameters["sign"] = [Sign.SIGNED, Sign.UNSIGNED]
    >>> possible_parameters["default"] = [None, 0, 44, -10]

    >>> (parameter_names, functional_combinations_possible_parameters) = test_type_multiple_parameters(data_type, possible_parameters)

    >>> test_type_specialize_abstract(data_type, parameter_names, functional_combinations_possible_parameters)

    """
