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


@NetzobLogger
class IPChannel(AbstractChannel):
    """An IPChannel is a communication channel that is used to send IP
    payloads. The **kernel** is responsible for building the IP header. It is
    similar to the CustomIPChannel channel, except that with CustomIPChannel the
    channel builds the IP header. Therefore, with :class:`IPChannel <netzob.Simulator.Channels.IPChannel.IPChannel>`,
    we **cannot** modify or fuzz the IP header fields.

    The IPChannel constructor expects some parameters:

    :param remoteIP: This parameter is the remote IP address to connect to.
    :param localIP: The local IP address. Default value is the local
                    IP address corresponding to the interface that
                    will be used to send the packet.
    :param upperProtocol: The protocol following the IP header.
                          Default value is socket.IPPROTO_TCP.
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type remoteIP: :class:`str`, required
    :type localIP: :class:`str`, optional
    :type upperProtocol: :class:`int`, optional
    :type timeout: :class:`float`, optional


    Adding to AbstractChannel variables, the IPChannel class provides the
    following public variables:

    :var remoteIP: The remote IP address to connect to.
    :var localIP: The local IP address.
    :var upperProtocol: The protocol following the IP header.
    :vartype remoteIP: :class:`str`
    :vartype localIP: :class:`str`
    :vartype upperProtocol: :class:`int`


    The following code shows the use of an IPChannel channel:

    >>> from netzob.all import *
    >>> client = IPChannel(remoteIP='127.0.0.1', timeout=1.)
    >>> client.open()
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> client.write(next(symbol.specialize()))
    15
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
        super(IPChannel, self).__init__(timeout=timeout)
        self.remoteIP = remoteIP
        self.localIP = localIP
        self.upperProtocol = upperProtocol

    @staticmethod
    def getBuilder():
        return IPChannelBuilder

    @public_api
    def open(self, timeout=AbstractChannel.DEFAULT_TIMEOUT):
        """Open the communication channel. If the channel is a client, it
        starts to connect to the specified server.

        :param timeout: The default timeout of the channel for opening
                        connection and waiting for a message. Default value
                        is blocking (None).
        :type timeout: :class:`float`, optional
        :raise: RuntimeError if the channel is already opened

        """

        super().open(timeout=timeout)
        self._socket = socket.socket(socket.AF_INET,
                                     socket.SOCK_RAW,
                                     self.upperProtocol)
        self._socket.settimeout(timeout or self.timeout)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**30)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**30)
        self._socket.bind((self.localIP, 0))
        self.isOpen = True

    @public_api
    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    @public_api
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
        """Write on the communication channel the specified data

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self._socket is None:
            raise Exception("socket is not available")

        try:
            len_data = self._socket.sendto(data, (self.remoteIP, 0))
        except OSError as e:
            self._logger.warning("OSError durring socket.sendto(): '{}'. Trying a second time after sleeping 1s...".format(e))
            time.sleep(1)
            len_data = self._socket.sendto(data, (self.remoteIP, 0))
        return len_data

    @public_api
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.

        :param data: the data to write on the channel
        :type data: :class:`bytes`

        """
        if self._socket is None:
            raise Exception("socket is not available")

        usePorts = False
        if self.upperProtocol == socket.IPPROTO_TCP or \
           self.upperProtocol == socket.IPPROTO_UDP:
            usePorts = True
            # get the ports from message to identify the good response
            #  (in TCP or UDP)

            portSrcTx = (data[0] * 256) + data[1]
            portDstTx = (data[2] * 256) + data[3]

        self.write(data)
        while True:
            dataReceived = self.read()

            if usePorts:
                portSrcRx = (dataReceived[0] * 256) + dataReceived[1]
                portDstRx = (dataReceived[2] * 256) + dataReceived[3]

                if (portSrcTx == portDstRx) and \
                   (portDstTx == portSrcRx):
                    break
            else:
                # Any response is the good one
                break

        return dataReceived

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
        if localIP is not None:
            self.__localIP = localIP
        else:
            self.__localIP = "0.0.0.0"

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


class IPChannelBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channels.IPChannel.IPChannel` instance

    >>> import socket
    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(dst_addr="1.2.3.4",
    ...                   src_addr="4.3.2.1",
    ...                   protocol=socket.IPPROTO_TCP)
    >>> builder = IPChannelBuilder().set_map(netinfo.getDict())
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.IPChannel.IPChannel'>
    >>> chan.remoteIP  # dst_addr key has been mapped to remoteIP attribute
    '1.2.3.4'
    """

    @public_api
    def __init__(self):
        super().__init__(IPChannel)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_dst_addr(self, value):
        self.attrs['remoteIP'] = value

    def set_protocol(self, value):
        self.attrs['upperProtocol'] = value
