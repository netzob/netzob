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
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
from netzob.Model.Vocabulary.Domain.Parser.MessageParser import MessageParser
from netzob.Model.Vocabulary.Domain.Parser.FlowParser import FlowParser
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol


@NetzobLogger
class AbstractionLayer(object):
    """An abstraction layer specializes a symbol into a message before
    emitting it and, on the other way, abstracts a received message
    into a symbol.

    The AbstractionLayer constructor expects some parameters:

    :param channel: The underlying communication channel (such as IPClient, UDPClient...).
    :param symbols: The list of permitted symbols during translation from/to concrete messages.
    :param memory: A memory object use to make persistent specific variables.
    :type channel: :class:`AbstractChannel <netzob.Model.Simuator.Channels.AbstractChannel.AbstractChannel>`, required
    :type symbols: :class:`Symbol <netzob.Model.Vocabular.Symbol.Symbol>`, required
    :type memory: :class:`Memory <netzob.Model.Vocabular.Domain.Variables.Memory.Memory>`, optional


    The following code shows a usage of the abstraction layer class,
    where two UDP channels (client and server) are built and transport
    just one permitted symbol:

    >>> from netzob.all import *
    >>> symbol = Symbol([Field(b"Hello Kurt !")], name = "Symbol_Hello")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbol])
    >>> abstractionLayerOut.openChannel()
    >>> abstractionLayerOut.writeSymbol(symbol)
    12
    >>> (receivedSymbol, receivedMessage) = abstractionLayerIn.readSymbol()
    >>> print(receivedSymbol.name)
    Symbol_Hello
    >>> print(receivedMessage)
    b'Hello Kurt !'


    The following example demonstrates that the abstraction layer can
    also handle a message flow:

    >>> symbolflow = Symbol([Field(b"Hello Kurt !Whats up ?")], name = "Symbol Flow")
    >>> symbol1 = Symbol([Field(b"Hello Kurt !")], name = "Symbol_Hello")
    >>> symbol2 = Symbol([Field(b"Whats up ?")], name = "Symbol_WUP")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol1, symbol2])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbolflow])
    >>> abstractionLayerOut.openChannel()
    >>> abstractionLayerOut.writeSymbol(symbolflow)
    22
    >>> (receivedSymbols, receivedMessage) = abstractionLayerIn.readSymbols()
    >>> print(receivedSymbols)
    [Symbol_Hello, Symbol_WUP]

    """

    def __init__(self, channel, symbols, memory=None):
        self.channel = channel
        self.symbols = symbols
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory
        self.specializer = MessageSpecializer(memory=self.memory)
        self.parser = MessageParser(memory=self.memory)
        self.flow_parser = FlowParser(memory=self.memory)

    @typeCheck(Symbol)
    def writeSymbol(self, symbol, rate=None, duration=None, presets=None):
        """Write the specified symbol on the communication channel
        after specializing it into a contextualized message.

        :param symbol: The symbol to write on the channel.
        :param rate: This specifies the bandwidth in octets to respect
                     during traffic emission (should be used with
                     duration= parameter). Default value is None (no
                     rate).
        :param duration: This tells how much seconds the symbol is
                         continuously written on the channel. Default
                         value is None (write only once).
        :param presets: This specifies how to parameterize the emitted
                        symbol. The expected content of this dict is
                        specified in :meth:`Symbol.specialize \
                        <netzob.Model.Vocabulary.Symbol.Symbol.specialize>`.
        :type symbol: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`, required
        :type rate: :class:`int`, optional
        :type duration: :class:`int`, optional
        :type presets: :class:`dict`, optional
        :raise: :class:`TypeError` if parameter is not valid and Exception if an exception occurs.

        """

        if symbol is None:
            raise TypeError(
                "The symbol to write on the channel cannot be None")

        len_data = 0
        if duration is None:
            len_data = self._writeSymbol(symbol, presets=presets)
        else:

            t_start = time.time()
            t_elapsed = 0
            t_delta = 0
            while True:

                t_elapsed = time.time() - t_start
                if t_elapsed > duration:
                    break

                # Specialize the symbol and send it over the channel
                len_data += self._writeSymbol(symbol, presets=presets)

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

    def _writeSymbol(self, symbol, presets=None):
        """Write the specified symbol on the communication channel after
        specializing it into a contextualized message.

        :param symbol: The symbol to write on the channel.
        :param presets: This specifies how to parameterize the emitted symbol.
        :type symbol: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        :type presets: :clasl:`dict`
        :raise: :class:`TypeError` if parameter is not valid and Exception if an exception occurs.

        """

        self._logger.debug("Specializing symbol '{0}' (id={1}).".format(
            symbol.name, symbol.id))

        self.specializer.presets = presets
        dataBin = self.specializer.specializeSymbol(symbol).generatedContent
        self.specializer.presets = None

        self.memory = self.specializer.memory
        self.parser.memory = self.memory
        data = TypeConverter.convert(dataBin, BitArray, Raw)

        len_data = self.channel.write(data)
        self._logger.debug("Writing {} octets to commnunication channel done..".format(len_data))
        return len_data

    @typeCheck(int)
    def readSymbols(self):
        """Read a flow from the abstraction layer and abstract it in one or
        more consecutive symbols.

        The timeout attribute of the underlying channel is important
        as it represents the amount of time (in seconds) above which
        no reception of a message triggers the reception of an
        :class:`EmptySymbol
        <netzob.Model.Vocabulary.EmptySymbol.EmptySymbol>`.

        """

        self._logger.debug("Reading data from communication channel...")
        data = self.channel.read()
        self._logger.debug("Received : {}".format(repr(data)))

        symbols = []

        # if we read some bytes, we try to abstract them
        if len(data) > 0:
            try:
                symbols_and_data = self.flow_parser.parseFlow(
                    RawMessage(data), self.symbols)
                for (symbol, alignment) in symbols_and_data:
                    symbols.append(symbol)
            except Exception as e:
                self._logger.error(e)

            if len(symbols) > 0:
                self.memory = self.flow_parser.memory
                self.specializer.memory = self.memory
        else:
            symbols.append(EmptySymbol())

        if len(symbols) == 0 and len(data) > 0:
            msg = RawMessage(data)
            symbols.append(UnknownSymbol(message=msg))

        return (symbols, data)

    @typeCheck(int)
    def readSymbol(self):
        """Read a message from the abstraction layer and abstract it
        into a symbol.

        The timeout attribute of the underlying channel is important
        as it represents the amount of time (in seconds) above which
        no reception of a message triggers the reception of an
        :class:`EmptySymbol
        <netzob.Model.Vocabulary.EmptySymbol.EmptySymbol>`.
        """

        self._logger.debug("Reading data from communication channel...")
        data = self.channel.read()
        self._logger.debug("Received : {}".format(repr(data)))

        symbol = None

        # if we read some bytes, we try to abstract them
        if len(data) > 0:
            for potential in self.symbols:
                try:
                    self.parser.parseMessage(RawMessage(data), potential)
                    symbol = potential
                    self.memory = self.parser.memory
                    self.specializer.memory = self.memory
                    break
                except Exception:
                    symbol = None

        if symbol is None and len(data) > 0:
            msg = RawMessage(data)
            symbol = UnknownSymbol(message=msg)
        elif symbol is None and len(data) == 0:
            symbol = EmptySymbol()

        return (symbol, data)

    def openChannel(self):
        """Open the underlying communication channel.

        """

        self.channel.open()
        self._logger.debug("Communication channel opened.")

    def closeChannel(self):
        """Close the underlying communication channel.

        """

        self.channel.close()
        self._logger.debug("Communication channel close.")

    def reset(self):
        """Reset the abstraction layer (i.e. its internal memory as well as the internal parsers).

        """

        self._logger.debug("Reseting abstraction layer")
        self.memory = Memory()
        self.specializer = MessageSpecializer(memory=self.memory)
        self.parser = MessageParser(memory=self.memory)
        self.flow_parser = FlowParser(memory=self.memory)
