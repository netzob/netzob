# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Types.AbstractType import AbstractType


class Raw(AbstractType):
    """Raw netzob data type expressed in bytes.

    For instance, we can use this type to parse any raw field of 2 bytes:

    >>> from netzob.all import *
    >>> f = Field(Raw(nbBytes=2))

    or with a specific value (default is little endianness)

    >>> f = Field(Raw('\\x01\\x02\\x03'))
    >>> print(f.domain.dataType)
    Raw=b'\\x01\\x02\\x03' ((0, 24))

    >>> f.domain.dataType.endianness = AbstractType.ENDIAN_BIG
    >>> print(f.domain.dataType)
    Raw=b'\\x01\\x02\\x03' ((0, 24))

    """

    def __init__(self, value=None, nbBytes=None, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            if isinstance(value, str):
                value = TypeConverter.convert(bytes(value, "utf-8"), Raw, BitArray)
            elif isinstance(value, bytes):
                value = TypeConverter.convert(value, Raw, BitArray)

        nbBits = self._convertNbBytesinNbBits(nbBytes)

        super(Raw, self).__init__(self.__class__.__name__, value, nbBits, unitSize=unitSize, endianness=endianness, sign=sign)

    def __str__(self):
        if self.value is not None:
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            from netzob.Model.Types.HexaString import HexaString
            return "{0}={1} ({2})".format(self.typeName, repr(TypeConverter.convert(self.value, BitArray, Raw)), self.size)
        else:
            return "{0}={1} ({2})".format(self.typeName, self.value, self.size)

    def __repr__(self):
        """
        >>> from netzob.all import *
        >>> f = Field(Raw("\\x01\\x02\\x03\\x04"))
        >>> s = Symbol(fields=[f])
        >>> messages = [RawMessage(s.specialize()) for x in range(5)]
        >>> s.messages = messages
        >>> print(s)
        Field             
        ------------------
        '\\x01\\x02\\x03\\x04'
        '\\x01\\x02\\x03\\x04'
        '\\x01\\x02\\x03\\x04'
        '\\x01\\x02\\x03\\x04'
        '\\x01\\x02\\x03\\x04'
        ------------------

        """
        if self.value is not None:
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            return str(TypeConverter.convert(self.value, BitArray, self.__class__))
        else:
            return str(self.value)

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

    def generate(self, generationStrategy=None):
        """Generates a random Raw that respects the requested size.

        >>> from netzob.all import *
        >>> a = Raw(nbBytes=(10))
        >>> gen = a.generate()
        >>> print(len(gen))
        80

        >>> from netzob.all import *
        >>> a = Raw(nbBytes=(10, 20))
        >>> gen = a.generate()
        >>> print(10<=len(gen) and 20<=len(gen))
        True



        """
        from netzob.Model.Types.TypeConverter import TypeConverter
        from netzob.Model.Types.BitArray import BitArray

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize, maxSize)
        return TypeConverter.convert(os.urandom(int(generatedSize / 8)), Raw, BitArray)

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        return data

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        return data

    @staticmethod
    def canParse(data):
        """Computes if specified data can be parsed as raw which is always the case if the data is at least 1 length and aligned on a byte.

        >>> from netzob.all import *
        >>> Raw.canParse(TypeConverter.convert("hello netzob", ASCII, BitArray))
        True

        The ascii table is defined from 0 to 127:
        >>> Raw.canParse(TypeConverter.convert(128, Integer, BitArray, src_sign=AbstractType.SIGN_UNSIGNED))
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        if len(data) % 8 != 0:
            return False

        return True

