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
from datetime import datetime, timedelta
from enum import Enum
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, public_api
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Sign, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer


@public_api
class Epoch(Enum):
    __repr__ = Enum.__str__
    WINDOWS = datetime(1601, 1, 1)
    MUMPS = datetime(1840, 12, 31)
    VMS = datetime(1858, 11, 17)
    EXCEL = datetime(1899, 12, 31)
    NTP = datetime(1900, 1, 1)
    MACOS_9 = datetime(1904, 1, 1)
    PICKOS = datetime(1967, 12, 31)
    UNIX = datetime(1970, 1, 1)
    FAT = datetime(1980, 1, 1)
    GPS = datetime(1980, 1, 6)
    ZIGBEE = datetime(2000, 1, 1)
    COCOA = datetime(2001, 1, 1)


@public_api
class Unity(Enum):
    __repr__ = Enum.__str__
    SECOND = 1
    DECISECOND = 10
    CENTISECOND = 100
    MILLISECOND = 1000
    MICROSECOND = 1000000
    NANOSECOND = 10000000000


@NetzobLogger
class Timestamp(AbstractType):
    r"""This class defines a Timestamp type.

    The Timestamp type defines dates in a specific format
    (such as Windows, Unix or MacOSX formats).

    The Timestamp constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains a fixed timestamp (in seconds by default).
                  If ``None``, the default generated value is the current time
                  in UTC.
    :param epoch: The initial date expressed in UTC from which
                  timestamp is measured. Default value is :attr:`Epoch.UNIX`.
    :param unity: This specifies the unity of the value (seconds,
                  milliseconds, nanoseconds). The default value is
                  :attr:`Unity.SECOND`.
    :param unitSize: The unitsize of the current value. Values must be one of
                     ``UnitSize.SIZE_*``.
                     The following unit sizes are available:

                     * UnitSize.SIZE_1
                     * UnitSize.SIZE_4
                     * UnitSize.SIZE_8
                     * UnitSize.SIZE_16
                     * UnitSize.SIZE_24
                     * UnitSize.SIZE_32 (default unit size)
                     * UnitSize.SIZE_64

    :param endianness: The endianness of the current value.
                       Values must be :attr:`Endianness.BIG` or
                       :attr:`Endianness.LITTLE`.
                       The default value is :attr:`Endianness.BIG`.
    :param sign: The sign of the current value.
                 Values must be :attr:`Sign.SIGNED` or :attr:`Sign.UNSIGNED`.
                 The default value is :attr:`Sign.UNSIGNED`.

    :type value: :class:`bitarray` or :class:`int`, optional
    :type epoch: :class:`~netzob.Model.Vocabulary.Types.Timestamp.Epoch`, optional
    :type unity: :class:`~netzob.Model.Vocabulary.Types.Timestamp.Unity`, optional
    :type unitSize: :class:`~netzob.Model.Vocabulary.Types.AbstractType.UnitSize`, optional
    :type endianness: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Endianness`, optional
    :type sign: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Sign`, optional

    .. note::
       :attr:`value` and :attr:`unitSize` attributes are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The Timestamp class provides the following public variables:

    :var typeName: The name of the implemented data type.
    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var size: The size in bits of the expected data type defined by a tuple (min, max).
               Instead of a tuple, an integer can be used to represent both min and max values.
    :var unitSize: The unitsize of the current value.
    :var epoch: The initial date expressed in UTC from which
                timestamp is measured.
    :var unity: This specifies the unity of the timestamp (seconds,
                milliseconds, nanoseconds).
    :var sign: The sign of the current value.
    :var endianness: The endianness of the current value.
    :vartype typeName: :class:`str`
    :vartype value: :class:`bitarray`
    :vartype size: ~typing.Tuple[int,int] or int
    :vartype unitSize: :class:`~netzob.Model.Vocabulary.Types.AbstractType.UnitSize`, optional
    :vartype epoch: :class:`~netzob.Model.Vocabulary.Types.Timestamp.Epoch`
    :vartype unity: :class:`~netzob.Model.Vocabulary.Types.Timestamp.Unity`
    :vartype sign: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Sign`
    :vartype endianness: :class:`~netzob.Model.Vocabulary.Types.AbstractType.Endianness`


    Available values for `epoch` parameter are:

    * Epoch.WINDOWS = datetime(1601, 1, 1)
    * Epoch.MUMPS = datetime(1840, 12, 31)
    * Epoch.VMS = datetime(1858, 11, 17)
    * Epoch.EXCEL = datetime(1899, 12, 31)
    * Epoch.NTP = datetime(1900, 1, 1)
    * Epoch.MACOS_9 = datetime(1904, 1, 1)
    * Epoch.PICKOS = datetime(1967, 12, 31)
    * Epoch.UNIX = datetime(1970, 1, 1)
    * Epoch.FAT = datetime(1980, 1, 1)
    * Epoch.GPS = datetime(1980, 1, 6)
    * Epoch.ZIGBEE = datetime(2000, 1, 1)
    * Epoch.COCOA = datetime(2001, 1, 1)

    Available values for `unity` parameter are:

    * Unity.SECOND = 1
    * Unity.DECISECOND = 10
    * Unity.CENTISECOND = 100
    * Unity.MILLISECOND = 1000
    * Unity.MICROSECOND = 1000000
    * Unity.NANOSECOND = 10000000000


    The creation of a Timestamp type with no parameter will create a bytes
    object of 4 bytes containing the current time in seconds from :attr:`Epoch.UNIX`:

    >>> from netzob.all import *
    >>> i = Timestamp()
    >>> len(i.generate().tobytes())
    4

    In the following example, a Timestamp data is created from a datetime
    and represented as 32 bits:

    >>> import time
    >>> import datetime
    >>> from netzob.all import *
    >>> date = datetime.datetime(2015, 10, 10, 17, 54, 2)
    >>> timestamp = time.mktime(date.timetuple())
    >>> time = Timestamp(timestamp)
    >>> time.size
    (0, 4294967296)
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

    @public_api
    def __init__(self,
                 value=None,
                 epoch=Epoch.UNIX,
                 unity=Unity.SECOND,
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

        size = (0, 1 << unitSize.value)

        super(Timestamp, self).__init__(
            self.__class__.__name__,
            value,
            size,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign)

    def __str__(self):
        if self.value is not None:
            return "{}({})".format(self.typeName, int.from_bytes(self.value.tobytes(), byteorder='big'))
        else:
            return "{}()".format(self.typeName)

    @public_api
    def count(self):
        r"""

        >>> from netzob.all import *
        >>> Timestamp().count()
        4294967296

        >>> Timestamp(1444494130).count()
        1

        """

        if self.value is not None:
            return 1
        else:
            return (1 << self.unitSize.value)

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
        >>> time = Timestamp(epoch=Epoch.WINDOWS, unity=Unity.NANOSECOND, unitSize=UnitSize.SIZE_64)
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
            value = value / self.unity.value

            # add the utc now with the epoch
            timestamp_datetime = self.epoch.value + timedelta(seconds=value)

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
        >>> f = Field(Timestamp(epoch=Epoch.WINDOWS, unitSize=UnitSize.SIZE_64))
        >>> len(f.specialize())
        8
        """
        if self.value is not None:
            return self.value

        # computes utc now
        now = datetime.utcnow()

        # substract the utc now with the epoch
        timestamp_datetime = now - self.epoch.value

        # convert obtained datetime to timestamp in seconds
        result_sec = timestamp_datetime.total_seconds()

        # apply the unity
        result_unity = int(result_sec * self.unity.value)

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

    @epoch.setter  # type: ignore
    def epoch(self, epoch):
        if epoch is None:
            raise Exception("Epoch cannot be None")
        self.__epoch = epoch


def _test():
    r"""

    >>> from netzob.all import *
    >>> t = Timestamp()
    >>> print(t)
    Timestamp()
    >>> t.size
    (0, 4294967296)
    >>> t.unitSize
    UnitSize.SIZE_32

    >>> t = Timestamp(1444494130)
    >>> print(t)
    Timestamp(1444494130)

    # test abstraction of arbitrary values

    >>> domains = [
    ...     Timestamp(), Timestamp(1444737333),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(f.specialize() for f in symbol.fields)
    >>> assert Symbol.abstract(data, [symbol])[1]

    """
