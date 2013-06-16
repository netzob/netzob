# -*- coding: utf-8 -*-

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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Decimal import Decimal


class TypeConverter(object):
    """A type converter class which provide the convert method.
    """

    @staticmethod
    def __supportedTypes():
        return [
            # an array of bits: [1,0,0,1,1,0..]
            BitArray,
            # original python way of encoding data, raw data
            Raw,
            # string data
            ASCII,
            # decimal
            Decimal,
        ]

    @staticmethod
    def __directEncoding():
        return {
            #(ASCII,bitarray):TypeConverter.__encodeASCIIToBitarray,
        }

    @staticmethod
    def convert(data, sourceType, destinationType,
                src_unitSize=AbstractType.defaultUnitSize(), src_endianness=AbstractType.defaultEndianness(), src_sign=AbstractType.defaultSign(),
                dst_unitSize=AbstractType.defaultUnitSize(), dst_endianness=AbstractType.defaultEndianness(), dst_sign=AbstractType.defaultSign()):
        """Encode data provided as a sourceType to a destinationType.

        To convert an ASCII to its binary (bitarray) representation

        >>> data = "That's an helloworld!"
        >>> bin = TypeConverter.convert(data, ASCII, BitArray)
        >>> print bin
        bitarray('001010100001011010000110001011101110010011001110000001001000011001110110000001000001011010100110001101100011011011110110111011101111011001001110001101100010011010000100')
        >>> data == TypeConverter.convert(bin, BitArray, ASCII)
        True

        To convert a raw data to its decimal representation and then to its ASCII representation
        >>> data = '\x23'
        >>> decData = TypeConverter.convert(data, Raw, Decimal)
        >>> print decData
        35
        >>> print TypeConverter.convert(decData, Decimal, ASCII)
        #

        You can also play with the unitSize to convert multiple ascii in a single high value decimal
        >>> TypeConverter.convert("5", ASCII, Decimal)
        53
        >>> print TypeConverter.convert("zoby", ASCII, Decimal)
        Traceback (most recent call last):
        ...
        error: unpack requires a string argument of length 1
        >>> print TypeConverter.convert("zoby", ASCII, Decimal, dst_unitSize=AbstractType.UNITSIZE_32)
        2036494202



        :param sourceType: the data source type
        :type sourceType: :class:`type`
        :param destinationType: the destination type
        :type destinationType: :class:`type`
        :keyword src_unitSize: the unitsize to consider while encoding. Values must be one of AbstractType.UNITSIZE_*
        :type src_unitSize: str
        :keyword src_endianness: the endianness to consider while encoding. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type src_endianness: str
        :keyword src_sign: the sign to consider while encoding Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type src_sign: str
        :keyword dst_unitSize: the unitsize of the expected result. Values must be one of AbstractType.UNITSIZE_*
        :type dst_unitSize: str
        :keyword dst_endianness: the endianness of the expected result. Values must be AbstractType.ENDIAN_BIG or AbstractType.ENDIAN_LITTLE
        :type dst_endianness: str
        :keyword dst_sign: the sign of the expected result. Values must be AbstractType.SIGN_SIGNED or AbstractType.SIGN_UNSIGNED
        :type dst_sign: str

        :raise: TypeError if parameter not valid

        """
        # is the two formats supported ?
        if sourceType not in TypeConverter.__supportedTypes():
            raise TypeError("The source type ({0}) is not supported".format(sourceType.__name__))
        if destinationType not in TypeConverter.__supportedTypes():
            raise TypeError("The destination type ({0}) is not supported".format(destinationType.__name__))
        if data is None:
            raise TypeError("Data cannot be None")

        # Do we have a specific source to destination encoding function
        if (sourceType, destinationType) in TypeConverter.__directEncoding().keys():
            func = TypeConverter.__directEncoding()[(sourceType, destinationType)]
            return func(data, src_unitSize, src_endianness, src_sign, dst_unitSize, dst_endianness, dst_sign)
        else:
            # Convert from source to raw
            if sourceType is not Raw:
                binData = sourceType.decode(data, src_unitSize, src_endianness, src_sign)
            else:
                binData = data

            # Convert from raw to Destination
            if destinationType is not Raw:
                outputData = destinationType.encode(binData, dst_unitSize, dst_endianness, dst_sign)
            else:
                outputData = binData

            return outputData
