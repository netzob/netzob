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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
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
from bitarray import bitarray
import random
import collections
from enum import Enum
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Scope import Scope


@public_api
class Endianness(Enum):
    """Enum class used to specify the endianness of a type.
    """
    BIG = 'big'
    """Endianness.BIG can be used to specify a BIG endianness of a type."""
    LITTLE = 'little'
    """Endianness.LITTLE can be used to specify a LITTLE endianness of a type."""
    __repr__ = Enum.__str__


@public_api
class Sign(Enum):
    """Enum class used to specify the sign of a type.
    """
    SIGNED = 'signed'
    """Sign.SIGNED can be used to specify a SIGNED sign of a type."""
    UNSIGNED = 'unsigned'
    """Sign.UNSIGNED can be used to specify a UNSIGNED sign of a type."""
    __repr__ = Enum.__str__


@public_api
class UnitSize(Enum):
    """Enum class used to specify the unit size of a type (i.e. the space in bits that a unitary element takes up).
    """
    SIZE_1 = 1
    """UnitSize.SIZE_1 can be used to specify a 1-bit unit size of a type."""
    SIZE_4 = 4
    """UnitSize.SIZE_4 can be used to specify a 4-bit unit size of a type."""
    SIZE_8 = 8
    """UnitSize.SIZE_8 can be used to specify a 8-bit unit size of a type."""
    SIZE_16 = 16
    """UnitSize.SIZE_16 can be used to specify a 16-bit unit size of a type."""
    SIZE_24 = 24
    """UnitSize.SIZE_24 can be used to specify a 24-bit unit size of a type."""
    SIZE_32 = 32
    """UnitSize.SIZE_32 can be used to specify a 32-bit unit size of a type."""
    SIZE_64 = 64
    """UnitSize.SIZE_64 can be used to specify a 64-bit unit size of a type."""
    __repr__ = Enum.__str__


@NetzobLogger
class AbstractType(object, metaclass=abc.ABCMeta):
    """AbstractType is the abstract class of all the classes that represent Netzob types.

    A type defines a definition domain as a unique value or specified
    with specific rules.  For instance, an integer under a specific
    interval, a string with a number of chars and an IPv4 of a
    specific netmask.

    """

    # This value will be used if generate() method is called
    # without any upper size limit
    # 65536 bits (which equals to 2^16 bits) is a completly arbitrary value used to limit data generation
    MAXIMUM_GENERATED_DATA_SIZE = 1 << 16

    # This value fixes a limit to the possible values a type can
    # generate. This limit corresponds to 1 day of data generation
    # based on a generation bandwith of 1 millions per seconds. Therefore: max = 1.000.000 * 3600 * 24
    MAXIMUM_POSSIBLE_VALUES = 86400000000

    @staticmethod
    def supportedUnitSizes():
        """Official unit sizes"""
        return [
            UnitSize.SIZE_1, UnitSize.SIZE_4,
            UnitSize.SIZE_8, UnitSize.SIZE_16,
            UnitSize.SIZE_24, UnitSize.SIZE_32,
            UnitSize.SIZE_64
        ]

    @staticmethod
    def getUnitSizeEnum(size):
        """Returns the enum value corresponding to the given size.
        If size is invalid, returns None."""
        if size == 1:
            return UnitSize.SIZE_1
        elif size == 4:
            return UnitSize.SIZE_1
        elif size == 4:
            return UnitSize.SIZE_4
        elif size == 8:
            return UnitSize.SIZE_8
        elif size == 16:
            return UnitSize.SIZE_16
        elif size == 24:
            return UnitSize.SIZE_24
        elif size == 32:
            return UnitSize.SIZE_32
        elif size == 64:
            return UnitSize.SIZE_64
        return None

    @staticmethod
    def supportedEndianness():
        """Official endianness supported"""
        return [Endianness.BIG, Endianness.LITTLE]

    @staticmethod
    def supportedSign():
        """Official sign supported"""
        return [Sign.SIGNED, Sign.UNSIGNED]

    @staticmethod
    def defaultUnitSize():
        """Return the default unit size

        :return: the default unit size
        :rtype: :class:`Enum`
        """
        return UnitSize.SIZE_8

    @staticmethod
    def defaultEndianness():
        """Return the default endianness

        :return: the default endianness
        :type endianness: :class:`Enum`
        """
        return Endianness.BIG

    @staticmethod
    def defaultSign():
        """Return the default sign

        :return: the default sign
        :type sign: :class:`Enum`
        """
        return Sign.SIGNED

    @public_api
    def __init__(self,
                 typeName,
                 value,
                 size=(None, None),
                 unitSize=None,
                 endianness=None,
                 sign=None,
                 default=None):
        self.typeName = typeName
        self.value = value

        # Handle endianness and sign attributes
        if endianness is None:
            endianness = AbstractType.defaultEndianness()
        self.endianness = endianness
        if sign is None:
            sign = AbstractType.defaultSign()
        self.sign = sign

        # Handle size attribute
        self.size = size

        # Compute unit size (i.e. the size used to store the length attribute of the current object)
        if self.value is None:
            value_length = 0
        else:
            value_length = len(self.value)
        if self.size[1] is None:
            size_max = 0
        else:
            size_max = self.size[1]

        unitSize_tmp = AbstractType.computeUnitSize(max(value_length, size_max))  # Compute unit size according to the maximum length

        # Check consistency of provided unitSize value according to the computed one
        if unitSize is None:
            self.unitSize = unitSize_tmp
        else:
            if unitSize.value < unitSize_tmp.value:
                raise ValueError("Provided unitSize '{}' is too small to encode the maximum length of the potential values to generate (unitSize should be: '{}')".format(unitSize, unitSize_tmp))
            else:
                self.unitSize = unitSize

        # Handle default attribute
        self.default = default

    def __str__(self):
        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        if self.value is not None:
            return "{}={}".format(
                self.typeName,
                TypeConverter.convert(self.value, BitArray,
                                      self.__class__))
        else:
            if self.size[0] == self.size[1]:
                return "{}(nbBits={})".format(self.typeName, self.size[0])
            else:
                return "{}(nbBits=({},{})".format(self.typeName, self.size[0], self.size[1])

    def __repr__(self):
        if self.value is not None:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            return str(
                TypeConverter.convert(self.value, BitArray, self.__class__,
                                      dst_unitSize=self.unitSize,
                                      dst_endianness=self.endianness,
                                      dst_sign=self.sign))
        else:
            return str(self.value)

    def __key(self):
        # Note: as bitarray objects cannot be hashed in Python3 (because bitarray objects are mutable), we cast a bitarray object in a tuple (which is immutable)
        if self.value is None:
            return (self.typeName, self.size, self.unitSize,
                    self.endianness, self.sign)
        else:
            return (self.typeName, tuple(self.value), self.size, self.unitSize,
                    self.endianness, self.sign)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @abc.abstractmethod
    def count(self):
        r"""The :meth:`count` method computes the number of unique
        elements the data type can produce.

        :return: The number of unique elements the data type can produce.
        :rtype: :class:`int`

        """
        raise NotImplementedError("Method count() is not implemented")

    @public_api
    @typeCheck(type)
    def convert(self,
                typeClass,
                dst_unitSize=None,
                dst_endianness=None,
                dst_sign=None):
        """Convert the current data type in a destination type specified in
        parameter.

        :param typeClass: The Netzob type class to which the current data
                          must be converted.
        :type typeClass: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`, required
        :return: The converted current value in the specified data type.
        :rtype: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`


        >>> from netzob.all import *
        >>> i = uint8(42)
        >>> r = i.convert(Raw)
        >>> r
        b'*'

        """

        if typeClass is None:
            raise TypeError("TypeClass cannot be None")
        if not issubclass(typeClass, AbstractType):
            raise TypeError("Requested typeClass ({0}) is not supported.".
                            format(typeClass))

        if dst_endianness is None:
            dst_endianness = AbstractType.defaultEndianness()
        if dst_sign is None:
            dst_sign = AbstractType.defaultSign()

        if dst_endianness not in AbstractType.supportedEndianness():
            raise TypeError("dst_endianness is not supported.")
        if dst_sign not in AbstractType.supportedSign():
            raise TypeError("sign is not supported.")

        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        return typeClass(
            TypeConverter.convert(
                self.value,
                BitArray,
                typeClass,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=dst_unitSize,
                dst_endianness=dst_endianness,
                dst_sign=dst_sign),
            unitSize=dst_unitSize,
            endianness=dst_endianness,
            sign=dst_sign)

    @public_api
    def generate(self):
        """This method should generate data that respects the current data type.

        :return: The data produced.
        :rtype: :class:`bitarray <bitarray.bitarray>`


        >>> from netzob.all import *
        >>> a = String(nbChars=20)
        >>> l = a.generate()
        >>> len(l)
        160
        >>> a = HexaString(nbBytes=20)
        >>> l = a.generate()
        >>> len(l)
        160
        >>> a = HexaString(b"aabbccdd")
        >>> a.generate()
        bitarray('10101010101110111100110011011101')

        """

        # Return the self.value in priority if it is defined
        if self.value is not None:
            return self.value

        if self.default is not None:
            return self.default

        # Else, generate a data that respects the permitted min and max sizes
        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize, maxSize)
        randomContent = [random.randint(0, 1) for i in range(0, generatedSize)]
        return bitarray(randomContent)

    @staticmethod
    def computeUnitSize(length):
        r"""Return a UnitSize that permits to encode the provided length.

        >>> from netzob.Model.Vocabulary.Types.BitArray import BitArray
        >>> from netzob.Model.Vocabulary.Types.Raw import Raw
        >>> from netzob.Model.Vocabulary.Types.HexaString import HexaString
        >>> from netzob.Model.Vocabulary.Types.String import String
        >>> from netzob.Model.Vocabulary.Types.Integer import Integer
        >>> b = BitArray('0')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        1

        >>> b = Raw(b'a')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        8

        >>> b = HexaString(b'aa')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        8

        >>> b = String('a')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        8

        >>> b = Integer(1)
        >>> b.unitSize
        UnitSize.SIZE_16
        >>> len(b.generate())
        16

        >>> b = BitArray('00')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        2

        >>> b = BitArray('0000000000000000')
        >>> b.unitSize
        UnitSize.SIZE_4
        >>> len(b.generate())
        16

        >>> b = BitArray('00000000000000000')
        >>> b.unitSize
        UnitSize.SIZE_8
        >>> len(b.generate())
        17

        >>> b = BitArray(nbBits=17)
        >>> b.unitSize
        UnitSize.SIZE_8
        >>> len(b.generate())
        17

        >>> b = BitArray(nbBits=(1,17))
        >>> b.unitSize
        UnitSize.SIZE_8
        >>> 1 <= len(b.generate()) <= 17
        True

        """
        if length is None:
            length = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        # Deduce unit size according to max possible length
        if length > (1 << UnitSize.SIZE_64.value):
            raise Exception("Maximum length for datatype is too large: '{}'".format(length))
        elif length > (1 << UnitSize.SIZE_32.value):
            unit_size = UnitSize.SIZE_64
        elif length > (1 << UnitSize.SIZE_24.value):
            unit_size = UnitSize.SIZE_32
        elif length > (1 << UnitSize.SIZE_16.value):
            unit_size = UnitSize.SIZE_24
        elif length > (1 << UnitSize.SIZE_8.value):
            unit_size = UnitSize.SIZE_16
        elif length > (1 << UnitSize.SIZE_4.value):
            unit_size = UnitSize.SIZE_8
        else:
            unit_size = UnitSize.SIZE_4

        return unit_size

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current types.

        This specific method generates mutations on the bit level.
        If any type accepts bit level mutations, it should call this method. This method
        introduce the following mutations:

        * Original Version in little endian
        * Original Version in big endian
        * Inversed bytes in little endian
        * Inversed bytes in big endian

        >>> from netzob.all import *
        >>> t = String("helloworld")
        >>> print(t.mutate())
        OrderedDict([('ascii-bits(bigEndian)', bitarray('01101000011001010110110001101100011011110111011101101111011100100110110001100100')), ('ascii-bits(littleEndian)', bitarray('00010110101001100011011000110110111101101110111011110110010011100011011000100110')), ('ascii(inversed)-bits(bigEndian)', bitarray('01100100011011000111001001101111011101110110111101101100011011000110010101101000')), ('ascii(inversed)-bits(littleEndian)', bitarray('00100110001101100100111011110110111011101111011000110110001101101010011000010110')), ('ascii(upper)-bits(bigEndian)', bitarray('01001000010001010100110001001100010011110101011101001111010100100100110001000100')), ('ascii(upper)-bits(littleEndian)', bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')), ('ascii(inversed-upper)-bits(bigEndian)', bitarray('01000100010011000101001001001111010101110100111101001100010011000100010101001000')), ('ascii(inversed-upper)-bits(littleEndian)', bitarray('00100010001100100100101011110010111010101111001000110010001100101010001000010010'))])

        >>> t = Integer(100)
        >>> print(t.mutate())
        OrderedDict([('bits(bigEndian)', bitarray('0000000001100100')), ('bits(littleEndian)', bitarray('0000000000100110'))])

        >>> t = Integer()
        >>> mutations = t.mutate()
        >>> print(len(mutations['bits(littleEndian)']))
        16

        :keyword prefixDescription: prefix to attach to the description of the generated mutation.
        :type prefixDescription: :class:`str`
        :return: a dict of computed mutations having the same types than the initial one.
        :rtype: :class:`dict`<str>=:class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """
        if prefixDescription is None:
            prefixDescription = ""
        else:
            prefixDescription += "-"

        mutations = collections.OrderedDict()

        # If no value is known, we generate a new one
        if self.value is None:
            val = self.generate()
        else:
            val = self.value

        if self.endianness == Endianness.LITTLE:
            mutations["{0}bits(littleEndian)".format(prefixDescription)] = val
            bigEndianValue = bitarray(val, endian=Endianness.BIG.value)
            mutations["{0}bits(bigEndian)".format(
                prefixDescription)] = bigEndianValue
        else:
            mutations["{0}bits(bigEndian)".format(prefixDescription)] = val
            littleEndianValue = bitarray(
                val, endian=Endianness.LITTLE.value)
            mutations["{0}bits(littleEndian)".format(
                prefixDescription)] = littleEndianValue

        return mutations

    @staticmethod
    @abc.abstractmethod
    def decode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the data from its current encoding to :class:`bytes`.

        :param data: The data encoded in current type which will be decoded in :class:`bytes`.
        :param unitSize: The unit size of the specified data.
        :param endianness: The endianness of the specified data.
        :param sign: The sign of the specified data.
        :type data: the current type of the data, required
        :type unitSize: :class:`~netzob.Model.Vocabulary.Types.AbstractType.UnitSize`, optional
        :type endianness: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Endianness`, optional
        :type sign: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Sign`, optional

        :return: Data encoded in :class:`bytes`
        :rtype: :class:`bytes`
        :raise: :class:`TypeError` if parameters are not valid.
        """
        raise NotImplementedError(
            "Internal Error: 'decode' method not implemented")

    @staticmethod
    @abc.abstractmethod
    def encode(data, unitSize=None, endianness=None, sign=None):
        """This method convert data from :class:`bytes` to its type.

        :param data: The data encoded in :class:`bytes` which will be encoded in its current type.
        :param unitSize: The unit size of the specified data.
        :param endianness: The endianness of the specified data.
        :param sign: The sign of the specified data.
        :type data: :class:`bytes`, required
        :type unitSize: :class:`~netzob.Model.Vocabulary.Types.AbstractType.UnitSize`, optional
        :type endianness: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Endianness`, optional
        :type sign: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Sign`, optional
        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        raise NotImplementedError(
            "Internal Error: 'encode' method not implemented")

    @abc.abstractmethod
    def canParse(self, data):
        """This method tells if the specified data can be parsed
        with the current type and its constraints.

        :param data: The data to parse.
        :type data: :class:`bitarray <bitarray.bitarray>`, required
        :return: ``True`` if the data can be parsed will the current type
        :rtype: :class:`bool`
        """
        raise NotImplementedError(
            "Internal Error: 'canParse' method not implemented")

    @property
    def value(self):
        """The current value of the instance. This value is represented
        under the bitarray format.

        :type: :class:`bitarray`
        """

        return self.__value

    @value.setter  # type: ignore
    @typeCheck(bitarray)
    def value(self, value):
        self.__value = value

    @property
    def size(self):
        """The size of the expected Type defined
         by a tuple (min, max).
         Instead of a tuple, an int can be used to represent both min and max values.

         The value 'None' can be set for min and/or max to represent no limitations.

         For instance, to create a String field of at least 10 chars:

         >>> from netzob.all import *
         >>> f = Field(String(nbChars=(10,None)))
         >>> f.domain.dataType.size
         (80, 65536)

         while to create a Raw field which content has no specific limits:

         >>> from netzob.all import *
         >>> f = Field(Raw())

         :type: tuple (int, int)
         :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.

         """
        return self.__size

    @size.setter  # type: ignore
    def size(self, size):

        if size is None:
            size = (0, AbstractType.MAXIMUM_GENERATED_DATA_SIZE)
        elif isinstance(size, int):
            size = (size, size)

        if isinstance(size, tuple):
            minSize, maxSize = size

            if minSize is None:
                minSize = 0

            if maxSize is None:
                maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

            if minSize is not None and not isinstance(minSize, int):
                raise TypeError("Size must be defined with a tuple of integers")

            if maxSize is not None and not isinstance(maxSize, int):
                raise TypeError("Size must be defined with a tuple of integers")

            if self.sign == Sign.UNSIGNED:
                if minSize < 0 or maxSize < 0:
                    raise TypeError("Size must be defined with a tuple of positive integers")

                if minSize == maxSize == 0:
                    raise TypeError("Size must be defined with a tuple of integers that cannot be both equal to zero")

            if maxSize < minSize:
                raise TypeError("Size must be defined with a tuple of integers, where the second value is greater than the first value")

            self.__size = (minSize, maxSize)
        else:
            raise TypeError(
                "Size must be defined by a tuple an int or with None")

    @property
    def default(self):
        """The default value of the type instance.

        :type: :class:`bitarray`
        """

        return self.__default

    @default.setter  # type: ignore
    @typeCheck(bitarray)
    def default(self, default):
        if default is not None:
            if not self.canParse(default):
                raise ValueError("Cannot set a default Type value (here '{}') that cannot be parsed (current type: {})".format(default.tobytes(), self))
        self.__default = default

    @staticmethod
    def normalize(data):
        """Given the specified data, this static methods normalize its representation
        using Netzob types.

        :parameter data: the data to normalize
        :type data: :class:`object`
        :return: an abstractType which value is data
        :rtype: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`

        >>> from netzob.all import *
        >>> normalizedData = AbstractType.normalize("john")
        >>> normalizedData.__class__
        <class 'netzob.Model.Vocabulary.Types.String.String'>
        >>> normalizedData.value
        bitarray('01101010011011110110100001101110')
        """

        if data is None:
            raise TypeError("Cannot normalize None data")

        normalizedData = None

        if isinstance(data, AbstractType):
            return data
        elif isinstance(data, int):
            from netzob.Model.Vocabulary.Types.Integer import Integer
            return Integer(value=data)
        elif isinstance(data, bytes):
            from netzob.Model.Vocabulary.Types.Raw import Raw
            normalizedData = Raw(value=data)
        elif isinstance(data, str):
            from netzob.Model.Vocabulary.Types.String import String
            normalizedData = String(value=data)
        elif isinstance(data, bitarray):
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            normalizedData = BitArray(value=data)

        if normalizedData is None:
            raise TypeError(
                "Not a valid data ({0}), impossible to normalize it.",
                type(data))

        return normalizedData

    def buildDataRepresentation(self):
        """It creates a :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data>` following the specified type.

        for instance, user can specify a domain with its type which is much more simple than creating a Data with the type

        >>> from netzob.all import *
        >>> ascii = String("hello john !")
        >>> ascii.typeName
        'String'
        >>> data = ascii.buildDataRepresentation()
        >>> data.dataType.value.tobytes()
        b'hello john !'
        >>> print(data.dataType)
        String('hello john !')

        :return: a Data of the current type
        :rtype: :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leads.Data.Data>`

        """
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data

        scope = None

        if self.value is not None:
            scope = Scope.CONSTANT
        else:
            scope = Scope.NONE

        return Data(dataType=self, scope=scope)

    def getFixedBitSize(self):
        """Provide the length of a theoretical value that would be generated.
        It is not the length of an effective value but a prediction of its
        length in case this latter is fixed.

        :return: the theoretical length of a value generated from this type
        :rtype: int
        :raise: ValueError in case the length is dynamic or could not be predicted
        """
        self._logger.debug("Determine the deterministic size of the value of "
                           "the type")
        if self.value:
            return len(self.value)
        elif any(self.size) and self.size[0] == self.size[1]:
            return self.size[0]
        raise ValueError("Cannot determine a fixed size for type '{}'"
                         .format(self))

    @property
    def typeName(self):
        """The name of the implemented type. We recommend
        to set this value with the name of :  Type.__class__.__name__.

        :type: `str`
        :raises: :class: `TypeError` if typeName is not a string
        """
        return self.__typeName

    @typeName.setter  # type: ignore
    @typeCheck(str)
    def typeName(self, typeName):
        if typeName is None:
            raise TypeError("typeName cannot be None")
        self.__typeName = typeName

    @property
    def unitSize(self):
        """The unitSize of the current value.

        :type: `str`
        :raises: :class: `TypeError` if unitSize is not a string and not a supported value.

        """
        return self.__unitSize

    @unitSize.setter  # type: ignore
    @typeCheck(UnitSize)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("UnitSize cannot be None")
        if unitSize not in UnitSize:
            raise TypeError(
                "Specified UnitSize is not supported, please refer to the UnitSize enum."
            )
        self.__unitSize = unitSize

    @property
    def endianness(self):
        """The endianness of the current value.
        The endianness definition is synchronized with the bitarray value.

        :type: `str`
        :raises: :class: `TypeError` if endianness is not a string and not a supported value.

        """
        return self.__endianness

    @endianness.setter  # type: ignore
    @typeCheck(Endianness)
    def endianness(self, endianness):
        if endianness is None:
            raise TypeError("Endianness cannot be None")
        if endianness not in Endianness:
            raise TypeError(
                "Specified Endianness is not supported, please refer to the Endianness enum."
            )

        self.__endianness = endianness

        ## Note: this two lines are commented because bit-ordering is not supported
        # if self.value is not None and self.value.endian() != self.__endianness:
        #     self.value = bitarray(self.value, endian=self.__endianness.value)

    @property
    def sign(self):
        """The sign of the current value.

        :type: `str`
        :raises: :class: `TypeError` if sign is not a string and not a supported value.

        """
        return self.__sign

    @sign.setter  # type: ignore
    @typeCheck(Sign)
    def sign(self, sign):
        if sign is None:
            raise TypeError("Sign cannot be None")
        if sign not in Sign:
            raise TypeError(
                "Specified Sign is not supported, please refer to the Sign enum."
            )
        self.__sign = sign


def test_type_one_parameter(data_type, possible_parameters):
    """This test tries all possible parameters as input for this
    datatype. This test should not trigger any exception as input
    parameters are considered to be valid.

    """
    functional_possible_parameters = OrderedDict()
    for parameter_name, parameter_contents in possible_parameters.items():
        functional_parameter_contents = []
        for parameter_content in parameter_contents:
            parameters = OrderedDict()
            parameters[parameter_name] = parameter_content
            try:
                data_type(**parameters)
            except Exception as e:
                print(parameters)
                print("Exception when creating a datatype with one parameter: '{}'".format(e))
        functional_possible_parameters[parameter_name] = functional_parameter_contents


def test_type_multiple_parameters(data_type, possible_parameters):
    """This test tries all possible parameters as multiple inputs for this
    datatype. This test should not trigger any exception as input
    parameters are considered to be valid.

    """
    import itertools

    parameter_names = possible_parameters.keys()
    functional_combinations_possible_parameters = []
    combinations_possible_parameters = list(itertools.product(*possible_parameters.values()))
    for current_combination in combinations_possible_parameters:
        parameters = OrderedDict()
        for idx, parameter_name in enumerate(parameter_names):
            parameters[parameter_name] = current_combination[idx]
        try:
            data_type(**parameters)
        except Exception as e:
            if "should have either" not in str(e):  # Handle mutually exclusive parameter types
                print(parameters)
                print("Exception when creating a datatype with multiple parameters: '{}'".format(e))
        else:
            functional_combinations_possible_parameters.append(current_combination)

    return (parameter_names, functional_combinations_possible_parameters)


def test_type_specialize_abstract(data_type, parameter_names, combinations_possible_parameters):
    from netzob.all import Field, Symbol

    def specialize_abstract(parameters):
        try:
            t = data_type(**parameters)
            f = Field(t)
            s = Symbol([f])
            d = next(s.specialize())
        except Exception as e:
            print(parameters)
            print("EXCEPTION IN SPECIALIZATION: '{}'".format(e))
            return

        try:
            assert len(d) > 0
        except Exception as e:
            print(parameters)
            print("EXCEPTION IN GENERATING VALUE")
            return

        try:
            data_structure = s.abstract(d)
        except Exception as e:
            print(parameters)
            print("EXCEPTION IN PARSING: '{}'".format(e))

        try:
            assert data_structure['Field'] == d
        except Exception as e:
            print(parameters)
            print("EXCEPTION IN COMPARING SPECIALIZATION AND ABSTRACTION RESULTS")

    for current_combination in combinations_possible_parameters:
        parameters = OrderedDict()
        for idx, parameter_name in enumerate(parameter_names):
            parameters[parameter_name] = current_combination[idx]
        specialize_abstract(parameters)
