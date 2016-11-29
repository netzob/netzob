#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
#|       - Georges Bossert <gbossert (a) miskin.fr>                          |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import socket
import time
import ssl

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Simulator.Channels.AbstractChannel import AbstractChannel, ChannelDownException


@NetzobLogger
class SSLClient(AbstractChannel):
    """An SSLClient is a communication channel that relies on SSL. It allows to create client connecting
    to a specific IP:Port server over a TCP/SSL socket.

    When the actor execute an OpenChannelTransition, it calls the open
    method on the ssl client which connects to the server.

    """

    def __init__(self, remoteIP, remotePort, localIP=None, localPort=None, timeout=2, server_cert_file=None, alpn_protocols=None):
        super(SSLClient, self).__init__(isServer=False)
        self.remoteIP = remoteIP
        self.remotePort = remotePort
        self.localIP = localIP
        self.localPort = localPort
        self.timeout = timeout
        self.__isOpen = False
        self.__socket = None
        self.__ssl_socket = None
        self.server_cert_file = server_cert_file
        self.alpn_protocols = alpn_protocols

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

        # lets create the ssl context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.check_hostname = False
        context.load_default_certs()
        if self.server_cert_file is not None:
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(self.server_cert_file)
        else:
            context.verify_mode = ssl.CERT_NONE

        if self.alpn_protocols is not None:
            context.set_alpn_protocols(self.alpn_protocols)

        
        # lets wrap the socket to create the ssl tunnel
        self.__ssl_socket = context.wrap_socket(self.__socket)
        self.__ssl_socket.settimeout(self.timeout)
            
        self._logger.debug("Connect to the SSL server to {0}:{1}".format(self.remoteIP, self.remotePort))
        self.__ssl_socket.connect((self.remoteIP, self.remotePort))

    def close(self):
        """Close the communication channel."""
        if self.__ssl_socket is not None:
            self.__ssl_socket.close()
        if self.__socket is not None:
            self.__socket.close()

    def read(self, timeout=None):
        """Read the next message on the communication channel.

        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """
        reading_seg_size = 1024
        
        if self.__ssl_socket is not None:
            data = ""
            finish = False
            while not finish:
                try:
                    recv = self.__ssl_socket.recv(reading_seg_size)
                except ssl.SSLError:
                    # says we received nothing (timeout issue)
                    recv = ""
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
                self.__ssl_socket.sendall(data)
            except ssl.SSLError:
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
    def timeout(self, timeout):
        self.__timeout = timeout
