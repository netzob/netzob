#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import uuid
from bitarray import bitarray
import random
import collections

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS

@NetzobLogger
class AbstractType(object, metaclass=abc.ABCMeta):
    """AbstractType is the abstract class of all the classes that represents netzob types.
    In Netzob, a type defines a definition domain as a unique value or specified with specific rules.
    For instance, an integer under a specific interval, a string with a number of chars and an IPv4 of a specific
    netmask.

    Every types store their current value (if they have one) as a :class:`bitarray.bitarray`.

    >>> from netzob.all import *
    >>> t = ASCII("netzob")
    >>> t.value
    bitarray('011011100110010101110100011110100110111101100010')
    >>> print(t.endianness)
    big
    """

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

    # This value will be used if generate() method is called
    # without any upper size limit
    # 8192 is completly arbitrary and equals 1k of data (1024 bytes)
    MAXIMUM_GENERATED_DATA_SIZE = 8192

    @staticmethod
    def supportedTypes():
        """Official list of supported types"""
        from netzob.Model.Types.ASCII import ASCII
        from netzob.Model.Types.Raw import Raw
        from netzob.Model.Types.BitArray import BitArray
        from netzob.Model.Types.Integer import Integer
        from netzob.Model.Types.HexaString import HexaString
        from netzob.Model.Types.IPv4 import IPv4
        from netzob.Model.Types.Timestamp import Timestamp

        return [
            # an array of bits: [1,0,0,1,1,0..]
            BitArray,
            # original python way of encoding data, raw data
            Raw,
            # string data
            ASCII,
            # decimal
            Integer,
            # hexstring
            HexaString,
            # IPv4
            IPv4,
            # Timestamp
            Timestamp
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
        return AbstractType.ENDIAN_BIG

    @staticmethod
    def defaultSign():
        """Return the default sign

        :return: the default sign
        :rtype: str
        """
        return AbstractType.SIGN_SIGNED

    def __init__(self, typeName, value, size=(None, None), unitSize=None, endianness=None, sign=None):
        """Constructor for an AbstractType, an abstract class.
        This constructor must only be called by inheriting classes.

        :parameter typeName: the name of the type (highly recommand the use of __class__.__name__.
        :type typeName: :class:`str`
        :parameter value: the current value of the instance (specified in bitarray)
        :type value: :class:`bitarray.bitarray`
        :parameter size: the size in bits that this value takes (to build the appropriate regex)
        :type size: a tupple with the min and the max size specified as integers
        :keyword unitSize: the unitsize of the current value. Values must be one of AbstractType.UNITSIZE_*. if None, the value is the default one.
        :type unitSize: str
        :keyword endianness: the endianness of the current value. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE. if None, the value is the default one.
        :type endianness: str
        :keyword sign: the sign pf tje current value. Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED. if None, the value is the default one.
        :type sign: str
        """

        self.id = uuid.uuid4()
        self.typeName = typeName
        self.value = value
        self.size = size
        if unitSize is None:
            unitSize = AbstractType.defaultUnitSize()
        self.unitSize = unitSize
        if endianness is None:
            endianness = AbstractType.defaultEndianness()
        self.endianness = endianness
        if sign is None:
            sign = AbstractType.defaultSign()
        self.sign = sign

    def __str__(self):
        from netzob.Model.Types.TypeConverter import TypeConverter
        from netzob.Model.Types.BitArray import BitArray
        if self.value is not None:
            return "{0}={1} ({2})".format(self.typeName, TypeConverter.convert(self.value, BitArray, self.__class__), self.size)
        else:
            return "{0}={1} ({2})".format(self.typeName, self.value, self.size)

    def __repr__(self):
        if self.value != None:
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            return str(TypeConverter.convert(self.value, BitArray, self.__class__))
        else:
            return str(self.value)

    def __key(self):
        # Note: as bitarray objects cannot be hashed in Python3 (because bitarray objects are mutable), we cast a bitarray object in a tuple (which is immutable)
        return (self.typeName, tuple(self.value), self.size, self.unitSize, self.endianness, self.sign)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @typeCheck(type)
    def convertValue(self, typeClass, dst_unitSize=None, dst_endianness=None, dst_sign=None):
        """Convert the current data in the netzob type
        specified in parameter.

        :parameter typeClass: the netzob class to which the current data must be converted
        :type typeClass: type
        :keyword dst_unitSize: the unitsize of the destination value. Values must be one of AbstractType.UNITSIZE_*. if None, the value is the default one.
        :type dst_unitSize: str
        :keyword dst_endianness: the endianness of the destination value. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE. if None, the value is the default one.
        :type dst_endianness: str
        :keyword dst_sign: the sign of the destination. Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED. if None, the value is the default one.
        :type dst_sign: str
        :return: the converted current value in the specified netzob type
        :rtype: :class:`netzob.Model.AbstractType.AbstractType`
        """
        if typeClass is None:
            raise TypeError("TypeClass cannot be None")
        if typeClass not in AbstractType.supportedTypes():
            raise TypeError("Requested typeClass ({0}) is not supported.".format(typeClass))

        if dst_unitSize is None:
            dst_unitSize = AbstractType.defaultUnitSize()
        if dst_endianness is None:
            dst_endianness = AbstractType.defaultEndianness()
        if dst_sign is None:
            dst_sign = AbstractType.defaultSign()

        if dst_unitSize not in AbstractType.supportedUnitSizes():
            raise TypeError("Dst_unitsize is not supported.")
        if dst_endianness not in AbstractType.supportedEndianness():
            raise TypeError("Dst_endianness is not supported.")
        if dst_sign not in AbstractType.supportedSign():
            raise TypeError("Sign is not supported.")

        from netzob.Model.Types.TypeConverter import TypeConverter
        from netzob.Model.Types.BitArray import BitArray
        return typeClass(TypeConverter.convert(self.value, BitArray, typeClass, src_unitSize=self.unitSize, src_endianness=self.endianness, src_sign=self.sign, dst_unitSize=dst_unitSize, dst_endianness=dst_endianness, dst_sign=dst_sign), unitSize=dst_unitSize, endianness=dst_endianness, sign=dst_sign)

    def generate(self, generationStrategy=None):
        """Generates a random data that respects the current data type.
        This is the minimal generation strategy, some types extends this.

        >>> from netzob.all import *
        >>> a = ASCII(nbChars=20)
        >>> l = a.generate()
        >>> print(len(l))
        160
        """

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize, maxSize)
        randomContent = [random.randint(0, 1) for i in range(0, generatedSize)]
        return bitarray(randomContent, endian=self.endianness)

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current types.

        This specific method allows to generate mutations on the bit level.
        If any type accepts bit level mutations, it should call this method. This method
        introduce the following mutations:

        * Original Version in little endian
        * Original Version in big endian
        * Inversed bytes in little endian
        * Inversed bytes in big endian

        >>> from netzob.all import *
        >>> t = ASCII("helloworld")
        >>> print(t.mutate())
        OrderedDict([('ascii-bits(bigEndian)', bitarray('01101000011001010110110001101100011011110111011101101111011100100110110001100100')), ('ascii-bits(littleEndian)', bitarray('00010110101001100011011000110110111101101110111011110110010011100011011000100110')), ('ascii(inversed)-bits(bigEndian)', bitarray('01100100011011000111001001101111011101110110111101101100011011000110010101101000')), ('ascii(inversed)-bits(littleEndian)', bitarray('00100110001101100100111011110110111011101111011000110110001101101010011000010110')), ('ascii(upper)-bits(bigEndian)', bitarray('01001000010001010100110001001100010011110101011101001111010100100100110001000100')), ('ascii(upper)-bits(littleEndian)', bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')), ('ascii(inversed-upper)-bits(bigEndian)', bitarray('01000100010011000101001001001111010101110100111101001100010011000100010101001000')), ('ascii(inversed-upper)-bits(littleEndian)', bitarray('00100010001100100100101011110010111010101111001000110010001100101010001000010010'))])

        >>> t = Integer(100)
        >>> print(t.mutate())
        OrderedDict([('bits(bigEndian)', bitarray('01100100')), ('bits(littleEndian)', bitarray('00100110'))])

        >>> t = Integer()
        >>> mutations = t.mutate()
        >>> print(len(mutations['bits(littleEndian)']))
        8

        :keyword prefixDescription: prefix to attach to the description of the generated mutation.
        :type prefixDescription: :class:`str`
        :return: a dict of computed mutations having the same types than the initial one.
        :rtype: :class:`dict`<str>=:class:`netzob.Model.Types.AbstractType.AbstractType`
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

        if self.endianness == AbstractType.ENDIAN_LITTLE:
            mutations["{0}bits(littleEndian)".format(prefixDescription)] = val
            bigEndianValue = bitarray(val, endian=AbstractType.ENDIAN_BIG)
            mutations["{0}bits(bigEndian)".format(prefixDescription)] = bigEndianValue
        else:
            mutations["{0}bits(bigEndian)".format(prefixDescription)] = val
            littleEndianValue = bitarray(val, endian=AbstractType.ENDIAN_LITTLE)
            mutations["{0}bits(littleEndian)".format(prefixDescription)] = littleEndianValue

        return mutations

    @staticmethod
    @abc.abstractmethod
    def decode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the specified data in python raw format.

        :param data: the data encoded in current type which will be decoded in raw
        :type data: the current type
        :keyword unitSize: the unit size of the specified data
        :type unitSize: :class:`netzob.Model.Types.UnitSize.UnitSize`
        :keyword endianness: the endianness of the specified data
        :type endianness: :class:`netzob.Model.Types.Endianness.Endianness`
        :keyword sign: the sign of the specified data
        :type sign: :class:`netzob.Model.Types.Sign.Sign`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        raise NotImplementedError("Internal Error: 'decode' method not implemented")

    @staticmethod
    @abc.abstractmethod
    def encode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the python raw data to the current type.

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unit size of the specified data
        :type unitSize: :class:`netzob.Model.Types.UnitSize.UnitSize`
        :keyword endianness: the endianness of the specified data
        :type endianness: :class:`netzob.Model.Types.Endianness.Endianness`
        :keyword sign: the sign of the specified data
        :type sign: :class:`netzob.Model.Types.Sign.Sign`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        raise NotImplementedError("Internal Error: 'encode' method not implemented")

    @abc.abstractmethod
    def canParse(self, data):
        """This method computes if the specified data can be parsed
        with the current type and its contraints

        :param data: the data encoded in python raw to check
        :type data: python raw
        :return: True if the data can be parsed will the curren type
        :rtype: bool
        """
        raise NotImplementedError("Internal Error: 'canParse' method not implemented")

    @property
    def value(self):
        """The current value of the instance. This value is represented
        under BitArray format

        :type: :class:`netzob.Model.Types.BitArray.BitArray`
        """

        return self.__value

    @value.setter
    @typeCheck(bitarray)
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
         >>> f = Field(ASCII(nbChars=(10,None)))
         >>> f.domain.dataType.size
         (80, None)

         while to create a Raw field which content has no specific limits:

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

            if maxSize is None and self.value is not None:
                maxSize = len(self.value)

            if minSize < 0:
                raise ValueError("Minimum size must be greater than 0")
            if maxSize is not None and maxSize < minSize:
                raise ValueError("Maximum must be greater or equals to the minimum")
            if maxSize is not None and maxSize > AbstractType.MAXIMUM_GENERATED_DATA_SIZE:
                raise ValueError("Maximum size supported for a variable is {0}.".format(AbstractType.MAXIMUM_GENERATED_DATA_SIZE))

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
        :rtype: :class:`netzob.Model.Types.AbstractType.AbstractType`

        >>> from netzob.all import *
        >>> normalizedData = AbstractType.normalize("netzob")
        >>> print(normalizedData.__class__)
        <class 'netzob.Model.Types.ASCII.ASCII'>
        >>> print(normalizedData.value)
        bitarray('011011100110010101110100011110100110111101100010')
        """

        if data is None:
            raise TypeError("Cannot normalize None data")

        normalizedData = None

        if isinstance(data, AbstractType):
            return data
        elif isinstance(data, int):
            from netzob.Model.Types.Integer import Integer
            return Integer(value=data)
        elif isinstance(data, bytes):
            from netzob.Model.Types.Raw import Raw
            normalizedData = Raw(value=data)
        elif isinstance(data, str):
            from netzob.Model.Types.ASCII import ASCII
            normalizedData = ASCII(value=data)

        if normalizedData is None:
            raise TypeError("Not a valid data ({0}), impossible to normalize it.", type(data))

        return normalizedData

    def buildDataRepresentation(self):
        """It creates a :class:`netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data` following the specified type.

        for instance, user can specify a domain with its type which is much more simple than creating a Data with the type

        >>> from netzob.all import *
        >>> ascii = ASCII("hello netzob !")
        >>> print(ascii.typeName)
        ASCII
        >>> data = ascii.buildDataRepresentation()
        >>> print(TypeConverter.convert(data.currentValue, BitArray, ASCII))
        hello netzob !
        >>> print(data.dataType)
        ASCII=hello netzob ! ((0, 112))

        :return: a Data of the current type
        :rtype: :class:`netzob.Model.Vocabulary.Domain.Variables.Leads.Data.Data`

        """
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data

        svas = None
        
        if self.value is not None:
            svas = SVAS.CONSTANT
        else:
            svas = SVAS.EPHEMERAL

        return Data(dataType=self, originalValue=self.value, svas=svas)

    @property
    def id(self):
        """Unique identifier of the type.

        This value must be a unique UUID instance (generated with uuid.uuid4()).

        :type: :class:`uuid.UUID`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, id):
        if id is None:
            raise ValueError("id is Mandatory.")
        self.__id = id

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

    @property
    def unitSize(self):
        """The unitSize of the current value.

        :type: `str`
        :raises: :class: `TypeError` if unitSize is not an str and not a supported value.

        """
        return self.__unitSize

    @unitSize.setter
    @typeCheck(str)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("UnitSize cannot be None")
        if not unitSize in AbstractType.supportedUnitSizes():
            raise TypeError("Specified UnitSize is not supported, please refer to the list in AbstractType.supportedUnitSize().")
        self.__unitSize = unitSize

    @property
    def endianness(self):
        """The endianness of the current value.
        The endianness definition is synchronized with the bitarray value.

        :type: `str`
        :raises: :class: `TypeError` if endianness is not an str and not a supported value.

        """
        return self.__endianness

    @endianness.setter
    @typeCheck(str)
    def endianness(self, endianness):
        if endianness is None:
            raise TypeError("Endianness cannot be None")
        if not endianness in AbstractType.supportedEndianness():
            raise TypeError("Specified Endianness is not supported, please refer to the list in AbstractType.supportedEndianness().")

        self.__endianness = endianness

        if self.value is not None and self.value.endian() != self.__endianness:
            self.value = bitarray(self.value, endian=self.__endianness)

    @property
    def sign(self):
        """The sign of the current value.

        :type: `str`
        :raises: :class: `TypeError` if sign is not an str and not a supported value.

        """
        return self.__sign

    @sign.setter
    @typeCheck(str)
    def sign(self, sign):
        if sign is None:
            raise TypeError("Sign cannot be None")
        if not sign in AbstractType.supportedSign():
            raise TypeError("Specified Sign is not supported, please refer to the list in AbstractType.supportedSign().")
        self.__sign = sign

