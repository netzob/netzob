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
import struct
import random
import string
from bitarray import bitarray
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Utils.Decorators import NetzobLogger


@NetzobLogger
class ASCII(AbstractType):
    """The netzob type ASCII, a wrapper for the "string" object.

    >>> from netzob.all import *
    >>> cAscii = ASCII("constante value")
    >>> print repr(cAscii)
    constante value
    >>> print cAscii.typeName
    ASCII
    >>> print cAscii.value
    bitarray('110001101111011001110110110011100010111010000110011101100010111010100110000001000110111010000110001101101010111010100110')

    Use the convert function to convert the current type to any other netzob type
    >>> raw = cAscii.convertValue(Raw)
    >>> print repr(raw)
    constante value
    >>> ip = cAscii.convertValue(IPv4)
    Traceback (most recent call last):
    ...
    TypeError: Impossible encode constante value into an IPv4 data (unpack requires a string argument of length 4)

    The type can be used to specify constraints over the domain
    >>> a = ASCII(nbChars=10)
    >>> print a.value
    None

    Its not possible to convert if the object has not value
    >>> a.convertValue(Raw)
    Traceback (most recent call last):
    ...
    TypeError: Data cannot be None

    """

    def __init__(self, value=None, nbChars=(None, None)):
        if value is not None and not isinstance(value, bitarray):
            from netzob.Common.Models.Types.TypeConverter import TypeConverter
            from netzob.Common.Models.Types.BitArray import BitArray
            value = TypeConverter.convert(value, ASCII, BitArray)
        else:
            value = None

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

        super(ASCII, self).__init__(self.__class__.__name__, value, (nbMinBit, nbMaxBit))

    def generate(self, generationStrategy=None):
        """Generates a random ASCII that respects the requested size.

        >>> from netzob.all import *
        >>> a = ASCII(nbChars=10)
        >>> gen = a.generate()
        >>> len(gen)/8
        10

        >>> b = ASCII("netzob")
        >>> gen = b.generate()
        >>> print len(gen)>0
        True

        """
        from netzob.Common.Models.Types.TypeConverter import TypeConverter
        from netzob.Common.Models.Types.BitArray import BitArray

        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize / 8, maxSize / 8)
        randomContent = ''.join([random.choice(string.letters + string.digits) for i in xrange(generatedSize)])
        return TypeConverter.convert(randomContent, ASCII, BitArray)

    @staticmethod
    def canParse(data):
        """This method returns True if data is an ASCII

        >>> from netzob.all import *
        >>> ASCII.canParse(TypeConverter.convert("hello netzob", ASCII, Raw))
        True

        The ascii table is defined from 0 to 127:
        >>> ASCII.canParse(TypeConverter.convert(128, Decimal, Raw, src_sign=AbstractType.SIGN_UNSIGNED))
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

        for byte in data:
            # We naively try to decode in ascii the binary.
            try:
                byte.decode('ascii')
            except:
                return False
        return True

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> ASCII.decode("hello")
        'hello'
        >>> ASCII.decode('\x5a\x6f\x62\x79\x20\x69\x73\x20\x64\x61\x20\x70\x6c\x61\x63\x65\x20\x21')
        'Zoby is da place !'
        >>> ASCII.decode(1021)
        '1021'

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
        >>> print ASCII.encode(raw)
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

        return str(data)
