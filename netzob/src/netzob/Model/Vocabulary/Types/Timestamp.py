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
import unittest
from datetime import datetime, timedelta

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer


@NetzobLogger
class Timestamp(AbstractType):
    r"""This class defines a Timestamp type.

    The Timestamp type defines dates in a specific format
    (such as Windows, Unix or MacOSX formats).

    The Timestamp constructor expects some parameters:

    :param value: The raw value of the timestamp (in seconds by default). If None, the default generated value is the current time in UTC.
    :param epoch: The initial date expressed in UTC from which
                  timestamp is measured. Default value is EPOCH_UNIX.
    :param unity: This specifies the unity of the timestamp (seconds,
                  milliseconds, nanoseconds). The default value is
                  UNITY_SECOND.
    :param unitSize: The unitsize of the current value. Values must be one of UnitSize.SIZE_* (see below for supported unit sizes). The default value is UnitSize.SIZE_32.
    :param endianness: The endianness of the current value. Values must be Endianness.BIG or Endianness.LITTLE. The default value is Endianness.BIG.
    :param sign: The sign of the current value. Values must be Sign.SIGNED or Sign.UNSIGNED. The default value is Sign.SIGNED.
    :type value: :class:`bitarray.bitarray` or :class:`int`, optional
    :type epoch: :class:`datetime.datetime`, optional
    :type unity: :class:`int`, optional
    :type unitSize: :class:`Enum`, optional
    :type endianness: :class:`Enum`, optional
    :type sign: :class:`Enum`, optional


    The Timestamp class provides the following public variables:

    :var typeName: The name of the implemented data type.
    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size in bits of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max value.
    :var unitSize: The unitsize of the current value. Values must be one of UnitSize.SIZE_* (see below for supported unit sizes).
    :var epoch: The initial date expressed in UTC from which
                timestamp is measured.
    :var unity: This specifies the unity of the timestamp (seconds,
                milliseconds, nanoseconds).
    :vartype typeName: :class:`str`
    :vartype value: :class:`bitarray.bitarray`
    :vartype size: a tuple (:class:`int`, :class:`int`) or :class:`int`
    :vartype unitSize: :class:`Enum`, optional
    :vartype epoch: :class:`datetime.datetime`
    :vartype unity: :class:`int`


    Available values for `epoch` parameter are:

    * EPOCH_WINDOWS = datetime(1601, 1, 1)
    * EPOCH_MUMPS = datetime(1840, 12, 31)
    * EPOCH_VMS = datetime(1858, 11, 17)
    * EPOCH_EXCEL = datetime(1899, 12, 31)
    * EPOCH_NTP = datetime(1900, 1, 1)
    * EPOCH_MACOS_9 = datetime(1904, 1, 1)
    * EPOCH_PICKOS = datetime(1967, 12, 31)
    * EPOCH_UNIX = datetime(1970, 1, 1)
    * EPOCH_FAT = datetime(1980, 1, 1)
    * EPOCH_GPS = datetime(1980, 1, 6)
    * EPOCH_ZIGBEE = datetime(2000, 1, 1)
    * EPOCH_COCOA = datetime(2001, 1, 1)

    Available values for `unity` parameter are:

    * UNITY_SECOND = 1
    * UNITY_DECISECOND = 10
    * UNITY_CENTISECOND = 100
    * UNITY_MILLISECOND = 1000
    * UNITY_MICROSECOND = 1000000
    * UNITY_NANOSECOND = 10000000000

    In the following example, a Timestamp data is created with a
    specific value '1444492442' and represented as 32 bits:

    >>> from netzob.all import *
    >>> time = Timestamp(1444492442)
    >>> time.size
    (None, None)
    >>> time.value
    bitarray('01010110000110010011010010011010')
    >>> time.sign
    Sign.UNSIGNED
    >>> time.endianness
    Endianness.BIG


    .. ifconfig:: scope in ('netzob')

       >>> from netzob.all import *
       >>> f0 = Field(Raw(b"00"), name="Start")
       >>> f1 = Field(Timestamp(1444737333), name="Timestamp")
       >>> f2 = Field(Raw(b"00"), name="End")
       >>> s = Symbol(fields=[f0, f1, f2])
       >>> s.messages = [RawMessage(s.specialize()) for x in range(5)]
       >>> print(s.str_data())
       Start | Timestamp     | End 
       ----- | ------------- | ----
       '00'  | b'V\x1c\xf15' | '00'
       '00'  | b'V\x1c\xf15' | '00'
       '00'  | b'V\x1c\xf15' | '00'
       '00'  | b'V\x1c\xf15' | '00'
       '00'  | b'V\x1c\xf15' | '00'
       ----- | ------------- | ----


    .. ifconfig:: scope in ('netzob')

       >>> s.fields[1].addEncodingFunction(TypeEncodingFunction(Timestamp))
       >>> print(s.str_data())
       Start | Timestamp                  | End 
       ----- | -------------------------- | ----
       '00'  | 'Tue Oct 13 11:55:33 2015' | '00'
       '00'  | 'Tue Oct 13 11:55:33 2015' | '00'
       '00'  | 'Tue Oct 13 11:55:33 2015' | '00'
       '00'  | 'Tue Oct 13 11:55:33 2015' | '00'
       '00'  | 'Tue Oct 13 11:55:33 2015' | '00'
       ----- | -------------------------- | ----

    """

    EPOCH_WINDOWS = datetime(1601, 1, 1)
    EPOCH_MUMPS = datetime(1840, 12, 31)
    EPOCH_VMS = datetime(1858, 11, 17)
    EPOCH_EXCEL = datetime(1899, 12, 31)
    EPOCH_NTP = datetime(1900, 1, 1)
    EPOCH_MACOS_9 = datetime(1904, 1, 1)
    EPOCH_PICKOS = datetime(1967, 12, 31)
    EPOCH_UNIX = datetime(1970, 1, 1)
    EPOCH_FAT = datetime(1980, 1, 1)
    EPOCH_GPS = datetime(1980, 1, 6)
    EPOCH_ZIGBEE = datetime(2000, 1, 1)
    EPOCH_COCOA = datetime(2001, 1, 1)

    UNITY_SECOND = 1
    UNITY_DECISECOND = 10
    UNITY_CENTISECOND = 100
    UNITY_MILLISECOND = 1000
    UNITY_MICROSECOND = 1000000
    UNITY_NANOSECOND = 10000000000

    def __init__(self,
                 value=None,
                 epoch=EPOCH_UNIX,
                 unity=UNITY_SECOND,
                 unitSize=UnitSize.SIZE_32,
                 endianness=AbstractType.defaultEndianness(),
                 sign=Sign.UNSIGNED):
        if value is not None and not isinstance(value, bitarray):
            # converts the specified value in bitarray
            value = TypeConverter.convert(
                value,
                Integer,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign)

        self.epoch = epoch
        self.unity = unity

        # Handle data size if value is None
        if value is None:
            nbBits = (unitSize.value, unitSize.value)
        else:
            nbBits = (None, None)

        super(Timestamp, self).__init__(
            self.__class__.__name__,
            value,
            nbBits,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        """Computes if specified data can be parsed as a Timestamp with the
        predefined constraints.

        >>> from netzob.all import *
        >>> time = Timestamp()
        >>> time.canParse(Integer(1444494130, unitSize=UnitSize.SIZE_32).value)
        True
        >>> # A timestamp is nothing else than 32bits parsed as an unsigned long
        >>> time.canParse(String("test").value)
        True
        >>> time.canParse(String("te").value)
        False

        However, some constrains over the definition of the Timestamp can be set to restrain the accepted values

        >>> from netzob.all import *
        >>> time = Timestamp(epoch=Timestamp.EPOCH_WINDOWS, unity=Timestamp.UNITY_NANOSECOND, unitSize=UnitSize.SIZE_64)
        >>> # the returned year is < 1900
        >>> time.canParse(String("test").value)
        False
        """

        if data is None:
            raise TypeError("data cannot be None")

        # Timestamp must be 8 bits modulo length
        if len(data) % 8 != 0:
            return False

        if len(data) < int(self.unitSize.value):
            return False

        try:

            value = TypeConverter.convert(
                data[:int(self.unitSize.value)],
                BitArray,
                Integer,
                dst_unitSize=UnitSize.SIZE_32,
                dst_sign=Sign.UNSIGNED)

            # convert the value in seconds
            value = value / self.unity

            # add the utc now with the epoch
            timestamp_datetime = self.epoch + timedelta(seconds=value)

            # convert obtained datetime to timestamp in seconds
            result_sec = int(timestamp_datetime.strftime('%s'))

            datetime.fromtimestamp(result_sec)
        except Exception:
            return False

        return True

    def getMinStorageValue(self):
            return 0

    def getMaxStorageValue(self):
            return 2**self.unitSize.value - 1

    def generate(self, generationStrategy=None):
        """Generates a Timestamp that follows the specified generationStrategy

        >>> from netzob.all import *
        >>> f = Field(Timestamp())
        >>> value = f.specialize()
        >>> len(value)
        4
        >>> f = Field(Timestamp(epoch=Timestamp.EPOCH_WINDOWS, unitSize=UnitSize.SIZE_64))
        >>> len(f.specialize())
        8
        """
        if self.value is not None:
            return self.value

        # computes utc now
        now = datetime.utcnow()

        # substract the utc now with the epoch
        timestamp_datetime = now - self.epoch

        # convert obtained datetime to timestamp in seconds
        result_sec = timestamp_datetime.total_seconds()

        # apply the unity
        result_unity = int(result_sec * self.unity)

        # convert to bitarray
        final = TypeConverter.convert(
            result_unity,
            Integer,
            BitArray,
            src_unitSize=self.unitSize,
            src_endianness=self.endianness,
            src_sign=Sign.UNSIGNED,
            dst_endianness=self.endianness)

        return final

    @staticmethod
    def decode(data,
               unitSize=UnitSize.SIZE_32,
               endianness=AbstractType.defaultEndianness(),
               sign=Sign.UNSIGNED):
        """Decodes the specified Timestamp data into its raw representation

        >>> from netzob.all import *
        >>> value = 1444494130
        >>> len(Timestamp.decode(value))
        4
        """

        if data is None:
            raise TypeError("Data cannot be None")

        return Integer.decode(
            data, unitSize=unitSize, endianness=endianness, sign=sign)

    @staticmethod
    def encode(data,
               unitSize=UnitSize.SIZE_32,
               endianness=AbstractType.defaultEndianness(),
               sign=Sign.UNSIGNED):
        from netzob.Model.Vocabulary.Types.Raw import Raw

        intValue = TypeConverter.convert(
            data,
            Raw,
            Integer,
            dst_unitSize=UnitSize.SIZE_32,
            dst_sign=Sign.UNSIGNED)
        parsedTimestamp = datetime.utcfromtimestamp(intValue)

        return parsedTimestamp.strftime("%c")

    @property
    def epoch(self):
        """Initial date expressed in UTC from which timestamp is measured"""
        return self.__epoch

    @epoch.setter
    @typeCheck(datetime)
    def epoch(self, epoch):
        if epoch is None:
            raise Exception("Epoch cannot be None")
        self.__epoch = epoch


class __TestTimestamp(unittest.TestCase):
    """
    Test class with test-only scenario that should not be documented.
    """

    def test_abstraction_arbitrary_values(self):
        from netzob.all import Field, Symbol
        domains = [
            Timestamp(), Timestamp(1444737333),
        ]
        symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
        data = b''.join(f.specialize() for f in symbol.fields)
        assert Symbol.abstract(data, [symbol])[1]
