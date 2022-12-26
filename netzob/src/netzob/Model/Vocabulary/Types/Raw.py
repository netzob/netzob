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
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Common.Utils.Decorators import public_api


class Raw(AbstractType):
    r"""This class defines a Raw type.

    The Raw type describes a sequence of bytes of arbitrary
    size.

    The Raw constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains a fixed sequence of bytes. If None, the constructed Raw will accept a random sequence of bytes, whose size may be specified (see :attr:`nbBytes` parameter).
    :param nbBytes: This parameter is used to describe a domain that contains an amount of bytes. This amount can be fixed or represented with an interval. If None, the accepted sizes will range from 0 to 8192.
    :param alphabet: The alphabet can be used to limit the bytes that can participate in the domain value. The default value is None.
    :param default: This parameter is the default value used in specialization.
    :type value: :class:`bitarray` or :class:`bytes`, optional
    :type nbBytes: an :class:`int` or a tuple with the min and the max sizes specified as :class:`int`, optional
    :type alphabet: a :class:`list` of :class:`bytes`, optional
    :type default: :class:`bitarray` or :class:`bytes`, optional

    .. note::
       :attr:`value` and :attr:`nbBytes` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.

       :attr:`value` and :attr:`alphabet` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.

       :attr:`value` and :attr:`default` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The Raw class provides the following public variables:

    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The internal size (in bits) of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max values.
    :var alphabet: The alphabet can be used to limit the bytes that can participate in the domain value.
    :var default: The default value used in specialization.
    :vartype value: :class:`bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`
    :vartype alphabet: a :class:`list` of :class:`bytes`
    :vartype default: :class:`bitarray`

    The creation of a Raw type with no parameter will create a bytes
    object whose length ranges from 0 to 8192:

    >>> from netzob.all import *
    >>> i = Raw()
    >>> len(i.generate().tobytes())
    533
    >>> len(i.generate().tobytes())
    7738
    >>> len(i.generate().tobytes())
    5505

    The following example shows how to define a six-byte long raw
    object, and the use of the generation method to produce a
    value:

    >>> from netzob.all import *
    >>> r = Raw(nbBytes=6)
    >>> len(r.generate().tobytes())
    6

    It is possible to define a range regarding the valid size of the
    raw object:

    >>> from netzob.all import *
    >>> r = Raw(nbBytes=(2, 20))
    >>> 2 <= len(r.generate().tobytes()) <= 20
    True

    The following example shows the specification of a raw constant:

    >>> from netzob.all import *
    >>> r = Raw(b'\x01\x02\x03')
    >>> print(r)
    Raw(b'\x01\x02\x03')

    The alphabet optional argument can be used to limit the bytes that
    can participate in the domain value:

    >>> from netzob.all import *
    >>> r = Raw(nbBytes=30, alphabet=[b"t", b"o"])
    >>> data = r.generate().tobytes()
    >>> data
    b'otoottootottottooooooottttooot'
    >>> for c in set(data):  # extract distinct characters
    ...    print(chr(c))
    t
    o

    This next example shows the usage of a default value:

    >>> from netzob.all import *
    >>> raw = Raw(nbBytes=2, default=b'\x01\x02')
    >>> raw.generate().tobytes()
    b'\x01\x02'

    """

    @public_api
    def __init__(self,
                 value=None,
                 nbBytes=None,
                 unitSize=None,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign(),
                 alphabet=None,
                 default=None):

        if value is not None and nbBytes is not None:
            raise ValueError("A Raw should have either its value or its nbBytes set, but not both")

        if value is not None and default is not None:
            raise ValueError("A Raw should have either its constant value or its default value set, but not both")

        if value is not None and alphabet is not None:
            raise ValueError("A Raw should have either its constant value or its alphabet value set, but not both")

        if value is not None:
            if len(value) == 0:
                raise ValueError("Raw value cannot have a length equal to 0")

        if value is not None and not isinstance(value, bitarray):
            if isinstance(value, bytes):
                tmp_value = value
                value = bitarray(endian='big')
                value.frombytes(tmp_value)
            else:
                raise ValueError("Unsupported input format for value: '{}', type is: '{}', expected type is 'bitarray' or 'bytes'".format(value, type(value)))

        if default is not None and not isinstance(default, bitarray):
            if isinstance(default, bytes):
                tmp_default = default
                default = bitarray(endian='big')
                default.frombytes(tmp_default)
            else:
                raise ValueError("Unsupported input format for default value: '{}', type is: '{}', expected type is 'bitarray' or 'bytes'".format(default, type(default)))

        # Handle raw data size if value is None
        if value is None:
            nbBits = self._convertNbBytesinNbBits(nbBytes)
        else:
            nbBits = (len(value), len(value))

        self.alphabet = alphabet

        super(Raw, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign,
            default=default)

    def __str__(self):
        if self.value is not None:
            return "{}({})".format(self.typeName,
                                   repr(self.value.tobytes()))
        else:
            if self.size[0] == self.size[1]:
                return "{}(nbBytes={})".format(self.typeName, int(self.size[0] / 8))
            else:
                return "{}(nbBytes=({},{}))".format(self.typeName, int(self.size[0] / 8), int(self.size[1] / 8))

    def __repr__(self):
        r"""
        >>> from netzob.all import *
        >>> f = Field(Raw(b"\x01\x02\x03\x04"))
        >>> s = Symbol(fields=[f])
        >>> messages = [RawMessage(next(s.specialize())) for x in range(5)]
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
            return str(self.value.tobytes())
        else:
            return str(self.value)

    def _convertNbBytesinNbBits(self, nbBytes):
        nbMinBit = 0
        nbMaxBit = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if nbBytes is not None:
            if isinstance(nbBytes, int):
                if nbBytes <= 0:
                    raise ValueError("nbBytes should be > 0")
                nbMinBit = nbBytes * 8
                nbMaxBit = nbMinBit
            else:
                if nbBytes[0] is not None:
                    if not isinstance(nbBytes[0], int) or nbBytes[0] < 0:
                        raise ValueError("first element of nbBytes should be an integer >= 0")
                    nbMinBit = nbBytes[0] * 8
                if nbBytes[1] is not None:
                    if not isinstance(nbBytes[1], int) or nbBytes[1] <= 0:
                        raise ValueError("second element of nbBytes should be an integer > 0")
                    nbMaxBit = nbBytes[1] * 8

        return (nbMinBit, nbMaxBit)

    @public_api
    def count(self):
        r"""

        >>> from netzob.all import *
        >>> Raw().count()
        86400000000

        >>> Raw(nbBytes=4).count()
        4294967296

        >>> Raw(nbBytes=1).count()
        256

        >>> Raw(nbBytes=(1, 3)).count()
        16843008

        >>> Raw(b"abcd").count()
        1

        """
        if self.value is not None:
            return 1
        else:
            range_min = int(self.size[0] / 8)
            range_max = int(self.size[1] / 8)
            permitted_values = 256
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
            return count

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

        if self.default is not None:
            return self.default

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize, maxSize)

        generatedValue = None
        if self.alphabet is None:
            generatedValue = b''.join(random.randint(0, 255).to_bytes(length=1, byteorder='big') for i in range(int(generatedSize / 8)))
        else:
            generatedValue = b"".join([random.choice(self.alphabet) for _ in range(int(generatedSize / 8))])

        result = bitarray(endian='big')
        result.frombytes(generatedValue)
        return result

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
        >>> b = bitarray(endian='big')
        >>> b.frombytes(b"hello john")
        >>> Raw().canParse(b)
        True

        >>> Raw().canParse(b"hello john")
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
            if len(rawData) < (minBits / 8):
                return False
        if maxBits is not None:
            if len(rawData) > (maxBits / 8):
                return False

        if self.alphabet is not None:
            raw_data_set = set(rawData)
            for element in raw_data_set:
                if bytes([element]) not in self.alphabet:
                    return False

        return True

    @property
    def alphabet(self):
        return self.__alphabet

    @alphabet.setter  # type: ignore
    def alphabet(self, alphabet):
        if alphabet is not None:
            if not isinstance(alphabet, list):
                raise TypeError("'alphabet' parameter must be a list")
            if len(alphabet) == 0:
                raise TypeError("'alphabet' parameter must be a non-empty list")
            for elt in alphabet:
                if not isinstance(elt, bytes):
                    raise TypeError("'alphabet' parameter must be a list of bytes")
                if len(elt) != 1:
                    raise TypeError("'alphabet' parameter must be a list of unique bytes")
        self.__alphabet = alphabet


def _test(self):
    r"""

    >>> from netzob.all import *
    >>> t = Raw()
    >>> print(t)
    Raw(nbBytes=(0,8192))
    >>> t.size
    (0, 65536)
    >>> t.unitSize
    UnitSize.SIZE_16

    >>> t = Raw(nbBytes=4)
    >>> print(t)
    Raw(nbBytes=4)

    >>> t = Raw(b"abcd")
    >>> print(t)
    Raw(b'abcd')


    >>> from netzob.all import Field, Symbol
    >>> domains = [
    ...     Raw(b"xxxx"), Raw(nbBytes=2),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(next(f.specialize()) for f in symbol.fields)
    >>> assert symbol.abstract(data)


    # Verify that you cannot create a Raw with a value AND an nbBytes:

    >>> i = Raw(b'test', nbBytes=(2, 10))
    Traceback (most recent call last):
    ...
    ValueError: A Raw should have either its value or its nbBytes set, but not both

    """


def _test_specialize_abstract():
    r"""
    >>> from netzob.all import *
    >>> from collections import OrderedDict
    >>> Conf.apply()
    >>> from netzob.Model.Vocabulary.Types.AbstractType import test_type_one_parameter, test_type_multiple_parameters, test_type_specialize_abstract

    >>> data_type = Raw

    >>> possible_parameters = OrderedDict()
    >>> possible_parameters["value"] = [None, b"aa", b"abcdef123456"]
    >>> possible_parameters["nbBytes"] = [None, 2, (2, 8), (0, 42)]
    >>> possible_parameters["alphabet"] = [None, [b"e"], [b"e", b"e"]]
    >>> possible_parameters["default"] = [None, b"ee"]

    >>> functional_possible_parameters = test_type_one_parameter(data_type, possible_parameters)

    >>> (parameter_names, functional_combinations_possible_parameters) = test_type_multiple_parameters(data_type, possible_parameters)

    >>> test_type_specialize_abstract(data_type, parameter_names, functional_combinations_possible_parameters)

    """
