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
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, UnitSize
from netzob.Model.Vocabulary.Types.Raw import Raw


class TypeConverter(object):
    """The TypeConverter class provides a conversion function between types.
    """

    @staticmethod
    def __directEncoding():
        return {
            # (String, bitarray):TypeConverter.__encodeStringToBitarray,
        }

    @staticmethod
    def convert(data,
                sourceType,
                destinationType,
                src_unitSize=AbstractType.defaultUnitSize(),
                src_endianness=AbstractType.defaultEndianness(),
                src_sign=AbstractType.defaultSign(),
                dst_unitSize=AbstractType.defaultUnitSize(),
                dst_endianness=AbstractType.defaultEndianness(),
                dst_sign=AbstractType.defaultSign()):
        r"""This function encodes data from a sourceType to a destinationType.

        :param sourceType: The data source type
        :param destinationType: The destination type
        :keyword Enum src_unitSize: The unitsize to consider while encoding. Value must be one of UnitSize.SIZE_*
        :keyword Enum src_endianness: The endianness to consider while encoding. Value must be Endianness.BIG or Endianness.LITTLE
        :keyword Enum src_sign: The sign to consider while encoding. Value must be Sign.SIGNED or Sign.UNSIGNED
        :keyword Enum dst_unitSize: The unitsize of the expected result. Value must be one of UnitSize.SIZE_*
        :keyword Enum dst_endianness: The endianness of the expected result. Value must be Endianness.BIG or Endianness.LITTLE
        :keyword Enum dst_sign: The sign of the expected result. Value must be Sign.SIGNED or Sign.UNSIGNED
        :type sourceType: :class:`type`
        :type destinationType: :class:`type`
        :raise: TypeError if parameters are not valid


        For example, to convert a String to a binary (BitArray) representation:

        >>> from netzob.all import *

        >>> data = b"hello"
        >>> bin = TypeConverter.convert(data, String, BitArray)
        >>> print(bin)
        bitarray('0110100001100101011011000110110001101111')
        >>>
        >>> data == TypeConverter.convert(bin, BitArray, String)
        True

        To convert a raw data to an integer representation and then to a String representation:

        >>> data = b'\x23'
        >>> decData = TypeConverter.convert(data, Raw, Integer)
        >>> print(decData)
        35
        >>> print(TypeConverter.convert(decData, Integer, String))
        b'#'

        You can also modify the unitSize to convert multiple String to a single high value integer:

        >>> TypeConverter.convert(b"5", String, Integer)
        53
        >>> print(TypeConverter.convert(b"kurt", String, Integer))
        1953658219
        >>> print(TypeConverter.convert(b"kurt", String, Integer,
        ...                             dst_unitSize=UnitSize.SIZE_32))
        1802859124

        It also works for 'semantic' data like IPv4:

        >>> TypeConverter.convert("192.168.0.10", IPv4, Integer,
        ...                       dst_sign=Sign.UNSIGNED)
        167815360
        >>> TypeConverter.convert("127.0.0.1", IPv4, BitArray)
        bitarray('01111111000000000000000000000001')
        >>> TypeConverter.convert(167815360, Integer, IPv4,
        ...                       src_unitSize=UnitSize.SIZE_32,
        ...                       src_sign=Sign.UNSIGNED)
        IPAddress('10.0.168.192')

        """
        # are the two formats supported ?
        if not issubclass(sourceType, AbstractType):
            raise TypeError(
                "The source type ({0}) is not supported".format(sourceType))
        if not issubclass(destinationType, AbstractType):
            raise TypeError("The destination type ({0}) is not supported".
                            format(destinationType))
        if data is None:
            raise TypeError("Data cannot be None")

        # Do we have a specific source to destination encoding function
        if (sourceType, destinationType
            ) in list(TypeConverter.__directEncoding().keys()):
            func = TypeConverter.__directEncoding()[(sourceType,
                                                     destinationType)]
            return func(data, src_unitSize, src_endianness, src_sign,
                        dst_unitSize, dst_endianness, dst_sign)
        else:

            # Convert from source to raw
            if sourceType is not Raw:
                binData = sourceType.decode(
                    data,
                    unitSize=src_unitSize,
                    endianness=src_endianness,
                    sign=src_sign)
            else:
                binData = data

            # Convert from raw to Destination
            if destinationType is not Raw:
                outputData = destinationType.encode(
                    binData,
                    unitSize=dst_unitSize,
                    endianness=dst_endianness,
                    sign=dst_sign)
            else:
                outputData = binData

            return outputData
