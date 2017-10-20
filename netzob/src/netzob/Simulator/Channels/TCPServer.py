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
from netzob.Simulator.AbstractChannel import AbstractChannel
from netzob.Simulator.ChannelBuilder import ChannelBuilder


@NetzobLogger
class TCPServer(AbstractChannel):
    """A TCPServer is a communication channel. It provides a
    server listening to a specified IP:Port over a TCP socket.

    When the actor executes an OpenChannelTransition, it calls the open
    method on the tcp server which starts the server. The objective of
    the server is to wait for the client to connect.

    The TCPServer constructor expects some parameters:

    :param localIP: The local IP address.
    :param localPort: The local IP port.
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type localIP: :class:`str`, required
    :type localPort: :class:`int`, required
    :type timeout: :class:`float`, optional


    Adding to AbstractChannel variables, the TCPServer class provides the
    following public variables:

    :var localIP: The local IP address.
    :var localPort: The local IP port.
    :vartype localIP: :class:`str`
    :vartype localPort: :class:`int`


    The following code shows the creation of a TCPServer channel:

    >>> from netzob.all import *
    >>> server = TCPServer(localIP='127.0.0.1', localPort=9999, timeout=1.)


    .. ifconfig:: scope in ('netzob')

       The following code shows a complete example of a communication
       between a client and a server in TCP:

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

       >>> channel = TCPServer(localIP="127.0.0.1", localPort=8886, timeout=1.)
       >>> abstractionLayer = AbstractionLayer(channel, [symbol])
       >>> server = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)

       >>> channel = TCPClient(remoteIP="127.0.0.1", remotePort=8886, timeout=1.)
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
                 localIP,
                 localPort,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT
                 ):
        super(TCPServer, self).__init__(timeout=timeout)
        self.localIP = localIP
        self.localPort = localPort
        self.__socket = None
        self.__clientSocket = None

    @staticmethod
    def getBuilder():
        return TCPServerBuilder

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

        self.__socket = socket.socket()
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the connection
        self.__socket.settimeout(timeout or self.timeout)
        self._logger.debug("Bind the TCP server to {0}:{1}".format(
            self.localIP, self.localPort))
        self.__socket.bind((self.localIP, self.localPort))
        self.__socket.listen(1)
        self._logger.debug("Ready to accept new TCP connections...")
        self.__clientSocket, addr = self.__socket.accept()
        self._logger.debug("New TCP connection received.")
        self.isOpen = True

    def close(self):
        """Close the communication channel."""
        if self.__clientSocket is not None:
            self.__clientSocket.close()
        if self.__socket is not None:
            self.__socket.close()
        self.isOpen = False
        self._logger.info("TCPServer has closed its socket")

    def read(self):
        """Read the next message on the communication channel.
        """
        reading_seg_size = 1024

        # Read loop
        if self.__clientSocket is not None:
            data = b""
            finish = False
            while not finish:
                try:
                    recv = self.__clientSocket.recv(reading_seg_size)
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
        if self.__clientSocket is not None:
            self.__clientSocket.sendall(data)
            return len(data)
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
    def localIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__localIP

    @localIP.setter
    @typeCheck(str)
    def localIP(self, localIP):
        if localIP is None:
            raise TypeError("LocalIP cannot be None")

        self.__localIP = localIP

    @property
    def localPort(self):
        """TCP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__localPort

    @localPort.setter
    @typeCheck(int)
    def localPort(self, localPort):
        if localPort is None:
            raise TypeError("LocalPort cannot be None")
        if localPort <= 0 or localPort > 65535:
            raise ValueError("LocalPort must be > 0 and <= 65535")

        self.__localPort = localPort


class TCPServerBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channel.TCPServer.TCPServer` instance

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(src_addr="4.3.2.1", src_port=32000)
    >>> chan = TCPServerBuilder().set_map(netinfo.getDict()).build()
    >>> assert isinstance(chan, TCPServer)
    """

    def __init__(self):
        super().__init__(TCPServer)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_src_port(self, value):
        self.attrs['localPort'] = value
