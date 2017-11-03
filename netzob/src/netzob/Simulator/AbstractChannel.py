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
import arpreq
import binascii
from fcntl import ioctl
import subprocess
from typing import Callable, List, Type  # noqa: F401

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Simulator.ChannelBuilder import ChannelBuilder


class ChannelDownException(Exception):
    pass


class ChannelInterface(object, metaclass=abc.ABCMeta):
    """The ChannelInterface class specifies the methods to implement in
    order to create a new communication channel.

    The following methods have to be implemented:

    * :meth:`~.open`
    * :meth:`~.close`
    * :meth:`~.read`
    * :meth:`~.writePacket`
    * :meth:`~.sendReceive`

    To associate a channel into a group a *similar* channels, class should
    declare a list of compatible families. An empty list of families means that
    the channel is *similar* to all possible families.

    """

    # Class attributes ##

    FAMILIES = []  # type: List[str]
    """
    **Class attribute**.

    :class:`~typing.List` of families.
    This attribute should be superseded in child classes.
    An empty list means that the channel is *similar* to all possible families.

    :type: :class:`List[str]`
    """

    # Class internal attributes #

    DEFAULT_WRITE_COUNTER_MAX = -1
    DEFAULT_TIMEOUT = None

    def __init__(self, timeout=DEFAULT_TIMEOUT):
        """
        :param timeout: The default timeout of the channel for global
                        connection. Default value is blocking (None).
        :type timeout: :class:`float`, optional

        """
        self.timeout = timeout

    # Interface methods ##

    @abc.abstractmethod
    def open(self, timeout=DEFAULT_TIMEOUT):
        """Open the communication channel. If the channel is a server, it
        starts to listen for incoming data.

        :param timeout: The default timeout of the channel for opening
                        connection and waiting for a message. Default value
                        is blocking (None).
        :type timeout: :class:`float`, optional

        """
        if self.isOpen:
            raise RuntimeError(
                "The channel is already open, cannot open it again")

    @abc.abstractmethod
    def close(self):
        """Close the communication channel."""

    @abc.abstractmethod
    def read(self):
        """Read the next message from the communication channel.

        :return: The received data.
        :rtype: :class:`bytes`

        """

    @abc.abstractmethod
    def writePacket(self, data):
        """Write on the communication channel the specified data.

        :param data: The data to write on the channel.
        :type data: :class:`bytes`
        """

    @abc.abstractmethod
    def sendReceive(self, data):
        """Write on the communication channel the specified data, wait for a
        response and return the received data.

        :param data: The data to write on the channel.
        :type data: :class:`bytes`, required
        :return: The received data.
        :rtype: :class:`bytes`

        """

    @property
    def timeout(self):
        """The default timeout of the channel for opening connection and
        waiting for a message. Default value is DEFAULT_TIMEOUT seconds
        (float). To specify no timeout, None value is expected.

        :rtype: :class:`float` or None
        """
        return self._timeout

    @timeout.setter
    @typeCheck((int, float, type(None)))
    def timeout(self, timeout):
        """
        :type timeout: :class:`float`, optional
        """
        self._timeout = None if timeout is None else float(timeout)


class AbstractChannel(ChannelInterface, metaclass=abc.ABCMeta):
    """A communication channel is an element allowing to establish a
    connection to or from a remote device.

    The AbstractChannel defines the API of a communication channel.

    A communication channel provides the following public variables:

    :var isOpen: The status of the communication channel.
    :var timeout: The default timeout in seconds for opening a connection and
                  waiting for a message.
    :var header: A Symbol that permits to access to the protocol header.
    :var header_presets: A dictionary of keys:values used to preset
                        (parameterize) the header fields during symbol
                        specialization. See :meth:`Symbol.specialize() <netzob.Model.Vocabulary.Symbol.Symbol.specialize>` for more information.
    :vartype isOpen: :class:`bool`
    :vartype timeout: :class:`int`
    :vartype header: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
    :vartype header_presets: ~typing.Dict[
                             ~typing.Union[str,~netzob.Model.Vocabulary.Field.Field],
                             ~typing.Union[~bitarray.bitarray,bytes,
                             ~netzob.Model.Vocabulary.Types.AbstractType.AbstractType]],
                             optional


    """

    # Abstract methods ##

    @abc.abstractstaticmethod
    def getBuilder():  # type: () -> Type[ChannelBuilder]
        """
        Provide the builder specific to an :class:`AbstractChannel`
        """

    # Public API methods ##

    def setSendLimit(self, maxValue):
        """Change the max number of writings.

        When it is reached, no packet can be sent anymore until
        :meth:`clearSendLimit` is called.

        If maxValue is -1, the sending limit is deactivated.

        :param maxValue: the new max value
        :type maxValue: :class:`int`, required
        """
        self.__writeCounterMax = maxValue

    def clearSendLimit(self):
        """Reset the writing counters.
        """
        self.__writeCounter = 0
        self.__writeCounterMax = AbstractChannel.DEFAULT_WRITE_COUNTER_MAX

    def write(self, data, rate=None, duration=None):
        """Write to the communication channel the specified data, either one
        time, either in loop according to the `rate` and `duration`
        parameter.

        :param data: The data to write on the channel.
        :param rate: This specifies the bandwidth in octets to respect during
                     traffic emission (should be used with duration= parameter).
        :param duration: This tells how much seconds the data is continuously
                         written on the channel.
        :type data: :class:`bytes`, required
        :type rate: :class:`int`, optional
        :type duration: :class:`int`, optional
        :return: The amount of written data, in bytes.
        :rtype: :class:`int`

        """

        if ((self.__writeCounterMax > 0) and
           (self.__writeCounter > self.__writeCounterMax)):
            raise Exception("Max write counter reached ({})"
                            .format(self.__writeCounterMax))

        rate_text = "unlimited"
        rate_unlimited = True
        if type(rate) is int and rate > 0:
            rate_text = "{} ko/s".format(round(rate / 1024, 2))
            rate_unlimited = False

        self.__writeCounter += 1
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

                while True:
                    t_tmp = t_elapsed
                    t_elapsed = time.time() - t_start
                    t_delta += t_elapsed - t_tmp

                    if not rate_unlimited and (len_data / t_elapsed) > rate:
                        time.sleep(0.001)
                    else:
                        break

                # Show some log every seconds
                if t_delta > 1:
                    t_delta = 0
                    self._logger.debug("Rate rule: {}, current rate: {} ko/s, sent data: {} ko, nb seconds elapsed: {}".format(rate_text,
                                                                                                                               round((len_data / t_elapsed) / 1024, 2),
                                                                                                                               round(len_data / 1024, 2),
                                                                                                                               round(t_elapsed, 2)))
        return len_data

    def checkReceived(self,
                      predicate,  # type: Callable[[bytes], bool]
                      *args, **kwargs):
        # type: (...) -> bool
        """
        Method used to delegate the validation of the received data into
        a callback

        :param predicate: the function used to validate the received data
        :param args: positional arguments passed to :attr:`predicate`
        :param kwargs: named arguments passed to :attr:`predicate`
        :type predicate: Callable[[bytes], bool], required
        """
        if not callable(predicate):
            raise ValueError("The predicate attribute must be a callable "
                             "expecting a single bytes attribute, not '{}'"
                             .format(type(predicate).__name__))
        return predicate(self.read(), *args, **kwargs)

    # Internal methods ##

    def __init__(self, _id=None, timeout=ChannelInterface.DEFAULT_TIMEOUT):
        super().__init__(timeout=timeout)
        self.id = uuid.uuid4() if _id is None else _id
        self._isOpened = False
        self.header = None  # A Symbol corresponding to the protocol header
        self.header_presets = {}  # A dict used to parameterize the header Symbol
        self.__writeCounter = 0
        self.__writeCounterMax = AbstractChannel.DEFAULT_WRITE_COUNTER_MAX

    def __enter__(self):
        """Enter the runtime channel context.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime channel context.
        """
        self.close()

    # Properties ##

    @property
    def isOpen(self):
        """
        Property (getter/setter).
        Returns ``True`` if the communication channel is open.

        :return: The status of the communication channel.
        :type: :class:`bool`
        """
        return self._isOpened

    @isOpen.setter
    @typeCheck(bool)
    def isOpen(self, isOpen):
        self._isOpened = isOpen

    @property
    def id(self):
        """
        Property (getter/setter).
        The unique identifier of the channel.

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("ID cannot be None")
        self.__id = _id


# Utilitary methods ##

class NetUtils(object):
    """A utilitary class that provides static methods to handle network
    address and interface resolutions.

    """

    @staticmethod
    def getRemoteMacAddress(remoteIP):
        """
        Retrieve remote MAC address from the remote IP address
        """
        dstMacAddr = arpreq.arpreq(remoteIP)
        if dstMacAddr is not None:
            dstMacAddr = dstMacAddr.replace(':', '')
            dstMacAddr = binascii.unhexlify(dstMacAddr)
        else:
            # Force ARP resolution
            p = subprocess.Popen(["/bin/ping", "-c1", remoteIP])
            p.wait()
            time.sleep(0.1)

            dstMacAddr = arpreq.arpreq(remoteIP)
            if dstMacAddr is not None:
                dstMacAddr = dstMacAddr.replace(':', '')
                dstMacAddr = binascii.unhexlify(dstMacAddr)
            else:
                raise Exception("Cannot resolve IP address to a MAC address for IP: '{}'".format(remoteIP))
        return dstMacAddr

    @staticmethod
    def getLocalMacAddress(interface):
        """
        Retrieve local MAC address from the network interface name
        """
        def get_interface_addr(ifname):
            s = socket.socket()
            response = ioctl(s,
                             0x8927,  # SIOCGIFADDR
                             struct.pack("16s16x", ifname))
            s.close()
            return struct.unpack("16xh6s8x", response)

        srcMacAddr = get_interface_addr(bytes(interface, 'utf-8'))[1]
        return srcMacAddr

    # Static methods used to retrieve local network interface
    # and local IP according to a remote IP

    @staticmethod
    def getLocalInterface(localIP):
        """
        Retrieve the network interface name associated with a specific IP
        address.

        :param localIP: the local IP address
        :type localIP: :class:`str`
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

        :param remoteIP: the remote IP address
        :type localIP: :class:`str`
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remoteIP, 53))
        localIPAddress = s.getsockname()[0]
        s.close()
        return localIPAddress
