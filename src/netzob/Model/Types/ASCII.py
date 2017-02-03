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
import string
import collections

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Common.Utils.Decorators import NetzobLogger, typeCheck


@NetzobLogger
class ASCII(AbstractType):
    """The netzob type ASCII, a wrapper for the "string" object (encoded in utf-8)

    >>> from netzob.all import *
    >>> cAscii = ASCII("constante value")
    >>> print(cAscii)
    ASCII=constante value ((0, 120))
    >>> print(cAscii.typeName)
    ASCII
    >>> print(cAscii.value)
    bitarray('011000110110111101101110011100110111010001100001011011100111010001100101001000000111011001100001011011000111010101100101')

    Use the convert function to convert the current type to any other netzob type
    >>> raw = cAscii.convertValue(Raw)
    >>> print(repr(raw))
    b'constante value'
    >>> ip = cAscii.convertValue(IPv4)
    Traceback (most recent call last):
    ...
    TypeError: Impossible encode b'constante value' into an IPv4 data (unpack requires a bytes object of length 4)

    The type can be used to specify constraints over the domain
    >>> a = ASCII(nbChars=10)
    >>> print(a.value)
    None

    Its not possible to convert if the object has not value
    >>> a.convertValue(Raw)
    Traceback (most recent call last):
    ...
    TypeError: Data cannot be None

    """

    def __init__(self, value=None, nbChars=(None, None), unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            value = TypeConverter.convert(value, ASCII, BitArray, src_unitSize=unitSize, src_endianness=endianness, src_sign=sign, dst_unitSize=unitSize, dst_endianness=endianness, dst_sign=sign)
        else:
            value = None

        self.nbChars = nbChars
        nbBits = self._convertNbCharsInNbBits(self.nbChars)

        super(ASCII, self).__init__(self.__class__.__name__, value, nbBits, unitSize=unitSize, endianness=endianness, sign=sign)

    def _convertNbCharsInNbBits(self, nbChars):
        nbMinBit = None
        nbMaxBit = None
        if nbChars is not None:
            if isinstance(nbChars, int):
                nbMinBit = nbChars * 8
                nbMaxBit = nbMinBit
            else:
                if nbChars[0] is not None:
                    nbMinBit = nbChars[0] * 8
                if nbChars[1] is not None:
                    nbMaxBit = nbChars[1] * 8
        return (nbMinBit, nbMaxBit)

    def generate(self, generationStrategy=None):
        """Generates a random ASCII that respects the requested size.

        >>> from netzob.all import *
        >>> a = ASCII(nbChars=10)
        >>> gen = a.generate()
        >>> len(gen)/8
        10.0

        >>> b = ASCII("netzob")
        >>> gen = b.generate()
        >>> print(len(gen)>0)
        True

        """
        from netzob.Model.Types.TypeConverter import TypeConverter
        from netzob.Model.Types.BitArray import BitArray

        minSize, maxSize = self.nbChars
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
        if minSize is None:
            minSize = 0

        generatedSize = random.randint(minSize, maxSize)
        randomContent = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(generatedSize)])
        return TypeConverter.convert(randomContent, ASCII, BitArray)

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current ASCII value.

        Mutations are first applied on the ASCII value than, each obtained mutations generates
        new bitarray mutations.
        ASCII mutations are:

        * Original Version
        * Original Version in Upper case
        * Original Version in Lower case

        >>> from netzob.all import *
        >>> t = ASCII("helloworld")
        >>> values = t.mutate()
        >>> print(values['ascii(upper)-bits(littleEndian)'])
        bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')
        >>> print(values['ascii(inversed)-bits(bigEndian)'])
        bitarray('01100100011011000111001001101111011101110110111101101100011011000110010101101000')


        :keyword prefixDescription: prefix to attach to the description of the generated mutation.
        :type prefixDescription: :class:`str`
        :return: a dict of computed mutations having the same types than the initial one.
        :rtype: :class:`dict`<str>=:class:`netzob.Model.Types.AbstractType.AbstractType`
        """
        if prefixDescription is None:
            prefixDescription = ""
        else:
            prefixDescription += "-"

        from netzob.Model.Types.TypeConverter import TypeConverter
        from netzob.Model.Types.BitArray import BitArray

        if self.value is None:
            val = self.generate()
        else:
            val = self.value

        strValue = TypeConverter.convert(val, BitArray, ASCII)

        mutations = collections.OrderedDict()

        mutations["{0}ascii".format(prefixDescription)] = strValue
        mutations["{0}ascii(inversed)".format(prefixDescription)] = strValue[::-1]
        if strValue != strValue.upper():
            mutations["{0}ascii(upper)".format(prefixDescription)] = strValue.upper()
            mutations["{0}ascii(inversed-upper)".format(prefixDescription)] = strValue[::-1].upper()
        if strValue != strValue.lower():
            mutations["{0}ascii(lower)".format(prefixDescription)] = strValue.lower()
            mutations["{0}ascii(inversed-lower)".format(prefixDescription)] = strValue[::-1].lower()

        results = collections.OrderedDict()
        for mutationName, mutationValue in list(mutations.items()):
            ba = BitArray(TypeConverter.convert(mutationValue, ASCII, BitArray))
            results.update(ba.mutate(mutationName))

        return results

    def canParse(self, data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method returns True if data is an ASCII (utf-8)

        >>> from netzob.all import *
        >>> ASCII().canParse(TypeConverter.convert("hello netzob", ASCII, BitArray))
        True

        The ascii table is defined from 0 to 127:
        >>> ASCII().canParse(TypeConverter.convert(128, Integer, BitArray, src_sign=AbstractType.SIGN_UNSIGNED))
        False

        >>> a = ASCII(nbChars=10)
        >>> a.canParse(TypeConverter.convert("hellohello", ASCII, BitArray))
        True
        >>> a.canParse(TypeConverter.convert("hello hello", ASCII, BitArray))
        False

        >>> a = ASCII(nbChars=(2,20))
        >>> a.canParse(TypeConverter.convert("Netzob", ASCII, BitArray))
        True
        >>> a.canParse(TypeConverter.convert("Hello netzob, what's up ?", ASCII, BitArray))
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as an ASCII
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        # Ascii must be 8 bits modulo length
        if len(data) % 8 != 0:
            return False

        rawData = data.tobytes()

        try:
            rawData.decode('utf-8')
        except:
            return False

        (minChar, maxChar) = self.nbChars
        if minChar is not None:
            if len(rawData) < minChar:
                return False
        if maxChar is not None:
            if len(rawData) > maxChar:
                return False

        return True

    @property
    def nbChars(self):
        return self.__nbChars

    @nbChars.setter
    def nbChars(self, nbChars):
        nbMinChar = None
        nbMaxChar = None
        if nbChars is not None:
            if isinstance(nbChars, int):
                nbMinChar = nbChars
                nbMaxChar = nbMinChar
            else:
                if nbChars[0] is not None:
                    if not isinstance(nbChars[0], int):
                        raise TypeError("First element of the tupple of the nbChars must be an int if defined.")
                    nbMinChar = nbChars[0]
                if nbChars[1] is not None:
                    if not isinstance(nbChars[1], int):
                        raise TypeError("Second element of the tupple of the nbChars must be an int if defined.")
                    nbMaxChar = nbChars[1]

        self.__nbChars = (nbMinChar, nbMaxChar)

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> ASCII.decode("hello")
        b'hello'
        >>> ASCII.decode('\x5a\x6f\x62\x79\x20\x69\x73\x20\x64\x61\x20\x70\x6c\x61\x63\x65\x20\x21')
        b'Zoby is da place !'
        >>> ASCII.decode(1021)
        b'1021'

        :param data: the data encoded in ASCII which will be decoded in raw
        :type data: the current type
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        return str(data).encode('utf-8')

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the python raw data to the ASCII.

        >>> from netzob.all import *
        >>> raw = ASCII.decode("hello zoby!")
        >>> print(ASCII.encode(raw))
        hello zoby!

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

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

