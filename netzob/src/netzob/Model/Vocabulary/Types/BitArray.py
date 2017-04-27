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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


@NetzobLogger
class BitArray(AbstractType):
    r"""This class defines a BitArray type.

    The BitArray type allows to describe a field that contains a
    sequence of bits of arbitrary sizes.

    The BitArray constructor expects some parameters:

    :param value: The current value of the type instance.
    :param nbBits: The size in bits that this value can take.
    :type value: :class:`bitarray.bitarray`, optional
    :type nbBits: an :class:`int` or a tupple with the min and the max size specified as :class:`int`, optional


    The two following examples show how to define a field with a
    BitArray. Both examples are equivalent. The second one is just
    more concise.

    >>> from netzob.all import *  
    >>> f1 = Field(BitArray(bitarray('00001111')))
    >>> f1.specialize()
    b'\x0f'

    >>> f1 = Field(bitarray('00001111'))
    >>> f1.specialize()
    b'\x0f'


    The following example shows how to define a bitfield of 1 bit, 47
    bits, 64 bits and then a field that accept a bitfield of variable
    size between 13 and 128 bits:

    >>> f1 = Field(BitArray(nbBits=1))
    >>> print(len(f1.domain.dataType.generate()))
    1

    >>> f2 = Field(BitArray(nbBits=47))
    >>> print(len(f2.domain.dataType.generate()))
    47

    >>> f3 = Field(BitArray(nbBits=64))
    >>> print(len(f3.domain.dataType.generate()))
    64

    >>> f4 = Field(BitArray(nbBits=(13, 128)))

    The following example shows how to specify a constant bitfield:

    >>> from bitarray import bitarray
    >>> b = BitArray(value = bitarray('00000000'))
    >>> print(b.generate())
    bitarray('00000000')

    """

    def __init__(self, value=None, nbBits=(None, None)):
        super(BitArray, self).__init__(self.__class__.__name__, value, nbBits)

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """For the moment its always true because we consider
        the decimal type to be very similar to the raw type.

        >>> from netzob.all import *

        >>> BitArray().canParse(TypeConverter.convert("hello netzob", ASCII, BitArray))
        True

        >>> b = BitArray(nbBits=8)
        >>> b.canParse(bitarray('01010101'))
        True

        >>> b.canParse(bitarray('010101011'))
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a BitArray
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if not isinstance(data, bitarray):
            raise TypeError("Data should be a python raw ({0}:{1})".format(
                data, type(data)))

        if len(data) == 0:
            return False

        (nbMinBits, nbMaxBits) = self.size

        nbBitsData = len(data)

        if nbMinBits is not None and nbMinBits > nbBitsData:
            return False
        if nbMaxBits is not None and nbMaxBits < nbBitsData:
            return False

        return True

    def generate(self, generationStrategy=None):
        """Generates a random bitarray that respects the constraints.
        """

        if self.value is not None:
            return self.value

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize, maxSize)
        randomContent = [random.randint(0, 1) for i in range(0, generatedSize)]
        return bitarray(randomContent, endian=self.endianness)

    @staticmethod
    @typeCheck(bitarray)
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.BitArray import BitArray
        >>> d = ASCII.decode("hello netzob")
        >>> r = BitArray.encode(d)
        >>> print(r.to01())
        011010000110010101101100011011000110111100100000011011100110010101110100011110100110111101100010
        >>> t = BitArray.decode(r)
        >>> print(t)
        b'hello netzob'


        :param data: the data encoded in BitArray which will be decoded in raw
        :type data: bitarray
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
        return data.tobytes()

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the BitArray.

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.BitArray import BitArray
        >>> BitArray.encode(Integer.decode(20))
        bitarray('00010100')

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in BitArray
        :rtype: :class:`BitArray <netzob.Model.Vocabulary.Types.BitArray.BitArray>`
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        if endianness == AbstractType.ENDIAN_BIG:
            endian = 'big'
        elif endianness == AbstractType.ENDIAN_LITTLE:
            endian = 'little'
        else:
            raise ValueError("Invalid endianness value")

        if isinstance(data, bytes):
            norm_data = data
        elif isinstance(data, str):
            norm_data = bytes(data, "utf-8")
        else:
            raise TypeError("Invalid type for: '{}'. Expected bytes or str, and got '{}'".format(data, type(data)))
            
        b = bitarray(endian=endian)
        b.frombytes(norm_data)
        return b
