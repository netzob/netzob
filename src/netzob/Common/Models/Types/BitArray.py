#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.Raw import Raw


@NetzobLogger
class BitArray(AbstractType):
    """A bitarray netzob type.

    It represents a set of bits with possible constraints.
    """

    def __init__(self, value=None, nbBits=(None, None)):
        super(BitArray, self).__init__(self.__class__.__name__, value, nbBits)

    @typeCheck(bitarray, str, str, str)
    def canParse(self, data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """For the moment its always true because we consider
        the decimal type to be very similar to the raw type.

        >>> from netzob.all import *
        >>> BitArray().canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        >>> b = BitArray(nbBits=8)
        >>> b.canParse(TypeConverter.convert(bitarray('01010101'), BitArray, Raw))
        True

        >>> b.canParse(TypeConverter.convert(bitarray('010101011'), BitArray, Raw))
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a BitArray
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

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
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> from netzob.Common.Models.Types.BitArray import BitArray
        >>> d = ASCII.decode("hello netzob")
        >>> r = BitArray.encode(d)
        >>> print r.to01()
        000101101010011000110110001101101111011000000100011101101010011000101110010111101111011001000110
        >>> t = BitArray.decode(r)
        >>> print t
        hello netzob


        :param data: the data encoded in BitArray which will be decoded in raw
        :type data: bitarray
        :keyword unitSize: the unit size of the specified data
        :type unitSize: :class:`netzob.Common.Models.Types.UnitSize.UnitSize`
        :keyword endianness: the endianness of the specified data
        :type endianness: :class:`netzob.Common.Models.Types.Endianness.Endianness`
        :keyword sign: the sign of the specified data
        :type sign: :class:`netzob.Common.Models.Types.Sign.Sign`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")
        return data.tobytes()

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the BitArray.

        >>> from netzob.all import *
        >>> from netzob.Common.Models.Types.BitArray import BitArray
        >>> BitArray.encode(Decimal.decode(20))
        bitarray('00101000')

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in BitArray
        :rtype: :class:`netzob.Common.Models.Types.BitArray.BitArray`
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

        b = bitarray(endian=endian)            
        b.frombytes(data)
        return b
