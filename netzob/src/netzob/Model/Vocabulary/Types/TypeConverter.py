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
import math

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer


class TypeConverter(object):
    """A type converter class which provide the convert method.
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
                src_unitSize=None,
                src_endianness=AbstractType.defaultEndianness(),
                src_sign=AbstractType.defaultSign(),
                dst_unitSize=None,
                dst_endianness=AbstractType.defaultEndianness(),
                dst_sign=AbstractType.defaultSign()):
        """Encode data provided as a sourceType to a destinationType.

        To convert an ASCII to its binary (bitarray) representation

        >>> from netzob.all import *
        >>> data = "That's an helloworld!"
        >>> bin = TypeConverter.convert(data, ASCII, BitArray)
        >>> print(bin)
        bitarray('010101000110100001100001011101000010011101110011001000000110000101101110001000000110100001100101011011000110110001101111011101110110111101110010011011000110010000100001')
        >>> data == TypeConverter.convert(bin, BitArray, ASCII)
        True

        To convert a raw data to its decimal representation and then to its ASCII representation

        >>> data = b'\\x23'
        >>> decData = TypeConverter.convert(data, Raw, Integer)
        >>> print(decData)
        35
        >>> print(TypeConverter.convert(decData, Integer, ASCII))
        #
        
        Conversion to and from Integer detects the output unitsize depending on the input:
        
        >>> TypeConverter.convert(b'\\x0b\\x00', Raw, Integer)
        2816
        >>> TypeConverter.convert(11, Integer, Raw)
        b'\\x0b'
        >>> TypeConverter.convert(b'\\xa0\\x0b', Raw, Integer, dst_sign=AbstractType.SIGN_SIGNED)
        -24565
        >>> TypeConverter.convert(-24565, Integer, Raw, src_sign=AbstractType.SIGN_SIGNED)
        b'\\xa0\\x0b'
        >>> TypeConverter.convert(0, Integer, Raw)
        b'\\x00'
        >>> TypeConverter.convert(b'\\x00\\x00\\x00', Raw, Integer)
        Traceback (most recent call last):
        ...
        TypeError: Unsupported autodetected Integer target UnitSize. Valid UnitSizes are 8, 16, 32 and 64 bits.

        You can also play with the unitSize to convert multiple ascii in a single high value decimal

        >>> TypeConverter.convert("5", ASCII, Integer)
        53
        >>> print(TypeConverter.convert("zoby", ASCII, Integer))
        2054120057
        >>> print(TypeConverter.convert("zoby", ASCII, Integer, dst_unitSize=AbstractType.UNITSIZE_32))
        2054120057

        It also works for 'semantic' data like IPv4s

        >>> TypeConverter.convert("192.168.0.10", IPv4, Integer, dst_sign=AbstractType.SIGN_UNSIGNED)
        3232235530
        >>> TypeConverter.convert("127.0.0.1", IPv4, BitArray)
        bitarray('01111111000000000000000000000001')
        >>> TypeConverter.convert(167815360, Integer, IPv4, src_unitSize=AbstractType.UNITSIZE_32, src_sign=AbstractType.SIGN_UNSIGNED)
        IPAddress('10.0.168.192')

        To check Integer conversion consistency
        >>> f = Field(b'some')
        >>> v = f.domain.currentValue.tobytes()
        >>> try:
        ...     v_hex = v.hex()
        ... except AttributeError:
        ...     import codecs # Python <= 3.4: 'bytes' object has no attribute 'hex'
        ...     v_hex = codecs.encode(v, 'hex_codec').decode('ascii')
        >>> '0x'+v_hex == hex(TypeConverter.convert(f.domain.currentValue, BitArray, Integer))
        True

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
	# Use defaultUnitSize for all types except Integer
        if dst_unitSize is None and destinationType is not Integer: 
            dst_unitSize = AbstractType.defaultUnitSize()
        if src_unitSize is None and sourceType is not Integer:
            src_unitSize = AbstractType.defaultUnitSize()

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
                if sourceType is Integer and src_unitSize is None:
                    src_unitSize = Integer.checkUnitSizeForValue(data,src_sign)

                binData = sourceType.decode(
                    data,
                    unitSize=src_unitSize,
                    endianness=src_endianness,
                    sign=src_sign)
            else:
                binData = data

            # Convert from raw to Destination
            if destinationType is not Raw:
                if destinationType is Integer and dst_unitSize is None:
                    nbUnits = len(binData)
                    if nbUnits == 8:
                        dst_unitSize = AbstractType.UNITSIZE_64
                    elif nbUnits == 4:
                        dst_unitSize = AbstractType.UNITSIZE_32
                    elif nbUnits == 2:
                        dst_unitSize = AbstractType.UNITSIZE_16
                    elif nbUnits == 1:
                        dst_unitSize = AbstractType.UNITSIZE_8
                    else:
                        raise TypeError("Unsupported autodetected Integer target UnitSize. Valid UnitSizes are 8, 16, 32 and 64 bits.")
                outputData = destinationType.encode(
                    binData,
                    unitSize=dst_unitSize,
                    endianness=dst_endianness,
                    sign=dst_sign)
            else:
                outputData = binData

            return outputData
