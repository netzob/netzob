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


    The creation of a BitArray type with no parameter will create a bytes
    object whose length ranges from 0 to 65535:

    >>> from netzob.all import *
    >>> i = BitArray()
    >>> len(i.generate().tobytes())
    534
    >>> len(i.generate().tobytes())
    6625
    >>> len(i.generate().tobytes())
    1458

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
        >>> d = String.decode("hello john")
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
    >>> Conf.apply()
    >>> from netzob.Model.Vocabulary.Types.AbstractType import test_type_one_parameter, test_type_multiple_parameters, test_type_specialize_abstract

    >>> possible_parameters = {}
    >>> possible_parameters["value"] = [None, '', b'', b'a', b'bb', "bb", 42, "00001111", b"00001111"]
    >>> possible_parameters["nbBits"] = [None, (), -4, 8, (0, 0), (2, 8), (8, 2), (-4, -2), (-4, 2), (2, -4), "test", ("test1", "test2"), (1, "test2")]
    >>> possible_parameters["default"] = [None, '', b"", b"e", b"eeee", b"ff", "ff", "00001111", b"00001111"]

    >>> data_type = BitArray

    >>> functional_possible_parameters = test_type_one_parameter(data_type, possible_parameters)
    {'value': None}
    {'value': ''}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'BitArray value cannot have a length equal to 0'
    {'value': b''}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'BitArray value cannot have a length equal to 0'
    {'value': b'a'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for value: 'b'a'', type: '<class 'bytes'>''
    {'value': b'bb'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for value: 'b'bb'', type: '<class 'bytes'>''
    {'value': 'bb'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Input value for the following BitArray is incorrect: 'bb'. Error: 'character must be '0' or '1', found 'b'''
    {'value': 42}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'object of type 'int' has no len()'
    {'value': '00001111'}
    {'value': b'00001111'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for value: 'b'00001111'', type: '<class 'bytes'>''
    {'nbBits': None}
    {'nbBits': ()}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'tuple index out of range'
    {'nbBits': -4}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'nbBits should be > 0'
    {'nbBits': 8}
    {'nbBits': (0, 0)}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'second element of nbBits should be an integer > 0'
    {'nbBits': (2, 8)}
    {'nbBits': (8, 2)}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Size must be defined with a tuple of integers, where the second value is greater than the first value'
    {'nbBits': (-4, -2)}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'first element of nbBits should be an integer >= 0'
    {'nbBits': (-4, 2)}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'first element of nbBits should be an integer >= 0'
    {'nbBits': (2, -4)}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'second element of nbBits should be an integer > 0'
    {'nbBits': 'test'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'first element of nbBits should be an integer >= 0'
    {'nbBits': ('test1', 'test2')}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'first element of nbBits should be an integer >= 0'
    {'nbBits': (1, 'test2')}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'second element of nbBits should be an integer > 0'
    {'default': None}
    {'default': ''}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Cannot set a default Type value (here 'b''') that cannot be parsed (current type: BitArray(nbBits=(0,65536))'
    {'default': b''}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for default value: 'b''', type: '<class 'bytes'>''
    {'default': b'e'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for default value: 'b'e'', type: '<class 'bytes'>''
    {'default': b'eeee'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for default value: 'b'eeee'', type: '<class 'bytes'>''
    {'default': b'ff'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for default value: 'b'ff'', type: '<class 'bytes'>''
    {'default': 'ff'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Input default value for the following BitArray is incorrect: 'ff'. Error: 'character must be '0' or '1', found 'f'''
    {'default': '00001111'}
    {'default': b'00001111'}
    EXCEPTION IN MODELING WITH ONE PARAMETER: 'Unsupported input format for default value: 'b'00001111'', type: '<class 'bytes'>''

    >>> (parameter_names, functional_combinations_possible_parameters) = test_type_multiple_parameters(data_type, functional_possible_parameters)
    {'value': None, 'nbBits': None, 'default': None}
    {'value': None, 'nbBits': None, 'default': '00001111'}
    {'value': None, 'nbBits': 8, 'default': None}
    {'value': None, 'nbBits': 8, 'default': '00001111'}
    {'value': None, 'nbBits': (2, 8), 'default': None}
    {'value': None, 'nbBits': (2, 8), 'default': '00001111'}
    {'value': '00001111', 'nbBits': None, 'default': None}
    {'value': '00001111', 'nbBits': None, 'default': '00001111'}
    EXCEPTION IN MODELING WITH MULTIPLE PARAMETERS: 'A BitArray should have either its constant value or its default value set, but not both'
    {'value': '00001111', 'nbBits': 8, 'default': None}
    EXCEPTION IN MODELING WITH MULTIPLE PARAMETERS: 'A BitArray should have either its value or its nbBits set, but not both'
    {'value': '00001111', 'nbBits': 8, 'default': '00001111'}
    EXCEPTION IN MODELING WITH MULTIPLE PARAMETERS: 'A BitArray should have either its value or its nbBits set, but not both'
    {'value': '00001111', 'nbBits': (2, 8), 'default': None}
    EXCEPTION IN MODELING WITH MULTIPLE PARAMETERS: 'A BitArray should have either its value or its nbBits set, but not both'
    {'value': '00001111', 'nbBits': (2, 8), 'default': '00001111'}
    EXCEPTION IN MODELING WITH MULTIPLE PARAMETERS: 'A BitArray should have either its value or its nbBits set, but not both'

    >>> test_type_specialize_abstract(data_type, parameter_names, functional_combinations_possible_parameters)

    """
