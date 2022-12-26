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
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Simulator.AbstractChannel import AbstractChannel, NetUtils
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
    >>> symbol = Symbol([Field(Raw(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00"))])
    >>> client.write(next(symbol.specialize()))
    14
    >>> client.close()

    """

    ## Class attributes ##

    ETH_P_ALL = 3
    FAMILIES = ["ethernet"]

    @public_api
    @typeCheck(str, str)
    def __init__(self,
                 interface,
                 timeout=AbstractChannel.DEFAULT_TIMEOUT):
        super(RawEthernetChannel, self).__init__(timeout=timeout)
        self.__interface = interface

    @staticmethod
    def getBuilder():
        return RawEthernetChannelBuilder

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

        self._socket = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.htons(RawEthernetChannel.ETH_P_ALL))
        self._socket.settimeout(timeout or self.timeout)
        self._socket.bind((self.interface, RawEthernetChannel.ETH_P_ALL))

        self.isOpen = True

    @public_api
    def close(self):
        """Close the communication channel."""
        if self._socket is not None:
            self._socket.close()
        self.isOpen = False

    @public_api
    def read(self):
        """Read the next message on the communication channel.
        """
        if self._socket is not None:
            (data, _) = self._socket.recvfrom(65535)
            return data
        else:
            raise Exception("socket is not available")

    @public_api
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

    def writePacket(self, data):
        """Write on the communication channel the specified data

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """

        if self._socket is None:
            raise Exception("socket is not available")

        try:
            len_data = self._socket.sendto(
                data, (self.interface,
                       RawEthernetChannel.ETH_P_ALL))
        except OSError as e:
            self._logger.warning("OSError durring socket.sendto(): '{}'. Trying a second time after sleeping 1s...".format(e))
            time.sleep(1)
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
        NetUtils.set_rate(self.interface, rate)
        if rate is not None:
            self._logger.info("Network rate limited to {:.2f} kBps ({} kbps) on {} interface".format(rate/1000, rate*8/1000, self.interface))
        self._rate = rate
        self._logger.info("tc status on {} interface: {}".format(self.interface, NetUtils.get_rate(self.interface)))

    @public_api
    def unset_rate(self):
        """This method clears the transmission rate.
        """
        if self._rate is not None:
            NetUtils.set_rate(self.interface, None)
            self._rate = None
            self._logger.info("Network rate limitation removed on {} interface".format(self.interface))
        self._logger.info("tc status on {} interface: {}".format(self.interface, NetUtils.get_rate(self.interface)))


class RawEthernetChannelBuilder(ChannelBuilder):
    """
    This builder is used to create a
    :class:`~netzob.Simulator.Channels.RawEthernetChannel.RawEthernetChannel`
    instance.

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> netinfo = NetInfo(interface="eth0")
    >>> builder = RawEthernetChannelBuilder().set_map(netinfo.getDict())
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.RawEthernetChannel.RawEthernetChannel'>
    >>> chan.interface  # interface key has been mapped to interface attribute
    'eth0'
    """

    @public_api
    def __init__(self):
        super().__init__(RawEthernetChannel)

    def set_interface(self, value):
        self.attrs['interface'] = value
