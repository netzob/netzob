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
import string
import collections

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Common.Utils.Decorators import NetzobLogger, typeCheck


@NetzobLogger
class String(AbstractType):
    r"""This class defines a String type, which is used to represent String
    or Unicode characters.

    The String type is a wrapper for the Python :class:`str` object
    with the capability to express more constraints on the permitted
    string values.

    The String constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains a fixed string. If None, the constructed string will accept a random sequence of character, whose size may be specified (see :attr:`nbChars` parameter).
    :param nbChars: This parameter is used to describe a domain that contains an amount of characters. This amount can be fixed or represented with an interval. If None, the accepted sizes will range from 0 to 65535.
    :param encoding: The encoding of the string, such as 'ascii' or
                    'utf-8'. Default value is 'utf-8'.
    :param eos: A list defining the potential terminal characters for
                the string, with either specific constants or pointers
                to other fields containing the permitted terminal
                values. Default value is an empty list, meaning there
                is no terminal character.
    :type value: :class:`bitarray` or :class:`str`, optional
    :type nbChars: an :class:`int` or a tuple with the min and the max sizes specified as :class:`int`, optional
    :type encoding: :class:`str`, optional
    :type eos: a :class:`list` of :class:`str`, optional

    .. note::
       :attr:`value` and :attr:`nbChars` attributes are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The String class provides the following public variables:

    :var typeName: The name of the implemented data type.
    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size in bits of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max values.
    :var encoding: The encoding of the current value, such as 'ascii' or 'utf-8'.
    :var eos: A list defining the potential terminal characters for
              the string.
    :vartype typeName: :class:`str`
    :vartype value: :class:`bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`
    :vartype encoding: :class:`str`
    :type eos: a :class:`list` of :class:`str`


    Supported encodings are available on the Python reference documentation: `Python Standard Encodings <https://docs.python.org/3.4/library/codecs.html#standard-encodings>`_.

    Strings can be either static, dynamic with fixed sizes or even
    dynamic with variable sizes.


    The creation of a String type with no parameter will create a string
    object whose length ranges from 0 to 65535:

    >>> from netzob.all import *
    >>> i = String()
    >>> len(i.generate().tobytes())
    6311
    >>> len(i.generate().tobytes())
    3429
    >>> len(i.generate().tobytes())
    3260

    The following examples show how to define a static string in UTF-8:

    >>> from netzob.all import *
    >>> s = String("Paris")
    >>> s.generate().tobytes()
    b'Paris'
    >>> s = String("Paris in Euro: €")
    >>> s.generate().tobytes()
    b'Paris in Euro: \xe2\x82\xac'
    >>> s = String("Paris in Euro: €", encoding='utf-8')
    >>> s.generate().tobytes()
    b'Paris in Euro: \xe2\x82\xac'

    The following example shows the raising of an exception if input
    value is not valid, with the definition of a string where
    the associated value contains a non-String element:

    >>> from netzob.all import *
    >>> s = String("Paris in €", encoding='ascii') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: Input value for the following string is incorrect: 'Paris in €'...

    The following example shows how to define a string with a
    fixed size and a dynamic content:

    >>> from netzob.all import *
    >>> s = String(nbChars=10)
    >>> len(s.generate().tobytes())
    10

    The following example shows how to define a string with a
    variable size and a dynamic content:

    >>> from netzob.all import *
    >>> s = String(nbChars=(10, 32))
    >>> 10 <= len(s.generate().tobytes()) <= 32
    True


    **String with terminal character**

    Strings with a terminal delimiter are supported. The following
    example shows the usage of a delimiter.

    >>> from netzob.all import *
    >>> s = String(nbChars=10, eos=['\n'])
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-1:] == b'\n'
    True

    The ``eos`` attribute specifies a list of values that are used as
    potential terminal characters. Terminal characters can be a
    constant (such as ``'\n'`` in the previous example).

    """

    def __init__(self,
                 value=None,
                 nbChars=None,
                 encoding='utf-8',
                 eos=[],
                 unitSize=None,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        self.encoding = encoding
        self.eos = eos

        if value is not None and nbChars is not None:
            raise ValueError("A String should have either its value or its nbChars set, but not both")

        # Convert value to bitarray
        if value is not None and not isinstance(value, bitarray):

            # Check if value is correct, and normalize it in str object, and then in bitarray
            if isinstance(value, bytes):
                try:
                    value = value.decode(self.encoding)
                except Exception as e:
                    raise ValueError("Input value for the following string is incorrect: '{}'. Error: '{}'".format(value, e))
            elif isinstance(value, str):
                try:
                    value.encode(self.encoding)
                except Exception as e:
                    raise ValueError("Input value for the following string is incorrect: '{}'. Error: '{}'".format(value, e))
            else:
                raise ValueError("Unsupported input format for value: '{}', type: '{}'".format(value, type(value)))

            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            value = TypeConverter.convert(
                value,
                String,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        # Handle string size if value is None
        if value is None:
            nbBits = self._normalizeNbChars(nbChars)
        else:
            nbBits = (len(value), len(value))

        super(String, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def __str__(self):
        if self.value is not None:
            return "{}('{}')".format(self.typeName, self.value.tobytes().decode(self.encoding))
        else:
            if self.size[0] == self.size[1]:
                return "{}(nbChars={})".format(self.typeName, int(self.size[0] / 8))
            else:
                return "{}(nbChars=({},{}))".format(self.typeName, int(self.size[0] / 8), int(self.size[1] / 8))

    def _normalizeNbChars(self, nbChars):
        nbMinBits = None
        nbMaxBits = None
        if nbChars is not None:
            if isinstance(nbChars, int):
                nbMinBits = nbChars * 8
                nbMaxBits = nbChars * 8
            else:
                if nbChars[0] is not None:
                    if not isinstance(nbChars[0], int):
                        raise TypeError(
                            "First element of the tuple of the nbChars must be an int if defined."
                        )
                    nbMinBits = nbChars[0] * 8
                if nbChars[1] is not None:
                    if not isinstance(nbChars[1], int):
                        raise TypeError(
                            "Second element of the tuple of the nbChars must be an int if defined."
                        )
                    nbMaxBits = nbChars[1] * 8

        return (nbMinBits, nbMaxBits)

    def count(self, presets=None, fuzz=None):
        r"""

        >>> from netzob.all import *
        >>> String().count()
        86400000000

        >>> String(nbChars=4).count()
        100000000

        >>> String(nbChars=(1, 2)).count()
        10100

        >>> String("hello").count()
        1

        """

        if self.value is not None:
            return 1
        else:
            range_min = int(self.size[0] / 8)
            range_max = int(self.size[1] / 8)
            permitted_values = len(string.printable)
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
            return count

    def generate(self, generationStrategy=None):
        """Generates a random String that respects the requested size.

        >>> from netzob.all import *
        >>> a = String(nbChars=10)
        >>> gen = a.generate()
        >>> len(gen)/8
        10.0

        >>> b = String("john")
        >>> b.generate().tobytes() == b"john"
        True

        """
        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize / 8, maxSize / 8)

        permitted_characters = list(string.printable)

        # Handle terminal character ('end of string')
        final_character = None
        if len(self.eos) > 0:
            final_character = random.choice(self.eos)

        # Generate the sufficient amount of data
        if self.value is not None:
            random_content = self.value.tobytes().decode(self.encoding)
        else:
            random_content = ""
        # Compare the length of the *unicode* value against the targeted size
        while len(random_content.encode(self.encoding)) < generatedSize:
            random_content += random.choice(permitted_characters)

            # Be sure that the potential terminal characters are not present in the first part of the generated string
            if final_character is not None:
                while True:
                    random_content_tmp = random_content
                    for elt in self.eos:
                        random_content_tmp = random_content_tmp.replace(elt, "")
                    if len(random_content_tmp) == len(random_content):
                        random_content = random_content_tmp
                        break
                    else:
                        random_content = random_content_tmp

        # Handle terminal character ('end of string')
        if final_character is not None:
            if self.value is None:
                # Remove the size of the added terminal character to the original random_content, and add the final character
                random_content = random_content[:len(random_content) - len(final_character)] + final_character
            else:
                random_content += final_character

        return TypeConverter.convert(random_content, String, BitArray)

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current String value.

        Mutations are first applied to the String value than, each obtained mutations generates
        new bitarray mutations.
        String mutations are:

        * Original Version
        * Original Version in Upper case
        * Original Version in Lower case

        >>> from netzob.all import *
        >>> t = String("helloworld")
        >>> values = t.mutate()
        >>> values['ascii(upper)-bits(littleEndian)']
        bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')
        >>> values['ascii(inversed)-bits(bigEndian)']
        bitarray('01100100011011000111001001101111011101110110111101101100011011000110010101101000')


        :keyword prefixDescription: prefix to attach to the description of the generated mutation.
        :type prefixDescription: :class:`str`
        :return: a dict of computed mutations having the same types than the initial one.
        :rtype: :class:`dict`<str>=:class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """
        if prefixDescription is None:
            prefixDescription = ""
        else:
            prefixDescription += "-"

        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray

        if self.value is None:
            val = self.generate()
        else:
            val = self.value

        strValue = TypeConverter.convert(val, BitArray, String)

        mutations = collections.OrderedDict()

        mutations["{0}ascii".format(prefixDescription)] = strValue
        mutations["{0}ascii(inversed)".format(
            prefixDescription)] = strValue[::-1]
        if strValue != strValue.upper():
            mutations["{0}ascii(upper)".format(
                prefixDescription)] = strValue.upper()
            mutations["{0}ascii(inversed-upper)".format(
                prefixDescription)] = strValue[::-1].upper()
        if strValue != strValue.lower():
            mutations["{0}ascii(lower)".format(
                prefixDescription)] = strValue.lower()
            mutations["{0}ascii(inversed-lower)".format(
                prefixDescription)] = strValue[::-1].lower()

        results = collections.OrderedDict()
        for mutationName, mutationValue in list(mutations.items()):
            ba = BitArray(
                TypeConverter.convert(mutationValue, String, BitArray))
            results.update(ba.mutate(mutationName))

        return results

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """This method returns True if data is a String (utf-8)

        **Some examples with bitarray as input**

        >>> from netzob.all import *
        >>> b = bitarray(endian='big')
        >>> b.frombytes(b"hello netzob")
        >>> String().canParse(b)
        True

        The ascii table is defined from 0 to 127:
        >>> String(encoding='ascii').canParse(Integer(128, sign=Sign.UNSIGNED).value)
        False

        >>> a = String(nbChars=10)
        >>> a.canParse(String("hellohello").value)
        True
        >>> a.canParse(String("hello hello").value)
        False

        >>> a = String(nbChars=(2,20))
        >>> a.canParse(String("John").value)
        True
        >>> a.canParse(String("Hello john, what's up ?").value)
        False

        >>> String("hello").canParse(String("hello").value)
        True


        **Some examples with string (ascii, unicode, ...) as input**

        >>> String("hello").canParse("hello")
        True

        >>> String("hello").canParse("helloo")
        False

        >>> String().canParse("helloo")
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a String
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        # Check if data is correct, and normalize it in str object, and then in bitarray
        if not isinstance(data, bitarray):
            if isinstance(data, bytes):
                try:
                    data = data.decode(self.encoding)
                except Exception as e:
                    raise ValueError("Input data for the following string is incorrect: '{}'. Error: '{}'".format(data, e))
            elif isinstance(data, str):
                try:
                    data.encode(self.encoding)
                except Exception as e:
                    raise ValueError("Input data for the following string is incorrect: '{}'. Error: '{}'".format(data, e))
            else:
                raise ValueError("Unsupported input format for data: '{}', type: '{}'".format(data, type(data)))

            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            data = TypeConverter.convert(
                data,
                String,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)

        # Compare with self.value if it is defined
        if self.value is not None:
            if self.value == data:
                return True
            else:
                return False

        # Else, compare with expected size
        if len(data) % 8 != 0:  # Ascii must be 8 bits modulo length
            return False

        # At this time, data is a bitarray
        rawData = data.tobytes()

        try:
            rawData.decode(self.encoding)
        except:
            return False

        (minChar, maxChar) = self.size
        if minChar is not None:
            if len(rawData) < (minChar / 8):
                return False
        if maxChar is not None:
            if len(rawData) > (maxChar / 8):
                return False

        # Verify the terminal character
        if len(self.eos) > 0:
            for permitted_element in self.eos:
                last_element = rawData[-(len(permitted_element)):]
                if last_element == str.encode(permitted_element):
                    break
            else:
                return False

        return True

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> String.decode("hello")
        b'hello'
        >>> String.decode('\x4a\x6f\x68\x6e\x20\x69\x73\x20\x69\x6e\x20\x74\x68\x65\x20\x6b\x69\x74\x63\x68\x65\x6e\x21')
        b'John is in the kitchen!'
        >>> String.decode(1021)
        b'1021'

        :param data: the data encoded in String which will be decoded in raw
        :type data: the current type
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: :class:`Enum`
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: :class:`Enum`
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        return str(data).encode('utf-8')

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the String.

        >>> from netzob.all import *
        >>> raw = String.decode("hello john!")
        >>> String.encode(raw)
        'hello john!'

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of UnitSize.SIZE_*
        :type unitSize: :class:`Enum`
        :keyword endianness: the endianness to consider while encoding. Values must be Endianness.BIG or Endianness.LITTLE
        :type endianness: :class:`Enum`
        :keyword sign: the sign to consider while encoding Values must be Sign.SIGNED or Sign.UNSIGNED
        :type sign: :class:`Enum`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        res = ""
        for ordElt in data:
            if ordElt >= 0x20 and ordElt <= 0x7e:  # means between ' ' and '~'
                res += chr(ordElt)
            else:
                res += "."

        return res

    @property
    def encoding(self):
        """The encoding of the current value, such as 'ascii' or 'utf-8'.

        :type: `str`
        :raises: :class: `TypeError` if encoding is not a str object.

        """
        return self.__encoding

    @encoding.setter  # type: ignore
    @typeCheck(str)
    def encoding(self, encoding):
        if encoding is None:
            raise TypeError("Encoding cannot be None")
        self.__encoding = encoding

    @property
    def eos(self):
        """A :class:`list` of :class:`str` defining the potential terminal
        characters for the string.

        """
        return self.__eos

    @eos.setter  # type: ignore
    def eos(self, eos):
        if eos is None:
            raise Exception("'eos' parameter cannot be None")
        if not isinstance(eos, list):
            raise Exception("'eos' parameter must be a list")
        eos_list = []

        for elt in eos:
            if isinstance(elt, str):
                eos_list.append(elt)
            else:
                raise Exception("'eos' parameter must be a list of string or AbstractField")
        self.__eos = eos_list


def _test(self):
    r"""

    >>> from netzob.all import *
    >>> t = String()
    >>> print(t)
    String(nbChars=(0,8192))
    >>> t.size
    (0, 65536)
    >>> t.unitSize
    UnitSize.SIZE_16

    >>> t = String(nbChars=4)
    >>> print(t)
    String(nbChars=4)
    >>> t.size
    (32, 32)

    >>> t = String("abcd")
    >>> print(t)
    String('abcd')

    Examples of string internal attributes access:

    >>> from netzob.all import *
    >>> cAscii = String("hello")
    >>> print(cAscii)
    String('hello')
    >>> cAscii.typeName
    'String'
    >>> cAscii.value
    bitarray('0110100001100101011011000110110001101111')

    The following example shows how to convert the
    current type to any other Netzob types:

    >>> from netzob.all import *
    >>> cAscii = String("hello")
    >>> raw = cAscii.convert(Raw)
    >>> print(repr(raw))
    b'hello'
    >>> ip = cAscii.convert(IPv4)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: Impossible to encode b'hello' into an IPv4 data...

    The type can be used to specify constraints over the domain:

    >>> from netzob.all import *
    >>> a = String(nbChars=10)
    >>> print(a.value)
    None

    It is not possible to convert if the object has not value:

    >>> from netzob.all import *
    >>> a = String(nbChars=10)
    >>> a.convert(Raw)
    Traceback (most recent call last):
    ...
    TypeError: Data cannot be None


    >>> from netzob.all import Field, Symbol
    >>> domains = [
    ...    String("abcd"), String(nbChars=(4, 5)),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(f.specialize() for f in symbol.fields)
    >>> Symbol.abstract(data, [symbol])  #doctest: +ELLIPSIS
    (Symbol, OrderedDict([('0', b'abcd'), ('1', ...)]))


    ## String with terminal character as a constant (specialization and abstraction)

    >>> from netzob.all import *
    >>> s = String(nbChars=10, eos=['A'])
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-1:] == b'A'
    True
    >>> symbol = Symbol([Field(s)])
    >>> (symbol1, structured_data) = Symbol.abstract(data, [symbol])
    >>> symbol1 == symbol
    True
    >>> data = data[:-1] + b'\t'
    >>> (symbol2, structured_data) = Symbol.abstract(data, [symbol])
    >>> isinstance(symbol2, UnknownSymbol)
    True


    ## String with terminal character as a list of constants (specialization and abstraction)

    >>> from netzob.all import *
    >>> s = String(nbChars=10, eos=['A', 'B'])
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-1:] == b'A' or data[-1:] == b'B'
    True
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-1:] == b'A' or data[-1:] == b'B'
    True
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-1:] == b'A' or data[-1:] == b'B'
    True
    >>> symbol = Symbol([Field(s)])
    >>> (symbol1, structured_data) = Symbol.abstract(data, [symbol])
    >>> symbol1 == symbol
    True
    >>> data = data[:-1] + b'\t'
    >>> (symbol2, structured_data) = Symbol.abstract(data, [symbol])
    >>> isinstance(symbol2, UnknownSymbol)
    True


    ## String with terminal character as a mulitple characters constant (specialization and abstraction)

    >>> from netzob.all import *
    >>> s = String(nbChars=10, eos=['\r\n'])
    >>> data = s.generate().tobytes()
    >>> len(data) == 10
    True
    >>> data[-2:] == b'\r\n'
    True
    >>> symbol = Symbol([Field(s)])
    >>> (symbol1, structured_data) = Symbol.abstract(data, [symbol])
    >>> symbol1 == symbol
    True
    >>> data = data[:-2] + b'\r\t'
    >>> (symbol2, structured_data) = Symbol.abstract(data, [symbol])
    >>> isinstance(symbol2, UnknownSymbol)
    True


    # Verify that you cannot create a String with a value AND an nbChars:

    >>> i = String('test', nbChars=(2, 10))
    Traceback (most recent call last):
    ...
    ValueError: A String should have either its value or its nbChars set, but not both


    """
