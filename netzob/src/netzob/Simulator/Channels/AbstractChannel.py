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
import uuid
import abc
import socket
import os
import fcntl
import struct
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class ChannelDownException(Exception):
    pass


class AbstractChannel(object, metaclass=abc.ABCMeta):

    TYPE_UNDEFINED = 0
    TYPE_RAWIPCLIENT = 1
    TYPE_IPCLIENT = 2
    TYPE_RAWETHERNETCLIENT = 3
    TYPE_SSLCLIENT = 4
    TYPE_TCPCLIENT = 5
    TYPE_TCPSERVER = 6
    TYPE_UDPCLIENT = 7
    TYPE_UDPSERVER = 8

    DEFAULT_WRITE_COUNTER_MAX = -1

    def __init__(self, isServer, _id=uuid.uuid4()):
        """Constructor for an Abstract Channel

        :parameter isServer: indicates if the channel is a server or not
        :type isServer: :class:`bool`
        :keyword _id: the unique identifier of the channel
        :type _id: :class:`uuid.UUID`
        :raise TypeError if parameters are not valid
        """

        self.isServer = isServer
        self.id = _id
        self.isOpened = False
        self.type = AbstractChannel.TYPE_UNDEFINED
        self.writeCounter = 0
        self.writeCounterMax = AbstractChannel.DEFAULT_WRITE_COUNTER_MAX

    def __enter__(self):
        """Enter the runtime channel context.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime channel context.
        """
        self.close()

    # Static methods used to retrieve local network interface
    # and local IP according to a remote IP

    @staticmethod
    def getLocalInterface(localIP):
        """Retrieve the network interface name associated with a specific IP
        address.
        """

        def getIPFromIfname(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
            )[20:24])

        ifname = None
        for networkInterface in os.listdir('/sys/class/net/'):
            try:
                ipAddress = getIPFromIfname(networkInterface)
            except:
                continue
            if ipAddress == localIP:
                ifname = networkInterface
                break
        return ifname

    @staticmethod
    def getLocalIP(remoteIP):
        """Retrieve the source IP address which will be used to connect to the
        destination IP address.
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remoteIP, 53))
        localIPAddress = s.getsockname()[0]
        s.close()
        return localIPAddress

    # OPEN, CLOSE, READ and WRITE methods

    @abc.abstractmethod
    def open(self, timeout=None):
        """Open the communication channel. If the channel is a server, it starts
        to listen and will create an instance for each different client.

        :keyword timeout: the maximum time to wait for a client to connect
        :type timout:
        """

    @abc.abstractmethod
    def close(self):
        """Close the communication channel."""

    @abc.abstractmethod
    def read(self, timeout=None):
        """Read the next message on the communication channel.

        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """

    def setWriteCounterMax(self, maxValue):
        """Change the max number of writings.
        When it is reached, no packet can be sent anymore until
        clearWriteCounter() is called.
        if maxValue==-1, the sending limit is deactivated.

        :parameter maxValue: the new max value
        :type maxValue: int
        """
        self.writeCounterMax = maxValue

    def clearWriteCounter(self):
        """Reset the writings counter.
        """
        self.writeCounter = 0

    def write(self, data, rate=None, duration=None):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: bytes object

        :param rate: specifies the bandwidth in octets to respect during traffic emission (should be used with duration= parameter)
        :type rate: int

        :param duration: tells how much seconds the symbol is continuously written on the channel
        :type duration: int

        :param duration: tells how much time the symbol is written on the channel
        :type duration: int

        """

        if ((self.writeCounterMax > 0) and
           (self.writeCounter > self.writeCounterMax)):
            raise Exception("Max write counter reached ({})"
                            .format(self.writeCounterMax))

        self.writeCounter += 1
        len_data = 0
        if duration is None:
            len_data = self.writePacket(data)
        else:

            t_start = time.time()
            t_elapsed = 0
            t_delta = 0
            while True:

                t_elapsed = time.time() - t_start
                if t_elapsed > duration:
                    break

                # Specialize the symbol and send it over the channel
                len_data += self.writePacket(data)

                if rate is None:
                    t_tmp = t_elapsed
                    t_elapsed = time.time() - t_start
                    t_delta += t_elapsed - t_tmp
                else:
                    # Wait some time to that we follow a specific rate
                    while True:
                        t_tmp = t_elapsed
                        t_elapsed = time.time() - t_start
                        t_delta += t_elapsed - t_tmp

                        if (len_data / t_elapsed) > rate:
                            time.sleep(0.001)
                        else:
                            break

                # Show some log every seconds
                if t_delta > 1:
                    t_delta = 0
                    self._logger.debug("Rate rule: {} ko/s, current rate: {} ko/s, sent data: {} ko, nb seconds elapsed: {}".format(round(rate / 1024, 2),
                                                                                                                                    round((len_data / t_elapsed) / 1024, 2),
                                                                                                                                    round(len_data / 1024, 2),
                                                                                                                                    round(t_elapsed, 2)))
        return len_data

    @abc.abstractmethod
    def writePacket(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """

    @abc.abstractmethod
    def sendReceive(self, data, timeout=None):
        """Write on the communication channel the specified data and returns the corresponding response

        :parameter data: the data to write on the channel
        :type data: binary object
        @type timeout: :class:`int`
        """

    # Management methods

    @property
    def isOpen(self):
        """Returns if the communication channel is open

        :return: the status of the communication channel
        :type: :class:`bool`
        """
        return self.isOpened

    @isOpen.setter
    @typeCheck(bool)
    def isOpen(self, isOpen):
        self.isOpened = isOpen

    # Properties

    @property
    def channelType(self):
        """Returns if the communication channel type

        :return: the type of the communication channel
        :type: :class:`int`
        """
        return self.type

    @property
    def isServer(self):
        """isServer indicates if this side of the channel plays the role of a server.

        :type: :class:`bool`
        """
        return self.__isServer

    @isServer.setter
    @typeCheck(bool)
    def isServer(self, isServer):
        if isServer is None:
            raise TypeError("IsServer cannot be None")
        self.__isServer = isServer

    @property
    def id(self):
        """the unique identifier of the channel

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("ID cannot be None")
        self.__id = _id
