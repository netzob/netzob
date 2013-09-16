#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
from netzob.Common.Models.Simulator.Channels.AbstractChannel import AbstractChannel


@NetzobLogger
class TCPServer(AbstractChannel):
    """A TCPServer is a communication channel. It allows to create server listening
    on a specified IP:Port over a TCP socket.

    When the actor execute an OpenChannelTransition, it calls the open method
    on the tcp server which starts the server. The objective of the server is to wait for
    the client to connect.

    >>> from netzob.all import *
    >>> server = TCPServer(listeningIP='127.0.0.1', listeningPort=9999)
    >>> server.open()


    """

    def __init__(self, listeningIP, listeningPort):
        super(TCPServer, self).__init__(isServer=True)
        self.listeningIP = listeningIP
        self.listeningPort = listeningPort
        self.__isOpen = False

    def open(self, timeout=None):
        """Open the communication channel. If the channel is a server, it starts to listen
        and will create an instance for each different client"""
        if self.isOpen:
            raise RuntimeError("The channel is already open, cannot open it again")

        self.__socket = socket.socket()
        # Reuse the connection
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._logger.debug("Bind the TCP server to {0}:{1}".format(self.listeningIP, self.listeningPort))

        self.__socket.bind((self.listeningIP, self.listeningPort))
        self.__socket.listen()

    def close(self):
        """Close the communication channel."""
        pass

    def read(self, timeout=None):
        """Read the next message on the communication channel.

        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """
        pass

    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        pass

    # Management methods

    def isOpen(self):
        """Returns if the communication channel is open

        :return: the status of the communication channel
        :type: :class:`bool`
        """
        return self.__isOpen

    # Properties

    @property
    def listeningIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__listeningIP

    @listeningIP.setter
    @typeCheck(str)
    def listeningIP(self, listeningIP):
        if listeningIP is None:
            raise TypeError("ListeningIP cannot be None")

        self.__listeningIP = listeningIP

    @property
    def listeningPort(self):
        """TCP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__listeningPort

    @listeningPort.setter
    @typeCheck(int)
    def listeningPort(self, listeningPort):
        if listeningPort is None:
            raise TypeError("ListeningPort cannot be None")
        if listeningPort <= 0 or listeningPort > 65535:
            raise ValueError("ListeningPort must be > 0 and <= 65535")

        self.__listeningPort = listeningPort
