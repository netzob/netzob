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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Simulator.Channels.AbstractChannel import AbstractChannel, ChannelDownException


@NetzobLogger
class TCPClient(AbstractChannel):
    """A TCPClient is a communication channel. It allows to create client connecting
    to a specific IP:Port server over a TCP socket.

    When the actor execute an OpenChannelTransition, it calls the open
    method on the tcp client which connects to the server.

    >>> from netzob.all import *
    >>> import time
    >>> client = TCPClient(remoteIP='127.0.0.1', remotePort=9999)

    >>> symbol = Symbol([Field("Hello Zoby !")])
    >>> s0 = State()
    >>> s1 = State()
    >>> s2 = State()
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1)
    >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=symbol, outputSymbols=[symbol])
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2)
    >>> automata = Automata(s0, [symbol])

    >>> channel = TCPServer(localIP="127.0.0.1", localPort=8885)
    >>> abstractionLayer = AbstractionLayer(channel, [symbol])
    >>> server = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)

    >>> channel = TCPClient(remoteIP="127.0.0.1", remotePort=8885)
    >>> abstractionLayer = AbstractionLayer(channel, [symbol])
    >>> client = Actor(automata = automata, initiator = True, abstractionLayer=abstractionLayer)

    >>> server.start()
    >>> client.start()

    >>> time.sleep(1)
    >>> client.stop()
    >>> server.stop()

    """

    def __init__(self, remoteIP, remotePort, localIP=None, localPort=None, timeout=5):
        super(TCPClient, self).__init__(isServer=False)
        self.remoteIP = remoteIP
        self.remotePort = remotePort
        self.localIP = localIP
        self.localPort = localPort
        self.timeout = timeout
        self.__isOpen = False
        self.__socket = None

    def open(self, timeout=None):
        """Open the communication channel. If the channel is a client, it starts to connect
        to the specified server.
        """

        if self.isOpen:
            raise RuntimeError("The channel is already open, cannot open it again")

        self.__socket = socket.socket()
        # Reuse the connection
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)
        if self.localIP is not None and self.localPort is not None:
            self.__socket.bind((self.localIP, self.localPort))
        self._logger.debug("Connect to the TCP server to {0}:{1}".format(self.remoteIP, self.remotePort))
        self.__socket.connect((self.remoteIP, self.remotePort))

    def close(self):
        """Close the communication channel."""
        if self.__socket is not None:
            self.__socket.close()

    def read(self, timeout=None):
        """Reads the next message on the communication channel.
        Continues to read while it receives something.


        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """
        reading_seg_size = 1024
        
        if self.__socket is not None:
            data = b""
            finish = False
            while not finish:
                try:
                    recv = self.__socket.recv(reading_seg_size)
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

    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        if self.__socket is not None:
            try:
                self.__socket.sendall(data)
            except socket.error:
                raise ChannelDownException()

        else:
            raise Exception("socket is not available")

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
            raise TypeError("RemoteIP cannot be None")

        self.__remoteIP = remoteIP

    @property
    def remotePort(self):
        """TCP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__remotePort

    @remotePort.setter
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

    @localIP.setter
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

    @localPort.setter
    @typeCheck(int)
    def localPort(self, localPort):
        self.__localPort = localPort

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    @typeCheck(int)
    def timeout(self, timeout):
        self.__timeout = timeout
