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
import binascii
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.ASCII import ASCII


class HexaString(AbstractType):

    def __init__(self, value=None, size=(None, None)):
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Types.TypeConverter import TypeConverter
            from netzob.Model.Types.BitArray import BitArray
            value = TypeConverter.convert(value, HexaString, BitArray)

        super(HexaString, self).__init__(self.__class__.__name__, value, size)

    def canParse(self, data):
        """It verifies the value is a string which only includes hexadecimal values.

        >>> from netzob.all import *
        >>> HexaString().canParse(TypeConverter.convert("0001020304050607080910", ASCII, Raw))
        True
        >>> HexaString().canParse(TypeConverter.convert("hello", ASCII, Raw))
        False

        Let's generate random binary raw data, convert it to HexaString
        and verify we can parse this

        >>> import os
        >>> # Generate 8 random bytes
        >>> randomData = os.urandom(8)
        >>> hex = TypeConverter.convert(randomData, Raw, HexaString)
        >>> len(hex)
        16
        >>> print(HexaString().canParse(hex))
        True

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as an hexastring
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")

        if len(data) == 0:
            return False

        # import logging
        # logger = logging.getLogger(__name__)

        # logger.warn("PAF: {0}".format(data))
            
        # if not ASCII().canParse(data):
        #     logger.warn("OUPS: {0}".format(data))
        #     return False

        # try:
        #     value = ASCII.encode(data)
        # except:
        #     return False

        allowedValues = [str(i) for i in range(0, 10)]
        allowedValues.extend(["a", "b", "c", "d", "e", "f"])

        str_data = data.decode('utf-8')
        for i in range(0, len(data)):
            if not str_data[i] in allowedValues:
                return False

        return True

    @staticmethod
    @typeCheck(str)
    def decode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the specified data in python raw format.

        >>> from netzob.all import *
        >>> import os
        >>> # Generate 1024 random bytes
        >>> randomData = os.urandom(1024)
        >>> # Convert to hexastring
        >>> hex = TypeConverter.convert(randomData, Raw, HexaString)
        >>> print(len(hex))
        2048
        >>> # Convert back to byte and verify we didn't lost anything
        >>> raw = TypeConverter.convert(hex, HexaString, Raw)
        >>> print(raw == randomData)
        True


        :param data: the data encoded in hexaString (str) which will be decoded in raw
        :type data: str
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
        if data is None:
            raise TypeError("data cannot be None")

        if len(data) % 2 == 1:
            data = '0' + data

        return binascii.unhexlify(data)

    @staticmethod
    def encode(data, unitSize=AbstractType.defaultUnitSize(), endianness=AbstractType.defaultEndianness(), sign=AbstractType.defaultSign()):
        """This method convert the python raw data to an HexaString

        >>> from netzob.all import *
        >>> import os
        >>> # Generate 4096 random bytes
        >>> randomData = os.urandom(4096)
        >>> # Convert to hexastring
        >>> hex = TypeConverter.convert(randomData, Raw, HexaString)
        >>> print(len(hex))
        8192
        >>> # Convert back to byte and verify we didn't lost anything
        >>> raw = TypeConverter.convert(hex, HexaString, Raw)
        >>> print(raw == randomData)
        True

        :param data: the data encoded in python raw which will be encoded in current type
        :type data: python raw
        :keyword unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type unitSize: str
        :keyword endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type endianness: str
        :keyword sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sign: str

        :return: data encoded in Hexa String
        :rtype: python str
        :raise: TypeError if parameters are not valid.
        """
        if data is None:
            raise TypeError("data cannot be None")

        return binascii.hexlify(data)

