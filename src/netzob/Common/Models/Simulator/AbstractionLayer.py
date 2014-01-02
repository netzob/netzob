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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField


@NetzobLogger
class AbstractionLayer(object):
    """An abstraction layer specializes a symbol into a message before
    emitting it and on the other way, abstracts a received message
    into a symbol.

    >>> from netzob.all import *
    >>> symbol = Symbol([Field("Hello Zoby !")], name = "Symbol_Hello")

    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol])
    >>> abstractionLayerIn.openChannel()

    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbol])
    >>> abstractionLayerOut.openChannel()

    >>> abstractionLayerOut.writeSymbol(symbol)
    >>> (receivedSymbol, receivedMessage) = abstractionLayerIn.readSymbol()
    >>> print receivedSymbol.name
    Symbol_Hello
    >>> print receivedMessage
    Hello Zoby !

    """

    def __init__(self, channel, symbols):
        self.channel = channel
        self.symbols = symbols

    @typeCheck(Symbol)
    def writeSymbol(self, symbol):
        """Write the specified symbol on the communication channel
        after specializing it into a contextualized message.

        :param symbol: the symbol to write on the channel
        :type symbol: :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raise TypeError if parameter is not valid and Exception if an exception occurs.
        """
        if symbol is None:
            raise TypeError("The symbol to write on the channel cannot be None")

        self._logger.info("Going to specialize symbol: '{0}' (id={1}).".format(symbol.name, symbol.id))
        data = symbol.specialize()
        self._logger.info("Data generated from symbol '{0}': {1}.".format(symbol.name, repr(data)))

        self._logger.info("Going to write to communication channel...")
        self.channel.write(data)
        self._logger.info("Writing to commnunication channel donne..")

    @typeCheck(int)
    def readSymbol(self, timeout=EmptySymbol.defaultReceptionTimeout()):
        """Read from the abstraction layer a message and abstract it
        into a message.
        The timeout parameter represents the amount of time (in millisecond) above which
        no reception of a message triggers the reception of an  :class:`netzob.Common.Models.Vocabulary.EmptySymbol.EmptySymbol`. If timeout set to None
        or to a negative value means it always wait for the reception of a message.

        :keyword timeout: the time above which no reception of message triggers the reception of an :class:`netzob.Common.Models.Vocabulary.EmptySymbol.EmptySymbol`
        :type timeout: :class:`int`
        :raise TypeError if the parameter is not valid and Exception if an error occurs.
        """
        self._logger.info("Going to read from communication channel...")
        data = self.channel.read()
        self._logger.info("Received data: '{0}'".format(repr(data)))

        symbol = AbstractField.abstract(data, self.symbols)
        if symbol is not None:
            self._logger.info("Received symbol on communication channel: '{0}'".format(symbol.name))
        else:
            self._logger.info("Received symbol on communication channel: '{0}'".format(symbol))

        return (symbol, data)

    def openChannel(self):
        self._logger.info("Going to open the communication channel...")
        self.channel.open()
        self._logger.info("Communication channel opened.")

    def closeChannel(self):
        self._logger.info("Going to close the communication channel...")
        self.channel.close()
        self._logger.info("Communication channel close.")
