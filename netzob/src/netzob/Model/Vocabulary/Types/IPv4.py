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
import struct
import random
import unittest

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netaddr import IPAddress, IPNetwork
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, public_api
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize


@NetzobLogger
class IPv4(AbstractType):
    r"""This class defines an IPv4 type.

    The IPv4 type encodes a :class:`bytes` object in an IPv4
    representation, and conversely decodes an IPv4 into a raw
    object.

    The IPv4 constructor expects some parameters:

    :param value: This parameter is used to describe a domain that contains an IP value expressed in standard dot notation
                  (ex: "192.168.0.10"). The default value is None.
    :param network: This parameter is used to describe a domain that contains a network address expressed in standard
                    dot notation (ex: "192.168.0.0/24"). The default value is None.
    :param endianness: The endianness of the current value. Values must be Endianness.BIG or Endianness.LITTLE. The default value is Endianness.BIG.
    :param default: This parameter is the default value used in specialization.
    :type value: :class:`str` or :class:`netaddr.IPAddress`, optional
    :type network: :class:`str` or :class:`netaddr.IPNetwork`, optional
    :type endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`, optional
    :type default: :class:`str` or :class:`netaddr.IPAddress`, optional

    .. note::
       :attr:`value` and :attr:`network` parameters are mutually
       exclusive. Setting both values raises an :class:`Exception`.

       :attr:`value` and :attr:`default` parameters are mutually exclusive.
       Setting both values raises an :class:`Exception`.


    The IPv4 class provides the following public variables:

    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var network: A constraint over the network. The parsed data belongs to this network or not.
    :var endianness: The endianness of the value. Values must be Endianness.BIG or Endianness.LITTLE.
    :var default: The default value used in specialization.
    :vartype value: :class:`bitarray`
    :vartype network: :class:`str` or :class:`netaddr.IPNetwork`
    :vartype endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`
    :vartype default: :class:`bitarray`


    The creation of an IPv4 type with no parameter will create a random bytes
    object of 4 bytes:

    >>> from netzob.all import *
    >>> i = IPv4()
    >>> i.generate().tobytes()
    b'\x93\tn|'

    The following examples show the use of an IPv4 type:

    >>> from netzob.all import *
    >>> ip = IPv4("192.168.0.10")
    >>> ip.value
    bitarray('11000000101010000000000000001010')

    It is also possible to specify an IPv4 type that accepts a range
    of IP addresses, through the :attr:`network` parameter, as shown in the
    following example:

    >>> from netzob.all import *
    >>> ip = IPv4(network="10.10.10.0/27")
    >>> IPv4(ip.generate())  # initialize with the generated bitarray value
    10.10.10.0


    This next example shows the usage of a default value:

    >>> from netzob.all import *
    >>> t = IPv4(default='127.0.0.1')
    >>> t.generate().tobytes()
    b'\x7f\x00\x00\x01'

    """

    @public_api
    def __init__(self,
                 value=None,
                 network=None,
                 unitSize=UnitSize.SIZE_32,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign(),
                 default=None):

        # Manage mutualy exclusive parameters
        if value is not None and network is not None:
            raise ValueError("An IPv4 should have either its value or its network set, but not both")

        if value is not None and default is not None:
            raise ValueError("An IPv4 should have either its constant value or its default value set, but not both")

        # Manage value parameter
        if value is not None and isinstance(value, IPAddress):
            value = str(value)

        if value is not None and not (isinstance(value, str) or isinstance(value, bitarray)):
            raise ValueError("An IPv4 value parameter should either be a str, a netaddr.IPAddress or a bitarray, but not a '{}'".format(type(value)))

        # Manage default parameter
        if default is not None and isinstance(default, IPAddress):
            default = str(default)

        if default is not None and not (isinstance(default, str) or isinstance(default, bitarray)):
            raise ValueError("An IPv4 default parameter should either be a str, a netaddr.IPAddress or a bitarray, but not a '{}'".format(type(default)))

        # Manage conversions
        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            value = TypeConverter.convert(
                value,
                IPv4,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        if default is not None and not isinstance(default, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            default = TypeConverter.convert(
                default,
                IPv4,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        self.network = network

        size = (0, 1 << unitSize.value)

        super(IPv4, self).__init__(
            self.__class__.__name__,
            value,
            size,
            unitSize=unitSize,
            endianness=endianness,
            sign=sign,
            default=default)

    def __str__(self):
        if self.value is not None:
            return "{}(\"{}\")".format(self.typeName, IPv4.encode(self.value.tobytes()))
        elif self.network is not None:
            return "{}(\"{}\")".format(self.typeName, self.network)
        else:
            return "{}()".format(self.typeName)

    @public_api
    def count(self):
        r"""

        >>> from netzob.all import *
        >>> IPv4("127.0.0.1").count()
        1

        >>> IPv4().count()
        4294967296

        >>> IPv4(network='192.168.0.0/24').count()
        256

        >>> IPv4(network='192.168.0.0/23').count()
        512

        """

        if self.value is not None:
            return 1
        if self.network is not None:
            return self.network.size
        else:
            return (1 << self.unitSize.value)

    def getMinStorageValue(self):
            return 0

    def getMaxStorageValue(self):
            return 2**self.unitSize.value - 1

    def generate(self, generationStrategy=None):
        r"""Generates a random IPv4 which follows the constraints.

        >>> from netzob.all import *
        >>> f = Field(IPv4())
        >>> len(next(f.specialize()))
        4

        >>> f = Field(IPv4("192.168.0.20"))
        >>> next(f.specialize())
        b'\xc0\xa8\x00\x14'

        >>> f = Field(IPv4(network="10.10.10.0/24"))
        >>> len(next(f.specialize()))
        4

        """
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.Raw import Raw

        if self.value is not None:
            return self.value
        elif self.default is not None:
            return self.default
        elif self.network is not None:
            ip = random.choice(self.network)
            return TypeConverter.convert(
                ip.packed,
                Raw,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)
        else:
            not_valid = [10, 127, 169, 172, 192]

            first = random.randrange(1, 256)
            while first in not_valid:
                first = random.randrange(1, 256)

            strip = ".".join([
                str(first), str(random.randrange(1, 256)),
                str(random.randrange(1, 256)), str(random.randrange(1, 256))
            ])

            ip = IPv4.encode(strip, unitSize=self.unitSize, endianness=self.endianness, sign=self.sign)
            return TypeConverter.convert(
                ip.packed,
                Raw,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        r"""Computes if specified data can be parsed as an IPv4 with the predefined constraints.

        >>> from netzob.all import *
        >>> ip = IPv4()
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("198.128.0.100")
        True
        >>> ip.canParse("256.0.0.1")
        False
        >>> ip.canParse("127.0.0.1")
        True
        >>> ip.canParse("127.0.0.-1")
        False
        >>> ip.canParse("::")
        False
        >>> ip.canParse("0.0.0.0")
        True
        >>> ip.canParse(b"\1\2\3\4")
        True


        And with some constraints over the expected IPv4:


        >>> ip = IPv4("192.168.0.10")
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("192.168.1.10")
        False
        >>> ip.canParse(3232235530)
        False
        >>> ip = IPv4("167.20.14.20")
        >>> ip.canParse(3232235530)
        False
        >>> ip.canParse("167.20.14.20")
        True


        or with contraints over the expected network the ipv4 belongs to:


        >>> ip = IPv4(network="192.168.0.0/24")
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("192.168.1.10")
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")
        if isinstance(data, bitarray):
            data = data.tobytes()

        try:
            ip = IPv4.encode(
                data, unitSize=self.unitSize, endianness=self.endianness, sign=self.sign)
            if ip is None or ip.version != 4:
                return False
        except:
            return False
        try:
            if self.value is not None:
                from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
                from netzob.Model.Vocabulary.Types.BitArray import BitArray

                res = TypeConverter.convert(
                    data,
                    IPv4,
                    BitArray,
                    src_unitSize=self.unitSize,
                    src_endianness=self.endianness,
                    src_sign=self.sign,
                    dst_unitSize=self.unitSize,
                    dst_endianness=self.endianness,
                    dst_sign=self.sign)

                return self.value == res
            elif self.network is not None:
                return ip in self.network
        except:
            return False

        return True

    def _isValidIPv4Network(self, network):
        """Computes if the specified network is a valid IPv4 network.

        >>> from netzob.all import *
        >>> ip = IPv4()
        >>> ip._isValidIPv4Network("192.168.0.10")
        True
        >>> ip._isValidIPv4Network("-1.168.0.10")
        False

        """
        if network is None:
            raise TypeError("None is not valid IPv4 network")
        try:
            net = IPNetwork(network)
            if net is not None and net.version == 4:
                return True
        except:
            return False
        return False

    @property
    def network(self):
        """A constraint over the network the parsed data belongs to this network or not."""
        return self.__network

    @network.setter  # type: ignore
    def network(self, network):
        if network is not None:
            if not self._isValidIPv4Network(network):
                raise TypeError(
                    "Specified network constraints is not valid IPv4 Network.")
            self.__network = IPNetwork(network)
        else:
            self.__network = None

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        r"""Decode the specified IPv4 data into its raw representation.

        >>> from netzob.all import *
        >>> IPv4.decode("127.0.0.1")
        b'\x7f\x00\x00\x01'

        """

        if data is None:
            raise TypeError("Data cannot be None")
        elif isinstance(data, bytes):
            return data
        else:
            try:
                ip = IPAddress(data)
            except Exception as e:
                raise TypeError("Data is not a valid IPv4, cannot decode it. Error: '{}'".format(e))
            return ip.packed

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """Encodes the specified data into an IPAddress object

        :param data: the data to encode into an IPAddress
        :type data: str or raw bytes (BBBB)
        :return: the encoded IPAddress
        """
        if isinstance(data, str):
            try:
                ip = IPAddress(data)
                if ip is not None and ip.version == 4:
                    return ip
            except:
                pass
        elif isinstance(data, bytes):
            try:
                structFormat = "<"
                if endianness == Endianness.BIG:
                    structFormat = ">"

                if not sign == Sign.SIGNED:
                    structFormat += "bbbb"
                else:
                    structFormat += "BBBB"

                quads = list(map(str, struct.unpack(structFormat, data)))
                strIP = '.'.join(quads)

                ip = IPAddress(strIP)

                if ip is not None and ip.version == 4:
                    return ip
            except Exception as e:
                raise TypeError("Impossible to encode {0} into an IPv4 data ({1})".
                                format(data, e))
        else:
            raise TypeError("Wrong data type for encode(). Expected str or bytes, got '{}'".format(type(data)))

    def getFixedBitSize(self):
        self._logger.debug("Determine the deterministic size of the value of "
                           "the type")
        return self.unitSize.value


def _test():
    r"""

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> import netaddr

    >>> t = IPv4()
    >>> print(t)
    IPv4()
    >>> t.size
    (0, 4294967296)
    >>> t.unitSize
    UnitSize.SIZE_32


    # Test value parameter

    >>> t = IPv4("192.168.1.1")
    >>> print(t)
    IPv4("192.168.1.1")

    >>> t = IPv4(192)
    Traceback (most recent call last):
    ...
    ValueError: An IPv4 value parameter should either be a str, a netaddr.IPAddress or a bitarray, but not a '<class 'int'>'

    >>> t = IPv4(netaddr.IPAddress("127.0.0.1"))
    >>> print(t)
    IPv4("127.0.0.1")

    
    # Test default parameter

    >>> t = IPv4(default="192.168.10.1")
    >>> print(t)
    IPv4()

    >>> t = IPv4(default=netaddr.IPAddress("127.0.0.2"))
    >>> print(t)
    IPv4()
    >>> data = t.generate().tobytes()
    >>> data
    b'\x7f\x00\x00\x02'
    >>> t.canParse(data)
    True

    >>> t = IPv4(default=192)
    Traceback (most recent call last):
    ...
    ValueError: An IPv4 default parameter should either be a str, a netaddr.IPAddress or a bitarray, but not a '<class 'int'>'


    # Test network parameter

    >>> t = IPv4(network="192.168.0.0/24")
    >>> print(t)
    IPv4("192.168.0.0/24")

    >>> t = IPv4(network=192)
    Traceback (most recent call last):
    ...
    TypeError: Specified network constraints is not valid IPv4 Network.

    >>> t = IPv4(network=netaddr.IPNetwork("192.168.0.0/24"))
    >>> print(t)
    IPv4("192.168.0.0/24")
    >>> data = t.generate().tobytes()
    >>> data
    b'\xc0\xa8\x00\x10'


    # test abstraction arbitrary values

    >>> domains = [
    ...    IPv4("1.2.3.4"), IPv4(),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(next(f.specialize()) for f in symbol.fields)
    >>> assert symbol.abstract(data)


    # Verify that you cannot create an IPv4 with a value AND a network:

    >>> i = IPv4('10.0.0.1', network="10.10.10.0/24")
    Traceback (most recent call last):
    ...
    ValueError: An IPv4 should have either its value or its network set, but not both

    """


def _test_specialize_abstract():
    r"""
    >>> from netzob.all import *
    >>> from collections import OrderedDict
    >>> import netaddr
    >>> Conf.apply()
    >>> from netzob.Model.Vocabulary.Types.AbstractType import test_type_one_parameter, test_type_multiple_parameters, test_type_specialize_abstract

    >>> data_type = IPv4

    >>> possible_parameters = OrderedDict()
    >>> possible_parameters["value"] = [None, "127.0.0.1", netaddr.IPAddress("127.0.0.2")]
    >>> possible_parameters["network"] = [None, "127.0.0.1/16"]
    >>> possible_parameters["endianness"] = [None, Endianness.LITTLE, Endianness.BIG]
    >>> possible_parameters["default"] = [None, "127.0.0.1"]

    >>> test_type_one_parameter(data_type, possible_parameters)

    >>> (parameter_names, functional_combinations_possible_parameters) = test_type_multiple_parameters(data_type, possible_parameters)

    >>> test_type_specialize_abstract(data_type, parameter_names, functional_combinations_possible_parameters)

    """
