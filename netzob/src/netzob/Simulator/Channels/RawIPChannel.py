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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Simulator.AbstractChannel import AbstractChannel, NetUtils
from netzob.Simulator.ChannelBuilder import ChannelBuilder
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.InternetChecksum import InternetChecksum
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS



@NetzobLogger
class RawIPChannel(AbstractChannel):
    """A RawIPChannel is a communication channel to send IP
    payloads. This **channel** is responsible for building the IP header. It is
    similar to the :class:`IPChannel <netzob.Simulator.Channels.IPChannel.IPChannel>`
    channel, except that with :class:`IPChannel` the OS kernel builds the IP header.
    Therefore, with RawIPChannel, we **can** modify or fuzz the IP header fields.

    The RawIPChannel constructor expects some parameters:

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

    Adding to AbstractChannel variables, the RawIPChannel class provides the
    following public variables:

    :var remoteIP: The remote IP address to connect to.
    :var localIP: The local IP address.
    :var upperProtocol: The protocol following the IP header.
    :vartype remoteIP: :class:`str`
    :vartype localIP: :class:`str`
    :vartype upperProtocol: :class:`int`


    The following code shows the use of a :class:`~netzob.Simulator.Channels.RawIPChannel.RawIPChannel`
    channel:

    >>> from netzob.all import *
    >>> client = RawIPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(symbol.specialize())
    >>> client.close()

    """

    ## Class attributes ##

    FAMILIES = ["ip"]

    @typeCheck(str, int)
    def __init__(self,
                 remoteIP,
                 localIP=None,
                 upperProtocol=socket.IPPROTO_TCP,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(RawIPChannel, self).__init__(timeout=timeout)
        self.remoteIP = remoteIP
        if localIP is None:
            localIP = NetUtils.getLocalIP(remoteIP)
        self.localIP = localIP
        self.upperProtocol = upperProtocol

        # Header initialization
        self.initHeader()

    @staticmethod
    def getBuilder():
        return RawIPChannelBuilder

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

    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    def read(self):
        """Read the next message on the communication channel.
        """
        if self._socket is not None:
            (data, _) = self._socket.recvfrom(65535)

            # Remove IP header from received data
            ipHeaderLen = (data[0] & 15) * 4  # (Bitwise AND 00001111) x 4bytes --> see RFC-791
            if len(data) > ipHeaderLen:
                data = data[ipHeaderLen:]
            return data
        else:
            raise Exception("socket is not available")

    def writePacket(self, data):
        """Write on the communication channel the specified data.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """

        self.header_presets['ip.payload'] = data
        packet = self.header.specialize(presets=self.header_presets)
        len_data = self._socket.sendto(packet, (self.remoteIP, 0))
        return len_data

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
                dataReceived = self.read()
                portSrcRx = (dataReceived[0] * 256) + dataReceived[1]
                portDstRx = (dataReceived[2] * 256) + dataReceived[3]
                stopWaitingResponse = (portSrcTx == portDstRx) and (portDstTx == portSrcRx)
                if stopWaitingResponse:  # and not timeout
                    responseOk = True
            if responseOk:
                return dataReceived
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
                dataType=BitArray(nbBits=8),
                originalValue=bitarray('00000000'),
                svas=SVAS.PERSISTENT))
        ip_tot_len = Field(
            name='ip.len', domain=BitArray('0000000000000000'))
        ip_id = Field(name='ip.id', domain=BitArray(nbBits=16))
        ip_flags = Field(name='ip.flags', domain=Data(dataType=BitArray(nbBits=3), originalValue=bitarray('000'), svas=SVAS.PERSISTENT))
        ip_frag_off = Field(name='ip.fragment', domain=Data(dataType=BitArray(nbBits=13), originalValue=bitarray('0000000000000'), svas=SVAS.PERSISTENT))
        ip_ttl = Field(name='ip.ttl', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('01000000'), svas=SVAS.PERSISTENT))
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

    # Management methods

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


class RawIPChannelBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channel.RawIPChannel.RawIPChannel` instance

    >>> import socket
    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(dst_addr="1.2.3.4",
    ...                   src_addr="4.3.2.1",
    ...                   protocol=socket.IPPROTO_TCP)
    >>> chan = RawIPChannelBuilder().set_map(netinfo.getDict()).build()
    >>> assert isinstance(chan, RawIPChannel)
    """

    def __init__(self):
        super().__init__(RawIPChannel)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_dst_addr(self, value):
        self.attrs['remoteIP'] = value

    def set_protocol(self, value):
        self.attrs['upperProtocol'] = value
