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
import io
import sys
try:
    from typing import Callable, Union
except ImportError:
    pass

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Simulator.AbstractChannel import AbstractChannel
from netzob.Simulator.ChannelBuilder import ChannelBuilder


@NetzobLogger
class DebugChannel(AbstractChannel):
    """A DebugChannel is a file-like channel that handles writing of output
    data.

    The DebugChannel constructor expects some parameters:

    :param stream: The output stream
    :param timeout: The default timeout of the channel for global
                    connection. Default value is blocking (None).
    :type stream: :class:`str` or a file-like object, required
    :type timeout: :class:`float`, optional


    The following code shows the use of a DebugChannel channel:

    >>> from netzob.all import *
    >>> client = DebugChannel("/dev/null")
    >>> symbol = Symbol([Field("Hello everyone!")])
    >>> with client:
    ...     client.write(next(symbol.specialize()))
    18
    """

    STREAM_MAP = {
        "stdout": sys.stdout,
        "stderr": sys.stderr
    }

    @public_api
    @typeCheck((str, io.IOBase))
    def __init__(self,
                 stream,  # type: Union[str, io.IOBase]
                 timeout=AbstractChannel.DEFAULT_TIMEOUT
                 ):
        # type: (...) -> None
        super(DebugChannel, self).__init__(timeout=timeout)
        self._stream = self.STREAM_MAP.get(stream, stream)

    @staticmethod
    def getBuilder():
        return DebugChannelBuilder

    @public_api
    def open(self, timeout=5.):
        """Open the communication channel. If the channel is a client, it
        starts to connect to the specified server.

        :param timeout: The default timeout of the channel for opening
                        connection and waiting for a message. Default value
                        is 5.0 seconds. To specify no timeout, None value is
                        expected.
        :type timeout: :class:`float`, optional
        :raise: RuntimeError if the channel is already opened

        """

        super().open(timeout=timeout)
        if isinstance(self._stream, str):
            self._stream = open(self._stream, 'w')
        self.isOpen = True

    @public_api
    def close(self):
        """Close the communication channel."""
        if self.isOpen:
            self._stream.close()
        self.isOpen = False

    @public_api
    def read(self):
        """Do nothing
        """

    def writePacket(self, data):
        """Write on stream

        :param data: the data to write on the channel
        :type data: :class:`bytes`
        """
        return self._stream.write(repr(data))

    @public_api
    def sendReceive(self, data):
        """Write on the communication channel the specified data and returns
        the corresponding response.

        :param data: the data to write on the channel
        :type data: :class:`bytes`

        """
        self.write(data)
        return self.read()

    @public_api
    def checkReceived(self,
                      predicate,  # type: Callable[..., bool]
                      *args, **kwargs):
        # type: (...) -> bool
        """
        Method used to simulate the validation of an input data that could not
        be retrieved.

        :param predicate: the function used to validate the received data
        :type predicate: Callable[[bytes], bool]
        """
        return True

    def updateSocketTimeout(self):
        """Do nothing
        """

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
        if rate is not None:
            self._logger.info("Network rate limited to {:.2f} kBps".format(rate/1000))
        self._rate = rate

    @public_api
    def unset_rate(self):
        """This method clears the transmission rate.
        """
        if self._rate is not None:
            self._rate = None
            self._logger.info("Network rate limitation removed")


class DebugChannelBuilder(ChannelBuilder):
    """
    This builder is used to create an
    :class:`~netzob.Simulator.Channels.DebugChannel.DebugChannel` instance

    >>> from netzob.Simulator.Channels.NetInfo import NetInfo
    >>> builder = DebugChannelBuilder().set("stream", "stderr")
    >>> chan = builder.build()
    >>> type(chan)
    <class 'netzob.Simulator.Channels.DebugChannel.DebugChannel'>
    """

    @public_api
    def __init__(self):
        super().__init__(DebugChannel)

    def set_stream(self, stream):
        self.attrs['stream'] = stream
