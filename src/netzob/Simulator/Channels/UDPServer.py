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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import socket

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
class UDPServer(AbstractChannel):
    """A UDPServer is a communication channel. It provides a
    server listening to a specific IP:Port over a UDP socket.

    The UDPServer constructor expects some parameters:

    :param localIP: This parameter is the local IP address.
    :param localPort: This parameter is the local IP port.
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type localIP: :class:`str`, required
    :type localPort: :class:`int`, required
    :type timeout: :class:`float`, optional


    Adding to AbstractChannel variables, the UDPServer class provides the
    following public variables:

    :var localIP: The local IP address.
    :var localPort: The local IP port.
    :vartype localIP: :class:`str`
    :vartype localPort: :class:`int`


    The following code shows the use of a UDPServer channel:

    >>> from netzob.all import *
    >>> server = UDPServer(localIP='127.0.0.1', localPort=9999, timeout=1.)
    >>> server.open()
    >>> server.close()


    .. ifconfig:: scope in ('netzob')

       The following code shows a complete example of a communication
       between a client and a server in UDP:

       >>> from netzob.all import *
       >>> import time
       >>> symbol = Symbol([Field("Hello everyone!")])
       >>> s0 = State()
       >>> s1 = State()
       >>> s2 = State()
       >>> openTransition = OpenChannelTransition(startState=s0, endState=s1)
       >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=symbol, outputSymbols=[symbol])
       >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2)
       >>> automata = Automata(s0, [symbol])
       >>>
       >>> channel = UDPServer(localIP="127.0.0.1", localPort=8884, timeout=1.)
       >>> server = Actor(automata = automata, channel=channel)
       >>> server.initiator = False
       >>>
       >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8884, timeout=1.)
       >>> client = Actor(automata = automata, channel=channel)
       >>>
       >>> server.start()
       >>> client.start()
       >>>
       >>> time.sleep(1)
       >>> client.stop()
       >>> server.stop()

    """

    ## Class attributes ##

    FAMILIES = ["udp"]

    @public_api
    @typeCheck(str, int)
    def __init__(self,
                 localIP,
                 localPort,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT
                 ):
        super(UDPServer, self).__init__(timeout=timeout)
        self.localIP = localIP
        self.localPort = localPort
        self.__remoteAddr = None

    @staticmethod
    def getBuilder():
        return UDPServerBuilder

    @public_api
    def open(self, timeout=AbstractChannel.DEFAULT_TIMEOUT):
        """Open the communication channel. This will open a UDP socket
        that listen for incoming messages.
        :param timeout: The default timeout of the channel for opening
                        connection and waiting for a message. Default value
                        is blocking (None).
        :type timeout: :class:`float`, optional
        :raise: RuntimeError if the channel is already opened
        """

        super().open(timeout=timeout)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Reuse the connection
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(self.timeout)
        self._socket.bind((self.localIP, self.localPort))
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
            (data, self.__remoteAddr) = self._socket.recvfrom(1024)
            return data
        else:
            raise Exception("socket is not available")

    def writePacket(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self._socket is not None and self.__remoteAddr is not None:
            len_data = self._socket.sendto(data, self.__remoteAddr)
            return len_data
        else:
            raise Exception(
                "Socket is not available or remote address is not known.")

    @public_api
    @typeCheck(bytes)
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.
        """
        raise NotImplementedError("Not yet implemented")

    # Management methods

    # Properties

    @property
    def localIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__localIP

    @localIP.setter  # type: ignore
    @typeCheck(str)
    def localIP(self, localIP):
        if localIP is None:
            raise TypeError("ListeningIP cannot be None")

        self.__localIP = localIP

    @property
    def localPort(self):
        """UDP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__localPort

    @localPort.setter  # type: ignore
    @typeCheck(int)
    def localPort(self, localPort):
        if localPort is None:
            raise TypeError("ListeningPort cannot be None")
        if localPort <= 0 or localPort > 65535:
            raise ValueError("ListeningPort must be > 0 and <= 65535")

        self.__localPort = localPort

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


class UDPServerBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channels.UDPServer.UDPServer` instance

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(src_addr="4.3.2.1", src_port=32000)
    >>> builder = UDPServerBuilder().set_map(netinfo.getDict())
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.UDPServer.UDPServer'>
    >>> chan.localPort  # src_port key has been mapped to localPort attribute
    32000
    """

    @public_api
    def __init__(self):
        super().__init__(UDPServer)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_src_port(self, value):
        self.attrs['localPort'] = value
