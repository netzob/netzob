#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Model.Types.IPv4 import IPv4
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Integer import Integer
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.Variables.Leafs.InternetChecksum import InternetChecksum
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


@NetzobLogger
class RawIPClient(AbstractChannel):
    """A RawIPClient is a communication channel allowing to send IP
    payloads. This channel is responsible for building the IP layer.

    Interesting link: http://www.offensivepython.com/2014/09/packet-injection-capturing-response.html

    >>> from netzob.all import *
    >>> client = RawIPClient(remoteIP='127.0.0.1')
    >>> client.open()
    >>> symbol = Symbol([Field("Hello Zoby !")])
    >>> client.write(symbol.specialize())
    >>> client.close()

    """

    ETH_P_IP = 0x0800

    @typeCheck(str, int)
    def __init__(self, remoteIP, localIP=None, upperProtocol=socket.IPPROTO_TCP, interface="eth0", timeout=5):
        super(RawIPClient, self).__init__(isServer=False)
        self.remoteIP = remoteIP
        self.localIP = localIP
        self.upperProtocol = upperProtocol
        self.interface = interface
        self.timeout = timeout
        self.__isOpen = False
        self.__socket = None

    def open(self, timeout=None):
        """Open the communication channel. If the channel is a client, it starts to connect
        to the specified server.
        """

        if self.isOpen:
            raise RuntimeError("The channel is already open, cannot open it again")

        self.__socket = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM, socket.htons(RawIPClient.ETH_P_IP))
        self.__socket.bind((self.interface, RawIPClient.ETH_P_IP))

    def close(self):
        """Close the communication channel."""
        if self.__socket is not None:
            self.__socket.close()

    def read(self, timeout=None):
        """Read the next message on the communication channel.

        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """
        # TODO: handle timeout
        if self.__socket is not None:
            (data, remoteAddr) = self.__socket.recvfrom(65535)
            return data
        else:
            raise Exception("socket is not available")

    @typeCheck(bytes)
    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        if self.__socket is not None:
            packet = self.buildPacket(data)
            self.__socket.sendto(packet, (self.interface, RawIPClient.ETH_P_IP))
        else:
            raise Exception("socket is not available")

    def buildPacket(self, payload):
        """Build a raw IP packet including the IP layer and its payload.

        :parameter payload: the payload to write on the channel
        :type payload: binary object
        """

        ip_ver = Field(name='Version', domain=BitArray(value=bitarray('0100')))  # IP Version 4
        ip_ihl = Field(name='Header length', domain=BitArray(bitarray('0000')))
        ip_tos = Field(name='TOS', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('00000000'), svas=SVAS.PERSISTENT))
        ip_tot_len = Field(name='Total length', domain=BitArray(bitarray('0000000000000000')))
        ip_id = Field(name='Identification number', domain=BitArray(nbBits=16))
        ip_flags = Field(name='Flags', domain=Data(dataType=BitArray(nbBits=3), originalValue=bitarray('000'), svas=SVAS.PERSISTENT))
        ip_frag_off = Field(name='Fragment offset', domain=Data(dataType=BitArray(nbBits=13), originalValue=bitarray('0000000000000'), svas=SVAS.PERSISTENT))
        ip_ttl = Field(name='TTL', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('10000000'), svas=SVAS.PERSISTENT))
        ip_proto = Field(name='Protocol', domain=Integer(value=self.upperProtocol, unitSize=AbstractType.UNITSIZE_8, endianness=AbstractType.ENDIAN_BIG, sign=AbstractType.SIGN_UNSIGNED))
        ip_checksum = Field(name='Checksum', domain=BitArray(bitarray('0000000000000000')))
        ip_saddr = Field(name='Source address', domain=IPv4(self.localIP))
        ip_daddr = Field(name='Destination address', domain=IPv4(self.remoteIP))
        ip_payload = Field(name='Payload', domain=payload)

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
                                  ip_payload], dataType=Raw(nbBytes=2), factor=1/float(8))
        ip_checksum.domain = InternetChecksum(fields=[ip_ver,
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
                                                      ip_daddr], dataType=Raw(nbBytes=2))
        
        packet = Symbol(name='IP layer', fields=[ip_ver,
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
        return packet.specialize()

    # Management methods

    @property
    def isOpen(self):
        """Returns if the communication channel is open

        :return: the status of the communication channel
        :type: :class:`bool`
        """
        return self.__isOpen

    @isOpen.setter
    @typeCheck(bool)
    def isOpen(self, isOpen):
        self.__isOpen = isOpen

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
        return self.__timeout

    @timeout.setter
    @typeCheck(int)
    def timeout(self, timeout):
        self.__timeout = timeout
