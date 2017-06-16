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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Common.Utils.Decorators import NetzobLogger, typeCheck


@NetzobLogger
class String(AbstractType):
    r"""This class defines a String type, in order to represent String or
    Unicode characters.

    The type String is a wrapper for the Python :class:`str` object
    with the capability to express more constraints on the permitted
    strings values.

    The String constructor expects some parameters:

    :param value: The current value of the type instance.
    :param nbChars: The amount of permitted String characters.
    :param encoding: The encoding of the string, such as 'ascii' or
                    'utf-8'. Default value is 'utf-8'.
    :param eof: A list defining the potential terminal characters for
                the string, with either specific constants or pointers
                to other fields containing the permitted terminal
                values. Default value is an empty list, meaning there
                is no terminal character.
    :param unitSize: Not implemented.
    :param endianness: Not implemented.
    :param sign: Not implemented.
    :type value: :class:`bitarray.bitarray`, optional
    :type nbChars: an :class:`int` or a tuple with the min and the max size specified as :class:`int`, optional
    :type encoding: :class:`str`, optional
    :type eof: a :class:`list` of :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>` or a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, optional


    Supported encodings are available on the Python reference documentation:

    .. _Python Standard Encodings: https://docs.python.org/3.4/library/codecs.html#standard-encodings


    Netzob allows describing a field that contains a String
    string. String strings can be either static or dynamic with fixed
    sizes or even dynamic with variable sizes.

    The following examples show how to define a static string in UTF-8:

    >>> from netzob.all import *
    >>> Field(String("Paris")).specialize()
    b'Paris'

    >>> Field(String("Paris in Euro: €")).specialize()
    b'Paris in Euro: \xe2\x82\xac'

    >>> Field(String("Paris in Euro: €", encoding='utf-8')).specialize()
    b'Paris in Euro: \xe2\x82\xac'

    The following example shows the raising of an exception if input
    value is not valid, with the definition of a String String where
    the associated value contains a non-String element:

    >>> Field(String("Paris in €", encoding='ascii')).specialize()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: Input value for the following string is incorrect: 'Paris in €'...

    The following example shows how to define a String string with a
    fixed size and a dynamic content:

    >>> f = Field(String(nbChars=10))

    The following example shows how to define a String string with a
    variable size and a dynamic content:

    >>> f = Field(String(nbChars=(10, 32)))


    **String with Terminal Character**

    Netzob supports strings with a terminal delimiter. Its usage is as
    follows:

    >>> f_eof    = Field(String('\t'))
    >>> f_string = Field(String(eof=[String('\n'), Raw('\x00'), f_eof]))

    The ``eof`` attribute specifies a list of values that is used as
    potential terminal characters. Terminal characters can either be
    defined as constants (such as ``String('\n')`` and ``Raw('\x00')``
    in the previous example) or defined as specific fields (such as
    ``f_eof`` in the previous example).


    **Examples of String Internal Attributes Access**

    >>> from netzob.all import *
    >>> cAscii = String("hello")
    >>> print(cAscii)
    String=hello ((None, None))
    >>> print(cAscii.typeName)
    String
    >>> print(cAscii.value)
    bitarray('0110100001100101011011000110110001101111')

    **Examples of Conversions**

    The following example shows how to convert the
    current type to any other Netzob type:

    >>> raw = cAscii.convertValue(Raw)
    >>> print(repr(raw))
    b'hello'
    >>> ip = cAscii.convertValue(IPv4)
    Traceback (most recent call last):
    ...
    TypeError: Impossible to encode b'hello' into an IPv4 data (unpack requires a bytes object of length 4)

    The type can be used to specify constraints over the domain:

    >>> a = String(nbChars=10)
    >>> print(a.value)
    None

    It is not possible to convert if the object has not value:

    >>> a.convertValue(Raw)
    Traceback (most recent call last):
    ...
    TypeError: Data cannot be None

    """

    def __init__(self,
                 value=None,
                 nbChars=(None, None),
                 encoding='utf-8',
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        self.encoding = encoding

        # Convert value to bitarray
        if value is not None and not isinstance(value, bitarray):

            # Check if value is correct, and normalize it in str object, and then bitarray
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
            nbBits = (None, None)

        super(String, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

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

    def generate(self, generationStrategy=None):
        """Generates a random String that respects the requested size.

        >>> from netzob.all import *
        >>> a = String(nbChars=10)
        >>> gen = a.generate()
        >>> len(gen)/8
        10.0

        >>> b = String("netzob")
        >>> b.generate() == TypeConverter.convert("netzob", String, BitArray)
        True

        """

        if self.value is not None:
            return self.value

        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize / 8, maxSize / 8)
        randomContent = ''.join([
            random.choice(string.printable)
            for i in range(generatedSize)
        ])
        return TypeConverter.convert(randomContent, String, BitArray)

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current String value.

        Mutations are first applied on the String value than, each obtained mutations generates
        new bitarray mutations.
        String mutations are:

        * Original Version
        * Original Version in Upper case
        * Original Version in Lower case

        >>> from netzob.all import *
        >>> t = String("helloworld")
        >>> values = t.mutate()
        >>> print(values['ascii(upper)-bits(littleEndian)'])
        bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')
        >>> print(values['ascii(inversed)-bits(bigEndian)'])
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
        >>> String().canParse(TypeConverter.convert("hello netzob", String, BitArray))
        True

        The ascii table is defined from 0 to 127:
        >>> String(encoding='ascii').canParse(TypeConverter.convert(128, Integer, BitArray, src_sign=Sign.UNSIGNED))
        False

        >>> a = String(nbChars=10)
        >>> a.canParse(TypeConverter.convert("hellohello", String, BitArray))
        True
        >>> a.canParse(TypeConverter.convert("hello hello", String, BitArray))
        False

        >>> a = String(nbChars=(2,20))
        >>> a.canParse(TypeConverter.convert("Netzob", String, BitArray))
        True
        >>> a.canParse(TypeConverter.convert("Hello netzob, what's up ?", String, BitArray))
        False

        >>> String("hello").canParse(TypeConverter.convert("hello", String, BitArray))
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

        # Check if data is correct, and normalize it in str object, and then bitarray
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
            if len(rawData) < (minChar/8):
                return False
        if maxChar is not None:
            if len(rawData) > (maxChar/8):
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
        >>> print(String.encode(raw))
        hello john!

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

    @encoding.setter
    @typeCheck(str)
    def encoding(self, encoding):
        if encoding is None:
            raise TypeError("Encoding cannot be None")
        self.__encoding = encoding
