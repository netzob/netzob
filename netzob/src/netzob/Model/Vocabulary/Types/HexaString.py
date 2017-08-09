#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
import binascii
import unittest
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.String import String


class HexaString(AbstractType):
    r"""This class defines a HexaString type.

    The HexaString type describes a sequence of bytes of
    arbitrary sizes with the hexastring notation (e.g. ``b'aabbcc'``
    instead of the raw notation ``b'\xaa\xbb\xcc'``).

    The HexaString constructor expects some parameters:

    :param value: The current value of the type instance.
    :param nbBytes: The size in bytes that this value can take.
    :type value: :class:`bitarray.bitarray` or :class:`bytes`, optional
    :type nbBytes: an :class:`int` or a tuple with the min and the max size specified as :class:`int`, optional


    The HexaString class provides the following public variables:

    :var typeName: The name of the implemented data type.
    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size in bits of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max value.
    :vartype typeName: :class:`str`
    :vartype value: :class:`bitarray.bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`


    The following example shows how to define a hexastring field with
    a constant value, and the use of the specialization method:

    >>> from netzob.all import *
    >>> f = Field(HexaString(b"aabbcc"))
    >>> f.specialize()
    b'\xaa\xbb\xcc'

    The following example shows how to define a hexastring field with
    a variable value, and the use of the specialization method:

    >>> from netzob.all import *
    >>> f = Field(HexaString(nbBytes=6))
    >>> len(f.specialize())
    6

    """


    def __init__(self,
                 value=None,
                 nbBytes=(None, None),
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):

        if value is not None and not isinstance(value, bitarray):
            if isinstance(value, bytes):
                from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
                from netzob.Model.Vocabulary.Types.BitArray import BitArray
                value = TypeConverter.convert(value, HexaString, BitArray)
            else:
                raise ValueError("Unsupported input format for value: '{}', type is: '{}', expected type is 'bitarray' or 'bytes'".format(value, type(value)))

        # Handle data size if value is None
        if value is None:
            nbBits = self._convertNbBytesinNbBits(nbBytes)
        else:
            nbBits = (None, None)

        super(HexaString, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def _convertNbBytesinNbBits(self, nbBytes):
        nbMinBit = None
        nbMaxBit = None
        if nbBytes is not None:
            if isinstance(nbBytes, int):
                nbMinBit = nbBytes * 8
                nbMaxBit = nbMinBit
            else:
                if nbBytes[0] is not None:
                    nbMinBit = nbBytes[0] * 8
                if nbBytes[1] is not None:
                    nbMaxBit = nbBytes[1] * 8
        return (nbMinBit, nbMaxBit)

    def canParse(self, data):
        r"""It verifies the value is a string which only includes hexadecimal
        values.

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a hexastring
        :rtype: bool
        :raise: TypeError if the data is None

        >>> from netzob.all import *
        >>> HexaString(b"aabbccdd").canParse(b"aabbccdd")
        True

        >>> HexaString(b"aabbccdd").canParse(b"aabbccddee")
        False

        >>> HexaString().canParse(b"aa")
        True

        >>> HexaString().canParse(b"aab")
        Traceback (most recent call last):
        ...
        Exception: The data 'b'aab'' should be aligned on the octet

        >>> HexaString(nbBytes=4).canParse(b"aabbccdd")
        True

        >>> HexaString(nbBytes=4).canParse(b"aa")
        False

        Let's generate random binary raw data, convert it to HexaString
        and verify we can parse this

        >>> import os
        >>> # Generate 8 random bytes
        >>> randomData = os.urandom(8)
        >>> hex = Raw(randomData).convert(HexaString)
        >>> len(hex.value)
        64
        >>> HexaString().canParse(hex.value)
        True

        A more complete example with the use of the abstract() method:

        >>> domain = HexaString(nbBytes=2)
        >>> data = b"aabb"
        >>> domain.canParse(data)
        True
        >>> spec_data = Symbol(fields=[Field(domain)])
        >>> data = b"\xaa\xbb"
        >>> Symbol.abstract(data, [spec_data])
        (Symbol, OrderedDict([('Field', b'\xaa\xbb')]))

        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        # Check if data is in bytes and normalize it in bitarray
        if not isinstance(data, bitarray):
            if isinstance(data, bytes):
                from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
                from netzob.Model.Vocabulary.Types.BitArray import BitArray
                bits_data = TypeConverter.convert(data, HexaString, BitArray)
                data = bits_data
            else:
                raise ValueError("Unsupported input format for data: '{}', type: '{}'".format(data, type(data)))

        # Compare with self.value if it is defined
        if self.value is not None:
            return self.value == data

        # Else, compare with expected size
        (minBits, maxBits) = self.size

        if minBits is not None:
            if len(data) < (minBits):
                return False
        if maxBits is not None:
            if len(data) > (maxBits):
                return False

        # And verify if content matches the expected hexastring permitted characters
        allowedValues = [str(i) for i in range(0, 10)]
        allowedValues.extend(["a", "b", "c", "d", "e", "f"])

        hexa_data = binascii.hexlify(data.tobytes())
        for i in range(0, len(hexa_data)):
            if not chr(hexa_data[i]) in allowedValues:
                return False

        return True

    @staticmethod
    @typeCheck(str)
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the specified data in hexastring format.

        >>> from netzob.all import *
        >>> import os

        >>> # Generate 1024 random bytes
        >>> randomData = os.urandom(1024)

        >>> # Convert to hexastring
        >>> hex = Raw(randomData).convert(HexaString)
        >>> len(hex.value)
        8192

        >>> # Convert back to byte and verify we didn't lost anything
        >>> raw = hex.convert(Raw)
        >>> raw.value.tobytes() == randomData
        True


        :param data: the data encoded in hexaString (str) which will be decoded in raw
        :type data: str
        :keyword unitSize: the unit size of the specified data
        :type unitSize: :class:`UnitSize <netzob.Model.Vocabulary.Types.UnitSize.UnitSize>`
        :keyword endianness: the endianness of the specified data
        :type endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.Endianness.Endianness>`
        :keyword sign: the sign of the specified data
        :type sign: :class:`Sign <netzob.Model.Vocabulary.Types.Sign.Sign>`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        if len(data) % 2 != 0:
            raise Exception("The data '{}' should be aligned on the octet".format(data))

        return binascii.unhexlify(data)

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the python raw data to a HexaString

        >>> from netzob.all import *
        >>> import os

        >>> # Generate 4096 random bytes
        >>> randomData = os.urandom(4096)
        >>> # Convert to hexastring
        >>> hex = Raw(randomData).convert(HexaString)
        >>> len(hex.value)
        32768
        >>> # Convert back to byte and verify we didn't lost anything
        >>> raw = hex.convert(Raw)
        >>> raw.value.tobytes() == randomData
        True

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: :class:`Enum`
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: :class:`Enum`
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

        :return: data encoded in Hexa String
        :rtype: python str
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        return binascii.hexlify(data)


class __TestHexaString(unittest.TestCase):
    """
    Test class with test-only scenario that should not be documented.
    """

    def test_abstraction_arbitrary_values(self):
        from netzob.all import Field, Symbol
        domains = [
            HexaString(b"aabb"), HexaString(nbBytes=4),
        ]
        symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
        data = b''.join(f.specialize() for f in symbol.fields)
        assert Symbol.abstract(data, [symbol])[1]
