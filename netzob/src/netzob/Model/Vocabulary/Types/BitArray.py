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
import unittest

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


@NetzobLogger
class BitArray(AbstractType):
    r"""This class defines a BitArray type.

    The BitArray type describes an object that contains a
    sequence of bits of arbitrary size.

    The BitArray constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains a fixed array of bits. If None, the constructed BitArray will accept a random sequence of bits, whose size may be specified (see :attr:`nbBits` parameter).
    :param nbBits: This parameter is used to describe a domain that contains an amount of bits. This amount can be fixed or represented with an interval. If None, the accepted sizes will range from 0 to 65535.
    :param default: This parameter is the default value used in specialization.
    :type value: :class:`bitarray`, optional
    :type nbBits: an :class:`int` or a tuple with the min and the max sizes specified as :class:`int`, optional
    :type default: :class:`bitarray`, optional

    .. note::
       :attr:`value` and :attr:`nbBits` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.

       :attr:`value` and :attr:`default` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The BitArray class provides the following public variables:

    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size in bits of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max values.
    :var constants: A list of named constants used to access the
                    bitarray internal elements. Those elements are
                    automatically accessible by predefined named
                    constants, whose names can be changed. Besides,
                    elements can be accessed in read or write mode.
    :var default: The default value used in specialization.
    :vartype value: :class:`bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`
    :vartype constants: a :class:`list` of :class:`str`
    :vartype default: :class:`bitarray`

    .. warning::
       **Important note about BitArray and 8-bit aligned data**

       It is expected that BitArrays or successive BitArrays should
       produce 8-bit aligned data. For example, if two successive
       BitArrays are defined in a field, they should together produce
       8-bit aligned data, as depicted below. In this example, an
       :class:`Agg
       <netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg.Agg>` is
       used to concatenate two BitArrays in a :class:`Field
       <netzob.Model.Vocabulary.Field.Field>`.

       >>> from netzob.all import *
       >>> domain1 = BitArray(nbBits=12)
       >>> domain2 = BitArray(nbBits=4)
       >>> f = Field(domain=Agg([domain1, domain2]))
       >>> data = next(f.specialize())
       >>> len(data)
       2

       If a field/symbol model contains BitArrays that does not
       produce 8-bit aligned data, a :class:`GenerationException
       <netzob.Model.Vocabulary.AbstractField.GenerationException>`
       exception is raised during specialization.

       >>> from netzob.all import *
       >>> domain1 = BitArray(nbBits=12)
       >>> domain2 = BitArray(nbBits=5)
       >>> f = Field(domain=Agg([domain1, domain2]))
       >>> data = next(f.specialize())
       Traceback (most recent call last):
       ...
       netzob.Model.Vocabulary.AbstractField.GenerationException: specialize() produced 17 bits, which is not aligned on 8 bits. You should review the field model.


       However, no exception would be raised during data abstraction
       in field/symbol, as the input data bytes are already 8-bit
       aligned.


    The creation of a BitArray type with no parameter will create a bytes
    object whose length ranges from 0 to 65535:

    >>> from netzob.all import *
    >>> i = BitArray()
    >>> len(i.generate().tobytes())
    4962
    >>> len(i.generate().tobytes())
    7992
    >>> len(i.generate().tobytes())
    4529
    
    The following example shows how to define a BitArray
    containing a fixed constant.

    >>> from netzob.all import *
    >>> b = BitArray('00001111')
    >>> b.generate().tobytes()
    b'\x0f'


    **Bitarray of fixed and dynamic sizes**

    The following example shows how to define a bitarray of 1 bit, 47
    bits, 64 bits and then a bitarray with a variable size between 13
    and 128 bits:

    >>> from netzob.all import *
    >>> b = BitArray(nbBits=1)
    >>> len(b.generate())
    1

    >>> from netzob.all import *
    >>> b = BitArray(nbBits=47)
    >>> len(b.generate())
    47

    >>> from netzob.all import *
    >>> b = BitArray(nbBits=64)
    >>> len(b.generate())
    64

    >>> from netzob.all import *
    >>> b = BitArray(nbBits=(13, 128))
    >>> 13 <= len(b.generate()) <= 128
    True


    **Accessing bitarray elements by named constant**

    In the following example, we define a bitarray with two
    elements. As this bitarray has a fixed length, elements are
    automatically accessible by predefined named constants ('item_0'
    and 'item_1'):

    >>> from netzob.all import *
    >>> b = BitArray('00')
    >>> b.constants
    ['item_0', 'item_1']

    Bitarray element names can be changed:

    >>> b.constants[0] = 'Urgent flag'
    >>> b.constants[1] = 'Data flag'
    >>> b.constants
    ['Urgent flag', 'Data flag']

    Bitarray elements can be accessed in read or write mode:

    >>> b['Urgent flag']
    False
    >>> b['Urgent flag'] = True
    >>> b['Urgent flag']
    True

    Bitarray elements can be used with binary operators:

    >>> b['Urgent flag'] |= b['Data flag']
    >>> b['Urgent flag']
    True


    **Using a default value**

    This next example shows the usage of a default value:

    >>> from netzob.all import *
    >>> t = BitArray(nbBits=16, default='1111111100000000')
    >>> t.generate().tobytes()
    b'\xff\x00'

    """

    @public_api
    def __init__(self, value=None, nbBits=None, default=None):

        if value is not None and nbBits is not None:
            raise ValueError("A BitArray should have either its value or its nbBits set, but not both")

        if value is not None and default is not None:
            raise ValueError("A BitArray should have either its constant value or its default value set, but not both")

        if value is not None:
            if len(value) == 0:
                raise ValueError("BitArray value cannot have a length equal to 0")

        # Handle input value
        if value is not None and not isinstance(value, bitarray):

            # Check if value is correct, and normalize it in str object, and then in bitarray
            if isinstance(value, str):
                try:
                    value = bitarray(value)
                except Exception as e:
                    raise ValueError("Input value for the following BitArray is incorrect: '{}'. Error: '{}'".format(value, e))
            else:
                raise ValueError("Unsupported input format for value: '{}', type: '{}'".format(value, type(value)))

        # Handle input value
        if default is not None and not isinstance(default, bitarray):

            # Check if default value is correct, and normalize it in str object, and then in bitarray
            if isinstance(default, str):
                try:
                    default = bitarray(default)
                except Exception as e:
                    raise ValueError("Input default value for the following BitArray is incorrect: '{}'. Error: '{}'".format(default, e))
            else:
                raise ValueError("Unsupported input format for default value: '{}', type: '{}'".format(default, type(default)))

        # Normalize nbBits
        if value is None:
            nbBits = self._normalizeNbBits(nbBits)
        else:
            nbBits = (len(value), len(value))

        super(BitArray, self).__init__(self.__class__.__name__, value, nbBits, default=default)
        self.constants = None  # A list of named constant used to access the bitarray elements

        # When value is not None, we can access each element of the bitarray with named constants
        if value is not None:
            self.constants = ["item_{}".format(_) for _ in range(len(value))]
            self.size = (len(value),) * 2

    def __getitem__(self, key):
        if isinstance(key, int):
            if self.value is not None:
                return self.value[key]
            else:
                raise ValueError("Cannot access internal bitarray value, as it does not exist.")
        else:
            if self.constants is not None:
                return self.value[self.constants.index(key)]
            else:
                raise ValueError("Named constant access to bitarray elements is not possible, as bitarray is not of fixed length.")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if self.value is not None:
                self.value[key] = value
            else:
                raise ValueError("Cannot access internal bitarray value, as it does not exist.")
        else:
            if self.constants is not None:
                self.value[self.constants.index(key)] = value
            else:
                raise ValueError("Named constant access to bitarray elements is not possible, as bitarray is not of fixed length.")

    def _normalizeNbBits(self, nbBits):
        nbMinBit = 0
        nbMaxBit = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if nbBits is not None:
            if isinstance(nbBits, int):
                if nbBits <= 0:
                    raise ValueError("nbBits should be > 0")
                nbMinBit = nbBits
                nbMaxBit = nbBits
            else:
                if nbBits[0] is not None:
                    if not isinstance(nbBits[0], int) or nbBits[0] < 0:
                        raise ValueError("first element of nbBits should be an integer >= 0")
                    nbMinBit = nbBits[0]
                if nbBits[1] is not None:
                    if not isinstance(nbBits[1], int) or nbBits[1] <= 0:
                        raise ValueError("second element of nbBits should be an integer > 0")
                    nbMaxBit = nbBits[1]

        return (nbMinBit, nbMaxBit)

    @public_api
    def count(self):
        r"""

        >>> from netzob.all import *
        >>> BitArray().count()
        86400000000

        >>> BitArray(nbBits=4).count()
        16

        >>> BitArray(nbBits=1).count()
        2

        >>> BitArray(nbBits=(1, 3)).count()
        14

        >>> BitArray("0101").count()
        1

        """

        if self.value is not None:
            return 1
        else:
            range_min = self.size[0]
            range_max = self.size[1]
            permitted_values = 2
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
            return count

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """For the moment its always true because we consider
        the decimal type to be very similar to the raw type.

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a BitArray
        :rtype: bool
        :raise: TypeError if the data is None


        >>> from netzob.all import *
        >>> BitArray().canParse(String("hello john").value)
        True

        >>> BitArray(nbBits=8).canParse(bitarray('01010101'))
        True

        >>> BitArray(nbBits=8).canParse(bitarray('010101011'))
        False

        >>> BitArray('11110101').canParse(bitarray('11110101'))
        True

        """

        if data is None:
            raise TypeError("data cannot be None")

        if not isinstance(data, bitarray):
            raise TypeError("Data should be a python raw ({0}:{1})".format(
                data, type(data)))

        if len(data) == 0:
            return False

        # Firtly, check if self.value matches the data
        if self.value is not None:
            if self.value == data:
                return True

        # Else, check if the data is comprised between the expected sizes
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

        if self.default is not None:
            return self.default

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize, maxSize)
        randomContent = [random.randint(0, 1) for i in range(0, generatedSize)]
        return bitarray(randomContent)

    @staticmethod
    @typeCheck(bitarray)
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.BitArray import BitArray
        >>> d = String.decode(b"hello john")
        >>> r = BitArray.encode(d)
        >>> r.to01()
        '01101000011001010110110001101100011011110010000001101010011011110110100001101110'
        >>> t = BitArray.decode(r)
        >>> t
        b'hello john'


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
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: :class:`Enum`
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: :class:`Enum`
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

        :return: data encoded in BitArray
        :rtype: :class:`BitArray <netzob.Model.Vocabulary.Types.BitArray.BitArray>`
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        if isinstance(data, bytes):
            norm_data = data
        elif isinstance(data, str):
            norm_data = bytes(data, "utf-8")
        else:
            raise TypeError("Invalid type for: '{}'. Expected bytes or str, and got '{}'".format(data, type(data)))

        b = bitarray()
        b.frombytes(norm_data)
        return b


def _test():
    r"""

    >>> from netzob.all import *
    >>> t = BitArray()
    >>> print(t)
    BitArray(nbBits=(0,65536)
    >>> t.size
    (0, 65536)
    >>> t.unitSize
    UnitSize.SIZE_16

    >>> t = BitArray('01010001')
    >>> print(t)
    BitArray=bitarray('01010001')


    # test abstraction arbitrary values

    >>> domains = [
    ...     BitArray(nbBits=8),  # BitArray(bitarray("00001111" "1")), BitArray(nbBits=7),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(next(f.specialize()) for f in symbol.fields)
    >>> assert symbol.abstract(data)


    # Verify that you cannot create a BitArray with a value AND an nbBits:

    >>> i = BitArray(b'aabb', nbBits=(2, 10))
    Traceback (most recent call last):
    ...
    ValueError: A BitArray should have either its value or its nbBits set, but not both

    """

def _test_bit_size():
    r"""

    # small test to check BitArray size

    >>> from netzob.all import *

    >>> len(BitArray(nbBits=1).generate())
    1
    >>> len(BitArray(nbBits=10).generate())
    10
    >>> len(BitArray(nbBits=32).generate())
    32
    >>> len(BitArray(nbBits=64).generate())
    64

    """

def _test_bit_named_const():
    r"""
    # test of named constant on BitArray

    >>> from netzob.all import *

    >>> b = BitArray('00000000')
    >>> b.constants[7] = 'first'
    >>> b.constants[6] = 'second'
    >>> b.constants[5] = 'third'
    >>> b.constants[0] = 'last'
    >>> b['first'] = 1
    >>> b
    bitarray('00000001')
    >>> b['second'] = True
    >>> b['third'] = 1
    >>> b['last'] = 1
    >>> b
    bitarray('10000111')

    """

def _test_bit_operations():
    r"""
    # test capability to affect value to named bits, potentially with boolean operators

    >>> from netzob.all import *
    >>> b = BitArray('00')
    >>> b.constants
    ['item_0', 'item_1']
    >>> b.constants[0] = 'Urgent flag'
    >>> b.constants[1] = 'Data flag'
    >>> b.constants
    ['Urgent flag', 'Data flag']
    >>> b['Urgent flag'] = True
    >>> b['Data flag'] = True
    >>> b['Urgent flag'] |= b['Data flag']
    >>> b['Urgent flag']
    True
    >>> b['Urgent flag'] = False
    >>> b['Data flag'] = True
    >>> b['Urgent flag'] |= b['Data flag']
    >>> b['Urgent flag']
    True
    """


def _test_specialize_abstract():
    r"""
    >>> from netzob.all import *
    >>> from collections import OrderedDict
    >>> Conf.apply()
    >>> from netzob.Model.Vocabulary.Types.AbstractType import test_type_one_parameter, test_type_multiple_parameters, test_type_specialize_abstract

    >>> data_type = BitArray

    >>> possible_parameters = OrderedDict()
    >>> possible_parameters["value"] = [None, "00001111"]
    >>> possible_parameters["nbBits"] = [None, 8, (2, 8)]
    >>> possible_parameters["default"] = [None, "00001111"]

    >>> test_type_one_parameter(data_type, possible_parameters)

    >>> (parameter_names, functional_combinations_possible_parameters) = test_type_multiple_parameters(data_type, possible_parameters)

    """


def _test_symbol():
    r"""

    ## Be sure to produce data aligned on bytes (8 bits)

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> domain = BitArray(nbBits=(5, 7))
    >>> f = Field(domain=domain, name="field1")
    >>> symbol = Symbol(fields=[f])
    >>> next(symbol.specialize())
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.GenerationException: specialize() produced 7 bits, which is not aligned on 8 bits. You should review the symbol model.

    >>> domain1 = BitArray(nbBits=3)
    >>> domain2 = BitArray(nbBits=7)
    >>> f1 = Field(domain=domain1, name="field1")
    >>> f2 = Field(domain=domain2, name="field2")
    >>> symbol = Symbol(fields=[f1, f2])
    >>> next(symbol.specialize())
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.GenerationException: specialize() produced 10 bits, which is not aligned on 8 bits. You should review the symbol model.

    >>> domain1 = BitArray(nbBits=3)
    >>> domain2 = BitArray(nbBits=5)
    >>> f1 = Field(domain=domain1, name="field1")
    >>> f2 = Field(domain=domain2, name="field2")
    >>> symbol = Symbol(fields=[f1, f2])
    >>> data = next(symbol.specialize())
    >>> data
    b'\xed'
    >>> symbol.abstract(data)
    OrderedDict([('field1', b'\xe0'), ('field2', b'h')])

    """


def _test_field_aligned_bitarrays():
    r"""

    ## Be sure to produce data aligned on bytes (8 bits)

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> domain = BitArray(nbBits=(2, 6))
    >>> f = Field(domain=domain, name="field1")
    >>> next(f.specialize())
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.GenerationException: specialize() produced 6 bits, which is not aligned on 8 bits. You should review the field model.

    >>> domain = BitArray(nbBits=(8, 8))
    >>> f = Field(domain=domain, name="field1")
    >>> next(f.specialize())
    b'\x99'

    >>> domain1 = BitArray(nbBits=3)
    >>> domain2 = BitArray(nbBits=13)
    >>> f1 = Field(domain=domain1, name="field1")
    >>> f2 = Field(domain=domain2, name="field2")
    >>> f = Field(domain=[f1, f2])
    >>> data = next(f.specialize())
    >>> data
    b'\xbe\xd6'
    >>> f.abstract(data)
    OrderedDict([('field1', b'\xa0'), ('field2', b'\xf6\xb0')])

    >>> domain1 = BitArray(nbBits=3)
    >>> domain2 = BitArray(nbBits=5)
    >>> f = Field(domain=Agg([domain1, domain2]))
    >>> data = next(f.specialize())
    >>> data
    b'\x17'
    >>> f.abstract(data)
    OrderedDict([('Field', b'\x17')])

    >>> domain1 = BitArray(nbBits=27)
    >>> domain2 = BitArray(nbBits=5)
    >>> f = Field(domain=Agg([domain1, domain2]))
    >>> data = next(f.specialize())
    >>> len(data)
    4
    >>> data
    b"H\xc6'\xa7"
    >>> f.abstract(data)
    OrderedDict([('Field', b"H\xc6'\xa7")])

    """
