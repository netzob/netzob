#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import socket
from bitarray import bitarray
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Simulator.AbstractChannel import AbstractChannel, NetUtils
from netzob.Simulator.ChannelBuilder import ChannelBuilder
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Preset import Preset
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.InternetChecksum import InternetChecksum
from netzob.Model.Vocabulary.Domain.Variables.Scope import Scope



@NetzobLogger
class CustomIPChannel(AbstractChannel):
    """A CustomIPChannel is a communication channel that is used to send IP
    payloads. This **channel** is responsible for building the IP header. It is
    similar to the :class:`IPChannel <netzob.Simulator.Channels.IPChannel.IPChannel>`
    channel, except that with :class:`IPChannel` the OS kernel builds the IP header.
    Therefore, with CustomIPChannel, we **can** modify or fuzz the IP header fields.

    The CustomIPChannel constructor expects some parameters:

    :param remoteIP: This parameter is the remote IP address to connect to.
    :param localIP: The local IP address. Default value is the local
                    IP address corresponding to the network interface that
                    will be used to send the packet.
    :param upperProtocol: The protocol following IP in the stack.
                          Default value is :attr:`socket.IPPROTO_TCP` (6).
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type remoteIP: :class:`str` or :class:`netaddr.IPAddress`, required
    :type localIP: :class:`str` or :class:`netaddr.IPAddress`, optional
    :type upperProtocol: :class:`int`, optional
    :type timeout: :class:`float`, optional

    .. todo:: add support of :class:`netaddr.IPAddress`

    Adding to AbstractChannel variables, the CustomIPChannel class provides the
    following public variables:

    :var remoteIP: The remote IP address to connect to.
    :var localIP: The local IP address.
    :var upperProtocol: The protocol following the IP header.
    :vartype remoteIP: :class:`str`
    :vartype localIP: :class:`str`
    :vartype upperProtocol: :class:`int`


    The following code shows the use of a :class:`~netzob.Simulator.Channels.CustomIPChannel.CustomIPChannel`
    channel:

    >>> from netzob.all import *
    >>> client = CustomIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(next(symbol.specialize()))
    35
    >>> client.close()

    """

    ## Class attributes ##

    FAMILIES = ["ip"]

    @public_api
    @typeCheck(str, int)
    def __init__(self,
                 remoteIP,
                 localIP=None,
                 upperProtocol=socket.IPPROTO_TCP,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(CustomIPChannel, self).__init__(timeout=timeout)
        self.remoteIP = remoteIP
        if localIP is None:
            localIP = NetUtils.getLocalIP(remoteIP)
        self.localIP = localIP
        self.upperProtocol = upperProtocol

        # Header initialization
        self.initHeader()

    @staticmethod
    def getBuilder():
        return CustomIPChannelBuilder

    @public_api
    def open(self, timeout=AbstractChannel.DEFAULT_TIMEOUT):
        """Open the communication channel.
        :param timeout: The default timeout of the channel for opening
                        connection and waiting for a message. Default value
                        is blocking (None).
        :type timeout: :class:`float`, optional
        :raise: RuntimeError if the channel is already opened
        """

        super().open(timeout=timeout)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.upperProtocol)
        self._socket.settimeout(timeout or self.timeout)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self._socket.bind((self.localIP, self.upperProtocol))
        self.isOpen = True

    @public_api
    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    @public_api
    def read(self):
        """Read the next message on the communication channel, and return the
        IP payload.

        """
        ip_packet = self._inner_read()
        ip_header_len = (ip_packet[0] & 15) * 4
        return ip_packet[ip_header_len:]

    def _inner_read(self):
        """Read the next message on the communication channel, and return the
        IP packet.

        """
        if self._socket is not None:
            (data, _) = self._socket.recvfrom(65535)
            return data
        else:
            raise Exception("socket is not available")

    def writePacket(self, data):
        """Write on the communication channel the specified data.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """

        self.header_preset['ip.payload'] = data
        packet = next(self.header.specialize(self.header_preset))

        try:
            len_data = self._socket.sendto(packet, (self.remoteIP, 0))
        except OSError as e:
            self._logger.warning("OSError durring socket.sendto(): '{}'. Trying a second time after sleeping 1s...".format(e))
            time.sleep(1)
            len_data = self._socket.sendto(packet, (self.remoteIP, 0))
        return len_data

    @public_api
    @typeCheck(bytes)
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self._socket is not None:
            # get the ports from message to identify the good response (in TCP or UDP)
            portSrcTx = (data[0] * 256) + data[1]
            portDstTx = (data[2] * 256) + data[3]

            responseOk = False
            stopWaitingResponse = False
            self.write(data)
            while stopWaitingResponse is False:
                dataReceived = self._inner_read()

                # IHL = (Bitwise AND 00001111) x 4bytes
                ipHeaderLen = (dataReceived[0] & 15) * 4
                portSrcRx = (dataReceived[ipHeaderLen] * 256) + \
                    dataReceived[ipHeaderLen + 1]
                portDstRx = (dataReceived[ipHeaderLen + 2] * 256) + \
                    dataReceived[ipHeaderLen + 3]

                stopWaitingResponse = (portSrcTx == portDstRx) and (portDstTx == portSrcRx)
                if stopWaitingResponse:  # and not timeout
                    responseOk = True
            if responseOk:
                return dataReceived[ipHeaderLen:]
        else:
            raise Exception("socket is not available")

    def initHeader(self):
        """Initialize the IP header according to the IP format definition.
        """

        ip_ver = Field(
            name='ip.version', domain=BitArray(
                value=bitarray('0100')))  # IP Version 4
        ip_ihl = Field(name='ip.hdr_len', domain=BitArray('0000'))
        ip_tos = Field(
            name='ip.tos',
            domain=Data(
                dataType=BitArray(nbBits=8, default=bitarray('00000000')),
                scope=Scope.SESSION))
        ip_tot_len = Field(
            name='ip.len', domain=BitArray('0000000000000000'))
        ip_id = Field(name='ip.id', domain=BitArray(nbBits=16))
        ip_flags = Field(name='ip.flags', domain=Data(dataType=BitArray(nbBits=3, default=bitarray('000')), scope=Scope.SESSION))
        ip_frag_off = Field(name='ip.fragment', domain=Data(dataType=BitArray(nbBits=13, default=bitarray('0000000000000')), scope=Scope.SESSION))
        ip_ttl = Field(name='ip.ttl', domain=Data(dataType=BitArray(nbBits=8, default=bitarray('01000000')), scope=Scope.SESSION))
        ip_proto = Field(name='ip.proto', domain=Integer(value=self.upperProtocol, unitSize=UnitSize.SIZE_8, endianness=Endianness.BIG, sign=Sign.UNSIGNED))
        ip_checksum = Field(name='ip.checksum', domain=BitArray('0000000000000000'))
        ip_saddr = Field(name='ip.src', domain=IPv4(self.localIP))
        ip_daddr = Field(
            name='ip.dst', domain=IPv4(self.remoteIP))
        ip_payload = Field(name='ip.payload', domain=Raw())

        ip_ihl.domain = Size([ip_ver,
                              ip_ihl,
                              ip_tos,
                              ip_tot_len,
                              ip_id, ip_flags,
                              ip_frag_off,
                              ip_ttl, ip_proto,
                              ip_checksum,
                              ip_saddr,
                              ip_daddr], dataType=BitArray(nbBits=4), factor=1/float(32))
        ip_tot_len.domain = Size([ip_ver,
                                  ip_ihl,
                                  ip_tos,
                                  ip_tot_len,
                                  ip_id,
                                  ip_flags,
                                  ip_frag_off,
                                  ip_ttl,
                                  ip_proto,
                                  ip_checksum,
                                  ip_saddr,
                                  ip_daddr,
                                  ip_payload], dataType=Raw(nbBytes=2, unitSize=UnitSize.SIZE_16), factor=1/float(8))
        ip_checksum.domain = InternetChecksum(targets=[ip_ver,
                                              ip_ihl,
                                              ip_tos,
                                              ip_tot_len,
                                              ip_id,
                                              ip_flags,
                                              ip_frag_off,
                                              ip_ttl,
                                              ip_proto,
                                              ip_checksum,
                                              ip_saddr,
                                              ip_daddr], dataType=Raw(nbBytes=2, unitSize=UnitSize.SIZE_16))

        self.header = Symbol(name='IP layer', fields=[ip_ver,
                                                      ip_ihl,
                                                      ip_tos,
                                                      ip_tot_len,
                                                      ip_id,
                                                      ip_flags,
                                                      ip_frag_off,
                                                      ip_ttl,
                                                      ip_proto,
                                                      ip_checksum,
                                                      ip_saddr,
                                                      ip_daddr,
                                                      ip_payload])
        self.header_preset = Preset(self.header)

    # Properties

    @property
    def remoteIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__remoteIP

    @remoteIP.setter  # type: ignore
    @typeCheck(str)
    def remoteIP(self, remoteIP):
        if remoteIP is None:
            raise TypeError("Listening IP cannot be None")

        self.__remoteIP = remoteIP

    @property
    def localIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__localIP

    @localIP.setter  # type: ignore
    @typeCheck(str)
    def localIP(self, localIP):
        self.__localIP = localIP

    @property
    def upperProtocol(self):
        """Upper protocol, such as TCP, UDP, ICMP, etc.

        :type: :class:`str`
        """
        return self.__upperProtocol

    @upperProtocol.setter  # type: ignore
    @typeCheck(int)
    def upperProtocol(self, upperProtocol):
        if upperProtocol is None:
            raise TypeError("Upper protocol cannot be None")

        self.__upperProtocol = upperProtocol

    @public_api
    def set_rate(self, rate):
        """This method set the the given transmission rate to the channel.
        Used in testing network under high load

        :parameter rate: This specifies the bandwidth in bytes per second to
                         respect during traffic emission. Default value is
                         ``None``, which means that the bandwidth is only
                         limited by the underlying physical layer.
        :type rate: :class:`int`, required
        """
        localInterface = NetUtils.getLocalInterface(self.localIP)
        NetUtils.set_rate(localInterface, rate)
        if rate is not None:
            self._logger.info("Network rate limited to {:.2f} kBps ({} kbps) on {} interface".format(rate/1000, rate*8/1000, localInterface))
        self._rate = rate
        self._logger.info("tc status on {} interface: {}".format(localInterface, NetUtils.get_rate(localInterface)))

    @public_api
    def unset_rate(self):
        """This method clears the transmission rate.
        """
        localInterface = NetUtils.getLocalInterface(self.localIP)
        if self._rate is not None:
            NetUtils.set_rate(localInterface, None)
            self._rate = None
            self._logger.info("Network rate limitation removed on {} interface".format(localInterface))
        self._logger.info("tc status on {} interface: {}".format(localInterface, NetUtils.get_rate(localInterface)))


class CustomIPChannelBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channels.CustomIPChannel.CustomIPChannel` instance

    >>> import socket
    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(dst_addr="1.2.3.4",
    ...                   src_addr="4.3.2.1",
    ...                   protocol=socket.IPPROTO_TCP)
    >>> builder = CustomIPChannelBuilder().set_map(netinfo.getDict())
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.CustomIPChannel.CustomIPChannel'>
    >>> chan.localIP  # src_addr key has been mapped to localIP attribute
    '4.3.2.1'
    """

    @public_api
    def __init__(self):
        super().__init__(CustomIPChannel)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_dst_addr(self, value):
        self.attrs['remoteIP'] = value

    def set_protocol(self, value):
        self.attrs['upperProtocol'] = value


def _test_write_read_with_same_channel():
    r"""

    >>> from netzob.all import *
    >>> client = CustomIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(next(symbol.specialize()))
    35
    >>> client.read()
    b'Hello everyone!'
    >>> client.close()

    """


def _test_write_read_with_different_channels():
    r"""

    >>> from netzob.all import *
    >>> client = CustomIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> server = CustomIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> server.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(next(symbol.specialize()))
    35
    >>> server.read()
    b'Hello everyone!'
    >>> client.close()
    >>> server.close()

    """


def _test_read_before_send():
    r"""

    >>> from netzob.all import *
    >>> client = CustomIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(b"some data")
    29
    >>> client.read()
    b'some data'
    >>> client.write(next(symbol.specialize()))
    35
    >>> client.close()

    """
