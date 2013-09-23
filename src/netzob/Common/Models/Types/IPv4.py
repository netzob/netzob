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
import string
from random import randrange

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from netaddr import IPAddress

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType


class IPv4(AbstractType):
    """This class supports the definition of type IPv4 in Netzob.
    it defines how to encode a python raw in an IPv4 representation or in the other way, to
    decode an IPv4 into a Raw.


    >>> from netzob.all import *
    >>> f1 = Field("IP=")
    >>> f2 = Field(IPv4())

    >>> f2.domain.learnable = False
    >>> s = Symbol(fields=[f1,f2])
    >>> msgs = [RawMessage(s.generate()) for x in xrange(10)]
    >>> s.messages = msgs
    >>> # Display the number of lines in the getcells()
    >>> print len(str(s).split('\\n'))
    10


    """
    def __init__(self, value=None, size=None):
        super(IPv4, self).__init__(self.__class__.__name__, value, None)

    def buildDataRepresentation(self):
        from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data import Data
        from netzob.Common.Models.Types.TypeConverter import TypeConverter
        from netzob.Common.Models.Types.Raw import Raw
        from netzob.Common.Models.Types.BitArray import BitArray
        (minSize, maxSize) = (32, 32)

        if self.value is not None:
            binValue = TypeConverter.convert(self.value, Raw, BitArray)
        else:
            binValue = None
        return Data(dataType=IPv4, originalValue=binValue, size=(minSize, maxSize))

    def generate(self, generationStrategy=None):
        """Generates a random IPv4
        """
        from netzob.Common.Models.Types.BitArray import BitArray
        from netzob.Common.Models.Types.TypeConverter import TypeConverter
        from netzob.Common.Models.Types.Raw import Raw

        not_valid = [10, 127, 169, 172, 192]

        first = randrange(1, 256)
        while first in not_valid:
            first = randrange(1, 256)

        strip = ".".join([str(first), str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256))])

        ip = IPv4.encode(strip)
        return TypeConverter.convert(ip.packed, Raw, BitArray)

    @staticmethod
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """Decode the specified IPv4 data into its raw representation.

        >>> from netzob.all import *
        >>> print IPv4.decode("127.0.0.1")
        \x7f\x00\x00\x01

        """

        if data is None:
            raise TypeError("Data cannot be None")
        if not IPv4.canParse(data):
            raise TypeError("Data is not a valid IPv4, cannot decode it.")
        ip = IPAddress(data)
        return ip.packed

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """Encodes the specified data into an IPAddress object

        :param data: the data to encode into an IPAddress
        :type data: str or raw bytes (BBBB)
        :return: the encoded IPAddress
        """
        if isinstance(data, str):
            try:
                ip = IPAddress(data)
                if ip is not None and ip.version == 4 and not ip.is_netmask():
                    return ip
            except:
                pass
        try:

            structFormat = ">"
            if endianness == AbstractType.ENDIAN_BIG:
                structFormat = ">"

            if not sign == AbstractType.SIGN_SIGNED:
                structFormat += "bbbb"
            else:
                structFormat += "BBBB"
            quads = map(str, struct.unpack(structFormat, data))
            strIP = string.join(quads, '.')

            ip = IPAddress(strIP)
            if ip is not None and ip.version == 4 and not ip.is_netmask():
                return ip
        except Exception, e:
            raise TypeError("Impossible encode {0} into an IPv4 data ({1})".format(data, e))

    @staticmethod
    def canParse(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        r"""Computes if specified data can be parsed as an IPv4.

        >>> from netzob.all import *
        >>> IPv4.canParse("192.168.0.10")
        True
        >>> IPv4.canParse("198.128.0.100")
        True
        >>> IPv4.canParse("256.0.0.1")
        False
        >>> IPv4.canParse("127.0.0.1")
        True
        >>> IPv4.canParse("127.0.0.-1")
        False

        >>> IPv4.canParse("::")
        False
        >>> IPv4.canParse("0.0.0.0")
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        try:
            ip = IPv4.encode(data, unitSize=unitSize, endianness=endianness, sign=sign)
            if ip is None or ip.version != 4 or ip.is_netmask():
                return False
        except:
            return False

        return True
