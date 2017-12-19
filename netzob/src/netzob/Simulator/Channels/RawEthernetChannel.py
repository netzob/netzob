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
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import socket
import binascii
from bitarray import bitarray

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
class RawEthernetChannel(AbstractChannel):
    r"""A RawEthernetChannel is a communication channel to send Raw Ethernet
    frames.

    The RawEthernetChannel constructor expects some parameters:

    :param interface: The local network interface name (such as 'eth0', 'lo').
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type interface: :class:`str`, required
    :type timeout: :class:`float`, optional

    .. todo:: add support of netaddr.EUI

    Adding to AbstractChannel variables, the RawEthernetChannel class provides
    the following public variables:

    :var interface: The network Interface name such as 'eth0', 'lo', determined
                    with the local MAC address. Read only variable.
    :vartype interface: :class:`str`


    >>> from netzob.all import *
    >>> from binascii import hexlify
    >>> client = RawEthernetChannel(interface="lo")
    >>> client.open()
    >>> symbol = Symbol([Field("ABC")])
    >>> client.write(symbol.specialize())
    17
    >>> client.close()

    """

    ## Class attributes ##

    ETH_P_ALL = 3
    FAMILIES = ["ethernet"]

    @typeCheck(str, str)
    def __init__(self,
                 interface,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(RawEthernetChannel, self).__init__(timeout=timeout)
        self.__interface = interface

    @staticmethod
    def getBuilder():
        return RawEthernetChannelBuilder

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

        self._socket = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.htons(RawEthernetChannel.ETH_P_ALL))
        self._socket.settimeout(timeout or self.timeout)
        self._socket.bind((self.interface, RawEthernetChannel.ETH_P_ALL))

        self.isOpen = True

    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    def read(self):
        """Read the next message on the communication channel.
        """
        if self._socket is not None:
            (data, _) = self._socket.recvfrom(65535)
            return data
        else:
            raise Exception("socket is not available")

    def sendReceive(self, data):
        """Write on the communication channel and returns the next packet
        coming from the destination address.

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """
        if self._socket is not None:

            targetHW = data[0:6]
            self.write(data)
            while True:
                (data, _) = self._socket.recvfrom(65535)
                if data[6:12] == targetHW:
                    return data
        else:
            raise Exception("socket is not available")

    def write(self, data, rate=None, duration=None):
        """Write to the communication channel the specified data.

        :param data: The data to write on the channel.
        :param rate: This specifies the bandwidth in octets to respect during
                     traffic emission (should be used with duration=parameter).
        :param duration: This tells how much seconds the symbol is continuously
                         written on the channel.
        :type data: :class:`bytes`, required
        :type rate: :class:`int`, optional
        :type duration: :class:`int`, optional
        :return: The amount of written data, in bytes.
        :rtype: :class:`int`
        """
        return super().write(data, rate=rate, duration=duration)

    def writePacket(self, data):
        """Write on the communication channel the specified data

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """

        if self._socket is None:
            raise Exception("socket is not available")

        len_data = self._socket.sendto(
            data, (self.interface,
                   RawEthernetChannel.ETH_P_ALL))
        return len_data

    # Properties

    @property
    def interface(self):
        """Local network interface name (such as 'eth0', 'lo').

        :type: :class:`str`
        """
        return self.__interface


class RawEthernetChannelBuilder(ChannelBuilder):
    """
    This builder is used to create a
    :class:`~netzob.Simulator.Channel.RawEthernetChannel.RawEthernetChannel`
    instance.

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(interface="eth0")
    >>> chan = RawEthernetChannelBuilder().set_map(netinfo.getDict()).build()
    >>> assert isinstance(chan, RawEthernetChannel)
    """

    def __init__(self):
        super().__init__(RawEthernetChannel)

    def set_interface(self, value):
        self.attrs['interface'] = value
