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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Simulator.Channels.AbstractChannel import AbstractChannel


@NetzobLogger
class UDPClient(AbstractChannel):
    """A UDPClient is a communication channel. It allows to create client connecting
    to a specific IP:Port server over a UDP socket.

    When the actor executes an OpenChannelTransition, it calls the
    open method on the UDP client which connects to the server.

    >>> from netzob.all import *
    >>> client = UDPClient(destIP='127.0.0.1', destPort=9999)
    >>> client.open()


    """

    @typeCheck(str, int)
    def __init__(self, destIP, destPort, localIP="127.0.0.1", localPort=random.randint(1024,65535)):
        super(UDPClient, self).__init__(isServer=False)
        self.destIP = destIP
        self.destPort = destPort
        self.localIP = localIP
        self.localPort = localPort
        self.__isOpen = False
        self.__socket = None

    def open(self, timeout=None):
        """Open the communication channel. If the channel is a client, it starts to connect
        to the specified server.
        """

        if self.isOpen:
            raise RuntimeError("The channel is already open, cannot open it again")

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Reuse the connection
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            (data, remoteAddr) = self.__socket.recvfrom(1024)
            return data
        else:
            raise Exception("socket is not available")

    @typeCheck(str)
    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        if self.__socket is not None:
            self.__socket.sendto(data, (self.destIP, self.destPort))
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
    def destIP(self):
        """IP on which the server will listen.

        :type: :class:`str`
        """
        return self.__destIP

    @destIP.setter
    @typeCheck(str)
    def destIP(self, destIP):
        if destIP is None:
            raise TypeError("ListeningIP cannot be None")

        self.__destIP = destIP

    @property
    def destPort(self):
        """UDP Port on which the server will listen.
        Its value must be above 0 and under 65535.


        :type: :class:`int`
        """
        return self.__destPort

    @destPort.setter
    @typeCheck(int)
    def destPort(self, destPort):
        if destPort is None:
            raise TypeError("ListeningPort cannot be None")
        if destPort <= 0 or destPort > 65535:
            raise ValueError("ListeningPort must be > 0 and <= 65535")

        self.__destPort = destPort
