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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Simulator.Channels.AbstractChannel import AbstractChannel


@NetzobLogger
class UDPServer(AbstractChannel):
    """A UDPServer is a communication channel. It allows to create a
    server that listen to a specific IP:Port over a UDP socket.

    When the actor executes an OpenChannelTransition, it calls the
    open method on the UDP server which makes it to listen for
    incomming messages.

    >>> from netzob.all import *
    >>> import time
    >>> server = UDPServer(localIP='127.0.0.1', localPort=9999)
    >>> server.open()
    >>> server.close()

    >>> symbol = Symbol([Field("Hello Zoby !")])
    >>> s0 = State()
    >>> s1 = State()
    >>> s2 = State()
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1)
    >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=symbol, outputSymbols=[symbol])
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2)
    >>> automata = Automata(s0, [symbol])

    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8884)
    >>> abstractionLayer = AbstractionLayer(channel, [symbol])
    >>> server = Actor(automata = automata, initiator = False, abstractionLayer=abstractionLayer)

    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8884)
    >>> abstractionLayer = AbstractionLayer(channel, [symbol])
    >>> client = Actor(automata = automata, initiator = True, abstractionLayer=abstractionLayer)

    >>> server.start()
    >>> client.start()

    >>> time.sleep(1)
    >>> client.stop()
    >>> server.stop()

    """

    @typeCheck(str, int)
    def __init__(self, localIP, localPort, timeout=5):
        super(UDPServer, self).__init__(isServer=False)
        self.localIP = localIP
        self.localPort = localPort
        self.timeout = timeout
        self.__isOpen = False
        self.__socket = None
        self.__remoteAddr = None

    def open(self, timeout=None):
        """Open the communication channel. This will open a UDP socket
        that listen for incomming messages.
        """

        if self.isOpen:
            raise RuntimeError("The channel is already open, cannot open it again.")

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Reuse the connection
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)
        self.__socket.bind((self.localIP, self.localPort))

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
            (data, self.__remoteAddr) = self.__socket.recvfrom(1024)
            return data
        else:
            raise Exception("socket is not available")

    @typeCheck(bytes)
    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        if self.__socket is not None and self.__remoteAddr is not None:
            self.__socket.sendto(data, self.__remoteAddr)
        else:
            raise Exception("Socket is not available or remote address is not known.")

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
    def localIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__localIP

    @localIP.setter
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

    @localPort.setter
    @typeCheck(int)
    def localPort(self, localPort):
        if localPort is None:
            raise TypeError("ListeningPort cannot be None")
        if localPort <= 0 or localPort > 65535:
            raise ValueError("ListeningPort must be > 0 and <= 65535")

        self.__localPort = localPort

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    @typeCheck(int)
    def timeout(self, timeout):
        self.__timeout = timeout
