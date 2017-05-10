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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.Raw import Raw


class TypeConverter(object):
    """The TypeConverter class provides a conversion function between types.
    """

    @staticmethod
    def supportedTypes():
        """Official list of supported types

        @deprecated: please use directly the AbstractType.supportedTypes() method instead of this wrapper.
        """
        return AbstractType.supportedTypes()

    @staticmethod
    def __directEncoding():
        return {
            # (ASCII,bitarray):TypeConverter.__encodeASCIIToBitarray,
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
        """This function allows to encode data from a sourceType to a destinationType.

        :param sourceType: The data source type
        :param destinationType: The destination type
        :keyword str src_unitSize: The unitsize to consider while encoding. Value must be one of AbstractType.UNITSIZE_*
        :keyword str src_endianness: The endianness to consider while encoding. Value must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :keyword str src_sign: The sign to consider while encoding. Value must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :keyword str dst_unitSize: The unitsize of the expected result. Value must be one of AbstractType.UNITSIZE_*
        :keyword str dst_endianness: The endianness of the expected result. Value must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :keyword str dst_sign: The sign of the expected result. Value must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type sourceType: :class:`type`
        :type destinationType: :class:`type`
        :raise: TypeError if parameters are not valid


        For example, to convert an ASCII to a binary (BitArray) representation:

        >>> from netzob.all import *
        >>> data = "hello"
        >>> bin = TypeConverter.convert(data, ASCII, BitArray)
        >>> print(bin)
        bitarray('0110100001100101011011000110110001101111')
        >>> data == TypeConverter.convert(bin, BitArray, ASCII)
        True

        To convert a raw data to an integer representation and then to an ASCII representation:

        >>> data = b'\\x23'
        >>> decData = TypeConverter.convert(data, Raw, Integer)
        >>> print(decData)
        35
        >>> print(TypeConverter.convert(decData, Integer, ASCII))
        #

        You can also modify the unitSize to convert multiple ASCII to a single high value integer:

        >>> TypeConverter.convert("5", ASCII, Integer)
        53
        >>> print(TypeConverter.convert("zoby", ASCII, Integer))
        2036494202
        >>> print(TypeConverter.convert("zoby", ASCII, Integer, dst_unitSize=AbstractType.UNITSIZE_32))
        2054120057

        It also works for 'semantic' data like IPv4:

        >>> TypeConverter.convert("192.168.0.10", IPv4, Integer, dst_sign=AbstractType.SIGN_UNSIGNED)
        167815360
        >>> TypeConverter.convert("127.0.0.1", IPv4, BitArray)
        bitarray('01111111000000000000000000000001')
        >>> TypeConverter.convert(167815360, Integer, IPv4, src_unitSize=AbstractType.UNITSIZE_32, src_sign=AbstractType.SIGN_UNSIGNED)
        IPAddress('10.0.168.192')

        """
        # is the two formats supported ?
        if sourceType not in TypeConverter.supportedTypes():
            raise TypeError(
                "The source type ({0}) is not supported".format(sourceType))
        if destinationType not in TypeConverter.supportedTypes():
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
