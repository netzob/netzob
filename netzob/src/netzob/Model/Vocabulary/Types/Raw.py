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
import random
import os
import unittest
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class Raw(AbstractType):
    r"""This class defines a Raw type.

    The Raw type describes a sequence of bytes of arbitrary
    sizes.

    The Raw constructor expects some parameters:

    :param value: The current value of the type instance.
    :param nbBytes: The size in bytes that this value can take.
    :param alphabet: The alphabet can be used to limit the bytes that can participate in the domain value.
    :param unitSize: Not implemented.
    :param endianness: Not implemented.
    :param sign: Not implemented.
    :type value: :class:`bitarray.bitarray`, optional
    :type nbBytes: an :class:`int` or a tuple with the min and the max size specified as :class:`int`, optional
    :type alphabet: a :class:`list` of :class:`object`, optional

    The following example shows how to define a six bytes long raw
    field, and the used of the specialization method to generate a
    value:

    >>> from netzob.all import *
    >>> f = Field(Raw(nbBytes=6))
    >>> print(len(f.specialize()))
    6

    Netzob can define a range, regarding the valid size of the
    raw field:

    >>> f = Field(Raw(nbBytes = (2, 20)))

    The following example shows the specification of a constant for a
    field:

    >>> f = Field(Raw(b'\x01\x02\x03'))
    >>> print(f.domain.dataType)
    Raw=b'\x01\x02\x03' ((None, None))

    The alphabet optional argument can be used to limit the bytes that
    can participate in the domain value:

    >>> f = Field(Raw(nbBytes=100, alphabet=["t", "o"]))
    >>> data = f.specialize()
    >>> data_set = set(data)
    >>> print(data_set)
    {116, 111}

    """

    def __init__(self,
                 value=None,
                 nbBytes=None,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign(),
                 alphabet=None):

        if value is not None and not isinstance(value, bitarray):
            if isinstance(value, bytes):
                tmp_value = value
                value = bitarray(endian='big')
                value.frombytes(tmp_value)
            else:
                raise ValueError("Unsupported input format for value: '{}', type is: '{}', expected type is 'bitarray' or 'bytes'".format(value, type(value)))

        # Handle raw data size if value is None
        if value is None:
            nbBits = self._convertNbBytesinNbBits(nbBytes)
        else:
            nbBits = (None, None)

        self.alphabet = alphabet
        
        super(Raw, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def __str__(self):
        if self.value is not None:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            from netzob.Model.Vocabulary.Types.HexaString import HexaString
            return "{0}={1} ({2})".format(
                self.typeName,
                repr(TypeConverter.convert(self.value, BitArray, Raw)),
                self.size)
        else:
            return "{0}={1} ({2})".format(self.typeName, self.value, self.size)

    def __repr__(self):
        r"""
        >>> from netzob.all import *
        >>> f = Field(Raw(b"\x01\x02\x03\x04"))
        >>> s = Symbol(fields=[f])
        >>> messages = [RawMessage(s.specialize()) for x in range(5)]
        >>> s.messages = messages
        >>> print(s.str_data())
        Field             
        ------------------
        '\x01\x02\x03\x04'
        '\x01\x02\x03\x04'
        '\x01\x02\x03\x04'
        '\x01\x02\x03\x04'
        '\x01\x02\x03\x04'
        ------------------

        """
        if self.value is not None:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            return str(
                TypeConverter.convert(self.value, BitArray, self.__class__))
        else:
            return str(self.value)

    def _convertNbBytesinNbBits(self, nbBytes):
        nbMinBit = 0
        nbMaxBit = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
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

    def generate(self, generationStrategy=None):
        """Generates a random Raw that respects the requested size or the
        predefined value.

        >>> from netzob.all import *
        >>> a = Raw(nbBytes=(10))
        >>> gen = a.generate()
        >>> print(len(gen))
        80

        >>> a = Raw(nbBytes=(10, 20))
        >>> gen = a.generate()
        >>> print(10<=len(gen) and 20<=len(gen))
        True

        >>> a = Raw(b"a")
        >>> a.generate()
        bitarray('01100001')

        >>> a = Raw(b"\x01")
        >>> a.generate()
        bitarray('00000001')

        """

        if self.value is not None:
            return self.value

        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize, maxSize)

        generatedValue = None
        if self.alphabet is None:
            generatedValue = os.urandom(int(generatedSize / 8))
        else:
            generatedValue = "".join([random.choice(self.alphabet) for _ in range(int(generatedSize / 8))])
            
        return TypeConverter.convert(generatedValue, Raw, BitArray)

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        return data

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        return data

    def canParse(self, data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """Computes if specified data can be parsed as raw which is always the
        case if the data is at least 1 length and aligned on a byte.

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None

        >>> from netzob.all import *
        >>> Raw().canParse(TypeConverter.convert("hello netzob", String, BitArray))
        True

        >>> Raw().canParse(b"hello netzob")
        True

        >>> Raw(b"hello").canParse(b"hello")
        True

        >>> Raw(b"hello").canParse(b"hello!")
        False

        >>> Raw(nbBytes=10).canParse(b"1234567890")
        True

        >>> Raw(nbBytes=10).canParse(b"123456789")
        False

        >>> Raw(nbBytes=(10, 1234)).canParse(b"123456789012345")
        True

        >>> Raw(nbBytes=(10, 1234)).canParse(b"aaaa")
        False

        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        # Check if data is in bytes and normalize it in bitarray
        if not isinstance(data, bitarray):
            if isinstance(data, bytes):
                tmp_data = data
                data = bitarray(endian='big')
                data.frombytes(tmp_data)
            else:
                raise ValueError("Unsupported input format for data: '{}', type: '{}'".format(data, type(data)))

        # Compare with self.value if it is defined
        if self.value is not None:
            if self.value == data:
                return True
            else:
                return False

        # Else, compare with expected size
        if len(data) % 8 != 0:
            return False

        # At this time, data is a bitarray
        rawData = data.tobytes()

        (minBits, maxBits) = self.size
        if minBits is not None:
            if len(rawData) < (minBits/8):
                return False
        if maxBits is not None:
            if len(rawData) > (maxBits/8):
                return False

        if self.alphabet is not None:
            data_set = set(data)
            for element in data_set:
                if element not in self.alphabet:
                    return False

        return True


class __TestRaw(unittest.TestCase):
    """
    Test class with test-only scenario that should not be documented.
    """

    def test_abstraction_arbitrary_values(self):
        from netzob.all import Field, Symbol
        domains = [
            Raw(b"xxxx"), Raw(nbBytes=2),
        ]
        symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
        data = b''.join(f.specialize() for f in symbol.fields)
        assert Symbol.abstract(data, [symbol])[1]
