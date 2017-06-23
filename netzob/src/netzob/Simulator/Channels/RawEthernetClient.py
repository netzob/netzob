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
from netzob.Simulator.Channels.AbstractChannel import AbstractChannel
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksum import Checksum
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


@NetzobLogger
class RawEthernetClient(AbstractChannel):
    """A RawEthernetClient is a communication channel allowing sending
    Ethernet frames. This channel is responsible for building the
    Ethernet layer.

    The RawEthernetClient constructor expects some parameters:

    :param remoteMac: The remote MAC address to connect to.
    :param localMac: The local MAC address.
    :param upperProtocol: The protocol following IP in the stack.
                          Default value is socket.IPPROTO_TCP.
    :param interface: The network interface to use. It is linked with
                      the local MAC address to use (`localMac` parameter).
                      Default value is 'eth0'.
    :param timeout: The default timeout of the channel for opening
                    connection and waiting for a message. Default value
                    is 5.0 seconds. To specify no timeout, None value is expected.
    :type remoteMac: :class:`str`, required
    :type localMac: :class:`str`, optional
    :type upperProtocol: :class:`int`, optional
    :type interface: :class:`str`, optional
    :type timeout: :class:`float`, optional


    The following code shows the use of a RawEthernetClient channel:

    >>> from netzob.all import *
    >>> client = RawEthernetClient(remoteIP='127.0.0.1')
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(symbol.specialize())
    >>> client.close()

    """

    ETH_P_ALL = 3

    @typeCheck(str, int)
    def __init__(self,
                 remoteMac,
                 localMac=None,
                 upperProtocol=socket.IPPROTO_TCP,
                 interface="eth0",
                 timeout=5.):
        super(RawEthernetClient, self).__init__(isServer=False)
        self.remoteMac = remoteMac
        self.localMac = localMac
        self.upperProtocol = upperProtocol
        self.interface = interface
        self.timeout = timeout
        self.__socket = None
        self.type = AbstractChannel.TYPE_RAWETHERNETCLIENT

    def open(self):
        """Open the communication channel. If the channel is a client, it
        starts to connect to the specified server.
        """

        if self.isOpen:
            raise RuntimeError(
                "The channel is already open, cannot open it again")

        self.__socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(RawEthernetClient.ETH_P_ALL))
        self.__socket.bind((self.interface, RawEthernetClient.ETH_P_ALL))
        self.isOpen = True

    def close(self):
        """Close the communication channel."""
        if self.__socket is not None:
            self.__socket.close()
        self.isOpen = False

    def read(self):
        """Read the next message on the communication channel.
        """
        if self.__socket is not None:
            (data, _) = self.__socket.recvfrom(65535)

            # Remove Ethernet header from received data
            ethHeaderLen = 14  # (Bitwise AND 00001111) x 4bytes --> see RFC-791
            if len(data) > ethHeaderLen:
                data = data[ethHeaderLen:]

            # Remove IP header from received data
            ipHeaderLen = (data[0] & 15) * 4  # (Bitwise AND 00001111) x 4bytes --> see RFC-791
            if len(data) > ipHeaderLen:
                data = data[ipHeaderLen:]
            return data
        else:
            raise Exception("socket is not available")

    def writePacket(self, data):
        """Write on the communication channel the specified data

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """

        if self.header is None:
            raise Exception("IP header structure is None")

        if self.__socket is None:
            raise Exception("socket is not available")

        self.header_presets['ip.payload'] = data
        packet = self.header.specialize(presets=self.header_presets)
        len_data = self.__socket.sendto(packet, (self.interface, RawEthernetClient.ETH_P_ALL))
        return len_data

    @typeCheck(bytes)
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self.__socket is not None:
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

    def initIPHeader(self, localIP, remoteIP):
        """Initialize the IP header according to the IP format definition.

        :param localIP: the local IP address
        :param remoteIP: the remote IP address
        :type localIP: :class:`str`
        :type remoteIP: :class:`str`
        """

        # Ethernet header

        eth_dst = Field(name='eth.dst', domain=Raw(self.remoteMac))
        eth_src = Field(name='eth.src', domain=Raw(self.localMac))
        eth_type = Field(name='eth.type', domain=Raw(b"\x08\x00"))

        # IP header

        self.localIP = localIP
        self.remoteIP = remoteIP

        ip_ver = Field(
            name='ip.version', domain=BitArray(
                value=bitarray('0100')))  # IP Version 4
        ip_ihl = Field(name='ip.hdr_len', domain=BitArray(bitarray('0000')))
        ip_tos = Field(
            name='ip.tos',
            domain=Data(
                dataType=BitArray(nbBits=8),
                originalValue=bitarray('00000000'),
                svas=SVAS.PERSISTENT))
        ip_tot_len = Field(
            name='ip.len', domain=BitArray(bitarray('0000000000000000')))
        ip_id = Field(name='ip.id', domain=BitArray(nbBits=16))
        ip_flags = Field(name='ip.flags', domain=Data(dataType=BitArray(nbBits=3), originalValue=bitarray('000'), svas=SVAS.PERSISTENT))
        ip_frag_off = Field(name='ip.fragment', domain=Data(dataType=BitArray(nbBits=13), originalValue=bitarray('0000000000000'), svas=SVAS.PERSISTENT))
        ip_ttl = Field(name='ip.ttl', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('01000000'), svas=SVAS.PERSISTENT))
        ip_proto = Field(name='ip.proto', domain=Integer(value=self.upperProtocol, unitSize=UnitSize.SIZE_8, endianness=Endianness.BIG, sign=Sign.UNSIGNED))
        ip_checksum = Field(name='ip.checksum', domain=BitArray(bitarray('0000000000000000')))
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
                                  ip_payload], dataType=Integer(unitSize=UnitSize.SIZE_16, sign=Sign.UNSIGNED), factor=1/float(8))
        ip_checksum.domain = Checksum(fields=[ip_ver,
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
                                              ip_daddr], checksumName='InternetChecksum', dataType=Raw(nbBytes=2, unitSize=UnitSize.SIZE_16))

        self.header = Symbol(name='Ethernet layer', fields=[eth_dst,
                                                            eth_src,
                                                            eth_type,
                                                            ip_ver,
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

    @remoteIP.setter
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

    @localIP.setter
    @typeCheck(str)
    def localIP(self, localIP):
        self.__localIP = localIP

    @property
    def upperProtocol(self):
        """Upper protocol, such as TCP, UDP, ICMP, etc.

        :type: :class:`str`
        """
        return self.__upperProtocol

    @upperProtocol.setter
    @typeCheck(int)
    def upperProtocol(self, upperProtocol):
        if upperProtocol is None:
            raise TypeError("Upper protocol cannot be None")

        self.__upperProtocol = upperProtocol

    @property
    def interface(self):
        """Interface such as eth0, lo.

        :type: :class:`str`
        """
        return self.__interface

    @interface.setter
    @typeCheck(str)
    def interface(self, interface):
        if interface is None:
            raise TypeError("Interface cannot be None")

        self.__interface = interface

    @property
    def timeout(self):
        """The default timeout of the channel for opening connection and
        waiting for a message. Default value is 5.0 seconds. To
        specify no timeout, None value is expected.

        :rtype: :class:`float` or None
        """
        return self.__timeout

    @timeout.setter
    @typeCheck(float)
    def timeout(self, timeout):
        """
        :type timeout: :class:`float`, optional
        """
        self.__timeout = timeout
