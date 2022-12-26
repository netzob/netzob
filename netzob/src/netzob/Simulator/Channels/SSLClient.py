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
#|       - Georges Bossert <gbossert (a) miskin.fr>                          |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import socket
import ssl

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Simulator.AbstractChannel import (AbstractChannel,
                                              ChannelDownException,
                                              NetUtils)
from netzob.Simulator.ChannelBuilder import ChannelBuilder


@NetzobLogger
class SSLClient(AbstractChannel):
    """An SSLClient is a communication channel that relies on SSL. It provides
    the connection of a client to a specific IP:Port server over a TCP/SSL
    socket.

    The SSLClient constructor expects some parameters:

    :param remoteIP: This parameter is the remote IP address to connect to.
    :param remotePort: This parameter is the remote IP port.
    :param localIP: The local IP address. Default value is the local
                    IP address corresponding to the network interface that
                    will be used to send the packet.
    :param localPort: The local IP port. Default value in a random
                     valid integer chosen by the kernel.
    :param server_cert_file: The path to a single file in PEM format
                             containing the certificate as well as any
                             number of CA certificates needed to
                             establish the certificate's
                             authenticity. Default value is None,
                             meaning that no verification is made on
                             the certificate given by the peer.
    :param alpn_protocols: Specify which protocols the socket should
                           advertise during the SSL/TLS handshake. It
                           should be a list of strings, like
                           ['http/1.1', 'spdy/2'], ordered by
                           preference. Default value is None.
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type remoteIP: :class:`str`, required
    :type remotePort: :class:`int`, required
    :type localIP: :class:`str`, optional
    :type localPort: :class:`int`, optional
    :type server_cert_file: :class:`str`, optional
    :type alpn_protocols: :class:`list`, optional
    :type timeout: :class:`float`, optional

    Adding to AbstractChannel public variables, the SSLClient class provides the
    following public variables:

    :var remoteIP: The remote IP address to connect to.
    :var remotePort: The remote IP port.
    :var localIP: The local IP address.
    :var localPort: The local IP port.
    :var server_cert_file: The path to a single file in PEM format
                             containing the certificate as well as any
                             number of CA certificates needed to
                             establish the certificate's
                             authenticity.
    :var alpn_protocols: Specify which protocols the socket should
                         advertise during the SSL/TLS handshake. It
                         should be a list of strings, like
                         ['http/1.1', 'spdy/2'], ordered by
                         preference.
    :vartype remoteIP: :class:`str`
    :vartype remotePort: :class:`int`
    :vartype localIP: :class:`str`
    :vartype localPort: :class:`int`
    :vartype server_cert_file: :class:`str`
    :vartype alpn_protocols: :class:`list`


    The following code shows the creation of a SSLClient channel:

    >>> from netzob.all import *
    >>> server = SSLClient(remoteIP='127.0.0.1', remotePort=9999)

    """

    ## Class attributes ##

    FAMILIES = ["tcp"]

    @public_api
    def __init__(self,
                 remoteIP,
                 remotePort,
                 localIP=None,
                 localPort=None,
                 server_cert_file=None,
                 alpn_protocols=None,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(SSLClient, self).__init__(timeout=timeout)
        self.remoteIP = remoteIP
        self.remotePort = remotePort
        self.localIP = localIP
        self.localPort = localPort
        self.__ssl_socket = None
        self.server_cert_file = server_cert_file
        self.alpn_protocols = alpn_protocols

    @staticmethod
    def getBuilder():
        return SSLClientBuilder

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

        self._socket = socket.socket()
        # Reuse the connection
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(timeout or self.timeout)

        if self.localIP is not None and self.localPort is not None:
            self._socket.bind((self.localIP, self.localPort))

        # lets create the ssl context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
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
        self.__ssl_socket = context.wrap_socket(self._socket)
        self.__ssl_socket.settimeout(timeout or self.timeout)

        self._logger.debug("Connect to the SSL server to {0}:{1}".format(
            self.remoteIP, self.remotePort))
        self.__ssl_socket.connect((self.remoteIP, self.remotePort))
        self.isOpen = True

    @public_api
    def close(self):
        """Close the communication channel."""
        if self.__ssl_socket is not None:
            self.__ssl_socket.close()
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    @public_api
    def read(self):
        """Read the next message on the communication channel.
        """
        reading_seg_size = 1024

        if self.__ssl_socket is not None:
            data = b""
            finish = False
            while not finish:
                try:
                    recv = self.__ssl_socket.recv(reading_seg_size)
                except Exception as e:
                    # says we received nothing (timeout issue)
                    recv = b""
                    self._logger.error(e)
                    
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
                self.__ssl_socket.sendall(data)
                return len(data)
            except ssl.SSLError:
                raise ChannelDownException()

        else:
            raise Exception("socket is not available")

    @public_api
    @typeCheck(bytes)
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
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

    def updateSocketTimeout(self):
        """Update the timeout of the socket."""
        super(SSLClient, self).updateSocketTimeout()
        if self._socket is not None:
            self.__ssl_socket.settimeout(self.timeout)

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


class SSLClientBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channels.SSLClient.SSLClient` instance

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(dst_addr="1.2.3.4", dst_port=1024,
    ...                   src_addr="4.3.2.1", src_port=32000)
    >>> builder = SSLClientBuilder().set_map(netinfo.getDict())
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.SSLClient.SSLClient'>
    >>> chan.remotePort  # dst_port key has been mapped to remotePort attribute
    1024
    """

    @public_api
    def __init__(self):
        super().__init__(SSLClient)

    def set_src_addr(self, value):
        self.attrs['localIP'] = value

    def set_dst_addr(self, value):
        self.attrs['remoteIP'] = value

    def set_src_port(self, value):
        self.attrs['localPort'] = value

    def set_dst_port(self, value):
        self.attrs['remotePort'] = value

    def set_server_cert_file(self, value):
        self.attrs['server_cert_file'] = value

    def set_alpn_protocls(self, value):
        self.attrs['alpn_protocls'] = value
