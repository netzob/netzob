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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Simulator.AbstractChannel import AbstractChannel, ChannelDownException
from netzob.Simulator.ChannelBuilder import ChannelBuilder


@NetzobLogger
class TCPClient(AbstractChannel):
    """A TCPClient is a communication channel. It provides the connection of a
    client to a specific IP:Port server over a TCP socket.

    When the actor executes an OpenChannelTransition, it calls the open
    method on the TCP client which connects to the server.

    The TCPClient constructor expects some parameters:

    :param remoteIP: This parameter is the remote IP address to connect to.
    :param remotePort: This parameter is the remote IP port.
    :param localIP: The local IP address. Default value is the local
                    IP address corresponding to the network interface that
                    will be used to send the packet.
    :param localPort: The local IP port. Default value in a random
                    valid integer chosen by the kernel.
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type remoteIP: :class:`str`, required
    :type remotePort: :class:`int`, required
    :type localIP: :class:`str`, optional
    :type localPort: :class:`int`, optional
    :type timeout: :class:`float`, optional


    Adding to AbstractChannel variables, the TCPClient class provides the
    following public variables:

    :var remoteIP: The remote IP address to connect to.
    :var remotePort: The remote IP port.
    :var localIP: The local IP address.
    :var localPort: The local IP port.
    :vartype remoteIP: :class:`str`
    :vartype remotePort: :class:`int`
    :vartype localIP: :class:`str`
    :vartype localPort: :class:`int`


    The following code shows the creation of a TCPClient channel:

    >>> from netzob.all import *
    >>> client = TCPClient(remoteIP='127.0.0.1', remotePort=9999, timeout=1.)


    .. ifconfig:: scope in ('netzob')

       Complete example with the use of an actor.

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

       >>> channel = TCPServer(localIP="127.0.0.1", localPort=8885, timeout=1.)
       >>> abstractionLayer = AbstractionLayer(channel, [symbol])
       >>> server = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)

       >>> channel = TCPClient(remoteIP="127.0.0.1", remotePort=8885, timeout=1.)
       >>> abstractionLayer = AbstractionLayer(channel, [symbol])
       >>> client = Actor(automata = automata, initiator = True, abstractionLayer=abstractionLayer)

       >>> server.start()
       >>> client.start()

       >>> time.sleep(1)
       >>> client.stop()
       >>> server.stop()

    """

    ## Class attributes ##

    FAMILIES = ["tcp"]


    def __init__(self,
                 remoteIP,
                 remotePort,
                 localIP=None,
                 localPort=None,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(TCPClient, self).__init__(timeout=timeout)
        self.remoteIP = remoteIP
        self.remotePort = remotePort
        self.localIP = localIP
        self.localPort = localPort

    @staticmethod
    def getBuilder():
        return TCPClientBuilder

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

        self._socket = socket.socket()
        # Reuse the connection
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(timeout or self.timeout)
        if self.localIP is not None and self.localPort is not None:
            self._socket.bind((self.localIP, self.localPort))
        self._logger.debug("Connect to the TCP server to {0}:{1}".format(
            self.remoteIP, self.remotePort))
        self._socket.connect((self.remoteIP, self.remotePort))
        self.isOpen = True

    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    def read(self):
        """Reads the next message on the communication channel.
        Continues to read while it receives something.
        """
        reading_seg_size = 1024

        if self._socket is not None:
            data = b""
            finish = False
            while not finish:
                try:
                    recv = self._socket.recv(reading_seg_size)
                except socket.timeout:
                    # says we received nothing (timeout issue)
                    recv = b""
                if recv is None or len(recv) == 0:
                    finish = True
                else:
                    data += recv
            return data
        else:
            raise Exception("socket is not available")

    def writePacket(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self._socket is not None:
            try:
                self._socket.sendall(data)
                return len(data)
            except socket.error:
                raise ChannelDownException()

        else:
            raise Exception("socket is not available")

    @typeCheck(bytes)
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.
        """

        raise NotImplementedError("Not yet implemented")

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
            raise TypeError("RemoteIP cannot be None")

        self.__remoteIP = remoteIP

    @property
    def remotePort(self):
        """TCP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__remotePort

    @remotePort.setter  # type: ignore
    @typeCheck(int)
    def remotePort(self, remotePort):
        if remotePort is None:
            raise TypeError("RemotePort cannot be None")
        if remotePort <= 0 or remotePort > 65535:
            raise ValueError("RemotePort must be > 0 and <= 65535")

        self.__remotePort = remotePort

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
    def localPort(self):
        """TCP Port on which the server will listen.
        Its value must be above 0 and under 65535.

        :type: :class:`int`
        """
        return self.__localPort

    @localPort.setter  # type: ignore
    @typeCheck(int)
    def localPort(self, localPort):
        self.__localPort = localPort


class TCPClientBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channel.TCPClient.TCPClient` instance

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(dst_addr="1.2.3.4", dst_port=1024,
    ...                   src_addr="4.3.2.1", src_port=32000)
    >>> chan = TCPClientBuilder().set_map(netinfo.getDict()).build()
    >>> assert isinstance(chan, TCPClient)
    """

    def __init__(self):
        super().__init__(TCPClient)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_dst_addr(self, value):
        self.attrs['remoteIP'] = value

    def set_src_port(self, value):
        self.attrs['localPort'] = value

    def set_dst_port(self, value):
        self.attrs['remotePort'] = value
