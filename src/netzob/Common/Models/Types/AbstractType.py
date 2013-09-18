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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class AbstractType(object):

    __metaclass__ = abc.ABCMeta

    # FEW KEY ELEMENTS
    ENDIAN_BIG = 'big'
    ENDIAN_LITTLE = 'little'
    SIGN_SIGNED = 'signed'
    SIGN_UNSIGNED = 'unsigned'
    UNITSIZE_1 = '1'
    UNITSIZE_4 = '4'
    UNITSIZE_8 = '8'
    UNITSIZE_16 = '16'
    UNITSIZE_32 = '32'
    UNITSIZE_64 = '64'

    @staticmethod
    def supportedTypes():
        """Official list of supported types"""
        from netzob.Common.Models.Types.ASCII import ASCII
        from netzob.Common.Models.Types.Raw import Raw
        from netzob.Common.Models.Types.BitArray import BitArray
        from netzob.Common.Models.Types.Decimal import Decimal
        from netzob.Common.Models.Types.HexaString import HexaString

        return [
            # an array of bits: [1,0,0,1,1,0..]
            BitArray,
            # original python way of encoding data, raw data
            Raw,
            # string data
            ASCII,
            # decimal
            Decimal,
            # hexstring
            HexaString,
        ]

    @staticmethod
    def supportedUnitSizes():
        """Official unit sizes"""
        return [
            AbstractType.UNITSIZE_1,
            AbstractType.UNITSIZE_4,
            AbstractType.UNITSIZE_8,
            AbstractType.UNITSIZE_16,
            AbstractType.UNITSIZE_32,
            AbstractType.UNITSIZE_64
        ]

    @staticmethod
    def supportedEndianness():
        """Official endianness supported"""
        return [
            AbstractType.ENDIAN_BIG,
            AbstractType.ENDIAN_LITTLE
        ]

    @staticmethod
    def supportedSign():
        """Official sign supported"""
        return [
            AbstractType.SIGN_SIGNED,
            AbstractType.SIGN_UNSIGNED
        ]

    @staticmethod
    def defaultUnitSize():
        """Return the default unit size

        :return: the default unit size
        :rtype: str
        """
        return AbstractType.UNITSIZE_8

    @staticmethod
    def defaultEndianness():
        """Return the default endianness

        :return: the default endianness
        :rtype: str
        """
        return AbstractType.ENDIAN_LITTLE

    @staticmethod
    def defaultSign():
        """Return the default sign

        :return: the default sign
        :rtype: str
        """
        return AbstractType.SIGN_SIGNED

    def __init__(self, typeName, value, size=(None, None)):
        self.typeName = typeName
        self.value = value
        self.size = size

    @staticmethod
    @abc.abstractmethod
    def decode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the specified data in python raw format.

        :param data: the data encoded in current type which will be decoded in raw
        :type data: the current type
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
        raise NotImplementedError("'decode' method not implemented")

    @staticmethod
    @abc.abstractmethod
    def encode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the python raw data to the current type.

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
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
        raise NotImplementedError("'encode' method not implemented")

    @staticmethod
    @abc.abstractmethod
    def canParse(data):
        """This method computes if the specified data can be parsed
        with the current type.

        :param data: the data encoded in python raw to check
        :type data: python raw
        :return: True if the data can be parsed will the curren type
        :rtype: bool
        """
        raise NotImplementedError("'canParse' method not implemented")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def size(self):
        """The size of the expected Type defined
         by a tuple (min, max).
         Instead of a tuple, an int can be used to represent both min and max value.

         The value 'None' can be set for min and/or max to represent no limitations.

         For instance, to create an ASCII field of at least 10 chars:

         >>> from netzob.all import *
         >>> f = Field(ASCII(size=(10,None)))
         >>> f.domain.size
         (80, None)

         while to create a Raw field which content has no specific limit:

         >>> from netzob.all import *
         >>> f = Field(Raw())

         :type: tuple (int, int)
         :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.

         """
        return self.__size

    @size.setter
    def size(self, size):

        if size is None:
            size = (None, None)
        if isinstance(size, int):
            size = (size, size)

        if isinstance(size, tuple):
            minSize, maxSize = size

            if minSize is not None and not isinstance(minSize, int):
                raise TypeError("Size must be defined with a tuple of int")
            if maxSize is not None and not isinstance(maxSize, int):
                raise TypeError("Size must be defined with a tuple of int")

            if minSize is None:
                minSize = 0

            if minSize < 0:
                raise ValueError("Minimum size must be greater than 0")
            if maxSize is not None and maxSize < minSize:
                raise ValueError("Maximum must be greater or equals to the minimum")

            self.__size = (minSize, maxSize)
        else:
            raise TypeError("Size must be defined by a tuple an int or with None")

    @staticmethod
    def normalize(data):
        """Given the specified data, this static methods normalize its representation
        using Netzob types.

        :parameter data: the data to normalize
        :type data: :class:`object`
        :return: an abstractType which value is data
        :rtype: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`

        >>> from netzob.all import *
        >>> normalizedData = AbstractType.normalize("netzob")
        >>> print normalizedData.__class__
        <class 'netzob.Common.Models.Types.ASCII.ASCII'>
        >>> print normalizedData.value
        netzob
        """

        if data is None:
            raise TypeError("Cannot normalize None data")

        if isinstance(data, int):
            from netzob.Common.Models.Types.Decimal import Decimal
            data = Decimal(value=data)
        elif isinstance(data, str):
            from netzob.Common.Models.Types.ASCII import ASCII
            data = ASCII(value=data)
        if isinstance(data, AbstractType):
            return data
        else:
            raise TypeError("Not a valid data")

    @abc.abstractmethod
    def buildDataRepresentation(self):
        """It creates a :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data.Data` following the specified type.

        for instance, user can specify a domain with its type which is much more simple than creating a Data with the type

        >>> from netzob.all import *
        >>> ascii = ASCII("hello netzob !")
        >>> print ascii.typeName
        ASCII
        >>> data = ascii.buildDataRepresentation()
        >>> print TypeConverter.convert(data.currentValue, BitArray, ASCII)
        hello netzob !
        >>> print data.dataType.__name__
        ASCII

        :return: a Data of the current type
        :rtype: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Leads.Data.Data`

        """
        return

    @property
    def typeName(self):
        """The name of the implemented type. We recommend
        to set this value with the name of :  Type.__class__.__name__.

        :type: `str`
        :raises: :class: `TypeError` if typeName is not an str
        """
        return self.__typeName

    @typeName.setter
    @typeCheck(str)
    def typeName(self, typeName):
        if typeName is None:
            raise TypeError("typeName cannot be None")
        self.__typeName = typeName
