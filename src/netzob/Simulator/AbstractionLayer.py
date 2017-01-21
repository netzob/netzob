#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
from netzob.Model.Vocabulary.Domain.Parser.MessageParser import MessageParser
from netzob.Model.Vocabulary.Domain.Parser.FlowParser import FlowParser
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Raw import Raw
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol
from netzob.Simulator.Channels.AbstractChannel import ChannelDownException



@NetzobLogger
class AbstractionLayer(object):
    """An abstraction layer specializes a symbol into a message before
    emitting it and on the other way, abstracts a received message
    into a symbol.

    >>> from netzob.all import *
    >>> symbol = Symbol([Field(b"Hello Zoby !")], name = "Symbol_Hello")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbol])
    >>> abstractionLayerOut.openChannel()
    >>> abstractionLayerOut.writeSymbol(symbol)
    >>> (receivedSymbol, receivedMessage) = abstractionLayerIn.readSymbol()
    >>> print(receivedSymbol.name)
    Symbol_Hello
    >>> print(receivedMessage)
    b'Hello Zoby !'

    The abstraction layer can also handle a message flow.

    >>> symbolflow = Symbol([Field(b"Hello Zoby !Whats up ?")], name = "Symbol Flow")
    >>> symbol1 = Symbol([Field(b"Hello Zoby !")], name = "Symbol_Hello")
    >>> symbol2 = Symbol([Field(b"Whats up ?")], name = "Symbol_WUP")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol1, symbol2])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbolflow])
    >>> abstractionLayerOut.openChannel()
    >>> abstractionLayerOut.writeSymbol(symbolflow)
    >>> (receivedSymbols, receivedMessage) = abstractionLayerIn.readSymbols()
    >>> print(receivedSymbols)
    [Symbol_Hello, Symbol_WUP]

    """

    def __init__(self, channel, symbols):
        self.channel = channel
        self.symbols = symbols
        self.memory = Memory()
        self.specializer = MessageSpecializer(memory = self.memory)
        self.parser = MessageParser(memory = self.memory)
        self.flow_parser = FlowParser(memory = self.memory)

    @typeCheck(Symbol)
    def writeSymbol(self, symbol):
        """Write the specified symbol on the communication channel
        after specializing it into a contextualized message.

        :param symbol: the symbol to write on the channel
        :type symbol: :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        :raise TypeError if parameter is not valid and Exception if an exception occurs.
        """
        if symbol is None:
            raise TypeError("The symbol to write on the channel cannot be None")

        self._logger.debug("Specializing symbol '{0}' (id={1}).".format(symbol.name, symbol.id))
        
        dataBin = self.specializer.specializeSymbol(symbol).generatedContent

        self.memory = self.specializer.memory
        self.parser.memory = self.memory
        data = TypeConverter.convert(dataBin, BitArray, Raw)

        self.channel.write(data)
        self._logger.debug("Writing to commnunication channel done..")                

    @typeCheck(int)
    def readSymbols(self, timeout=EmptySymbol.defaultReceptionTimeout()):
        """Read from the abstraction layer a flow and abstract it with one or more consecutive symbols
        
        The timeout parameter represents the amount of time (in millisecond) above which
        no reception of a message triggers the reception of an  :class:`netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`. If timeout set to None
        or to a negative value means it always wait for the reception of a message.

        :keyword timeout: the time above which no reception of message triggers the reception of an :class:`netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`
        :type timeout: :class:`int`
        :raise TypeError if the parameter is not valid and Exception if an error occurs.
        """

        self._logger.debug("Reading data from communication channel...")
        data = self.channel.read(timeout = timeout)
        self._logger.debug("Received : {}".format(repr(data)))

        symbols = []

        # if we read some bytes, we try to abstract them
        if len(data) > 0:
            try:
                symbols_and_data = self.flow_parser.parseFlow(RawMessage(data), self.symbols)
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
            symbols.append(UnknownSymbol(message = msg))

        return (symbols, data)
    

    @typeCheck(int)
    def readSymbol(self, timeout=EmptySymbol.defaultReceptionTimeout()):
        """Read from the abstraction layer a message and abstract it
        into a message.
        The timeout parameter represents the amount of time (in millisecond) above which
        no reception of a message triggers the reception of an  :class:`netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`. If timeout set to None
        or to a negative value means it always wait for the reception of a message.

        :keyword timeout: the time above which no reception of message triggers the reception of an :class:`netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`
        :type timeout: :class:`int`
        :raise TypeError if the parameter is not valid and Exception if an error occurs.
        """

        self._logger.debug("Reading data from communication channel...")
        data = self.channel.read(timeout = timeout)
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
            symbol = UnknownSymbol(message = msg)            
        elif symbol is None and len(data) == 0:
            symbol = EmptySymbol()

        return (symbol, data)

    def openChannel(self):
        self.channel.open()
        self._logger.debug("Communication channel opened.")

    def closeChannel(self):
        self.channel.close()
        self._logger.debug("Communication channel close.")

    def reset(self):
        self._logger.debug("Reseting abstraction layer")
        self.memory = Memory()
        self.specializer = MessageSpecializer(memory = self.memory)
        self.parser = MessageParser(memory = self.memory)
        self.flow_parser = FlowParser(memory = self.memory)
        

