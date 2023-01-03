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
import socket
from collections import OrderedDict
from queue import Queue, Empty
from enum import Enum
#from multiprocessing import Queue

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
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol
from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment


class SymbolBadSettingsException(Exception):
    pass


class Operation(Enum):
    """Tells the direction of the symbol on the communication channel.

    """
    ABSTRACT = 'abstract'
    """Indicates that the symbol has been abstracted from a concrete representation."""
    SPECIALIZE = 'specialize'
    """Indicates that the symbol has been specialized into a concrete representation."""
    __repr__ = Enum.__str__


@NetzobLogger
class AbstractionLayer(object):
    """An abstraction layer specializes a symbol into a message before
    emitting it and, on the other way, abstracts a received message
    into a symbol.

    The AbstractionLayer constructor expects some parameters:

    :param channel: This parameter is the underlying communication channel (such as IPChannel,
                    UDPClient...).
    :param symbols: This parameter is the list of permitted symbols during translation from/to
                    concrete messages.
    :param actor: An actor that will visit the associated automaton and provide a dedicated memory context.
    :type channel: :class:`AbstractChannel <netzob.Model.Simulator.AbstractChannel.AbstractChannel>`, required
    :type symbols: a :class:`list` of :class:`Symbol <netzob.Model.Vocabular.Symbol.Symbol>`, required
    :type actor: :class:`Actor <netzob.Simulator.Actor.Actor>`, optional


    The AbstractionLayer class provides the following public variables:

    :var channel: The underlying communication channel (such as IPChannel,
                  UDPClient...).
    :var symbols: The list of permitted symbols during translation from/to
                  concrete messages.
    :var actor: An actor that will visit the associated automaton and provide a dedicated memory context.
    :vartype channel: :class:`AbstractChannel <netzob.Model.Simulator.AbstractChannel.AbstractChannel>`
    :vartype symbols: a :class:`list` of :class:`Symbol <netzob.Model.Vocabular.Symbol.Symbol>`
    :vartype actor: :class:`Actor <netzob.Simulator.Actor.Actor>`


    **Usage example of the abstraction layer**

    The following code shows a usage of the abstraction layer class,
    where two UDP channels (client and server) are built and transport
    just one permitted symbol:

    >>> from netzob.all import *
    >>> symbol = Symbol([Field(b"Hello Kurt !")], name = "Symbol_Hello")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889, timeout=1.)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889, timeout=1.)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbol])
    >>> abstractionLayerOut.openChannel()
    >>> (data, data_len, data_structure) = abstractionLayerOut.writeSymbol(symbol)
    >>> data_len
    12
    >>> (received_symbol, received_data, received_structure) = abstractionLayerIn.readSymbol()
    >>> received_symbol.name
    'Symbol_Hello'
    >>> received_data
    b'Hello Kurt !'


    **Handling message flow within the abstraction layer**

    The following example demonstrates that the abstraction layer can
    also handle a message flow:

    >>> from netzob.all import *
    >>> symbolflow = Symbol([Field(b"Hello Kurt !Whats up ?")], name = "Symbol Flow")
    >>> symbol1 = Symbol([Field(b"Hello Kurt !")], name = "Symbol_Hello")
    >>> symbol2 = Symbol([Field(b"Whats up ?")], name = "Symbol_WUP")
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889, timeout=1.)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol1, symbol2])
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889, timeout=1.)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbolflow])
    >>> abstractionLayerOut.openChannel()
    >>> (data, data_len, data_structure) = abstractionLayerOut.writeSymbol(symbolflow)
    >>> data_len
    22
    >>> (received_symbols, received_data) = abstractionLayerIn.readSymbols()
    >>> received_symbols
    [Symbol_Hello, Symbol_WUP]


    **Relationships between the environment and the produced messages**

    The following example shows how to define a relationship between a
    message to send and an environment variable, then how to leverage this
    relationship when using the abstraction layer.

    >>> from netzob.all import *
    >>> # Environment variable definition
    >>> memory1 = Memory()
    >>> env1 = Data(String(), name="env1")
    >>> memory1.memorize(env1, String("John").value)
    >>>
    >>> # Symbol definition
    >>> f7 = Field(domain=String("master"), name="F7")
    >>> f8 = Field(domain=String(">"), name="F8")
    >>> f9 = Field(domain=Value(env1), name="F9")
    >>> symbol = Symbol(fields=[f7, f8, f9], name="Symbol_Hello")
    >>>
    >>> # Creation of channels with dedicated abstraction layer
    >>> channelIn = UDPServer(localIP="127.0.0.1", localPort=8889, timeout=1.)
    >>> abstractionLayerIn = AbstractionLayer(channelIn, [symbol])
    >>> abstractionLayerIn.memory = memory1
    >>> abstractionLayerIn.openChannel()
    >>> channelOut = UDPClient(remoteIP="127.0.0.1", remotePort=8889, timeout=1.)
    >>> abstractionLayerOut = AbstractionLayer(channelOut, [symbol])
    >>> abstractionLayerOut.memory = memory1
    >>> abstractionLayerOut.openChannel()
    >>>
    >>> # Sending of a symbol containing a data coming from the environment
    >>> (data, data_len, data_structure) = abstractionLayerOut.writeSymbol(symbol)
    >>> data_len
    11
    >>> (received_symbol, received_data, received_structure) = abstractionLayerIn.readSymbol()
    >>> received_symbol.name
    'Symbol_Hello'
    >>> received_data
    b'master>John'

    """

    def __init__(self, channel, symbols, actor=None):

        # Initialize public variables from parameters
        self.channel = channel
        self.symbols = symbols
        self.actor = actor

        # Initialize local private variables
        self.__specializer = None
        self.__parser = None
        self.__flow_parser = None
        if self.actor is None:
            self.memory = Memory()  # self.memory expects specializer, parser and flow_parser to be initialized
        self.__specializer = MessageSpecializer(memory=self.memory)
        self.__parser = MessageParser(memory=self.memory)
        self.__flow_parser = FlowParser(memory=self.memory)
        self.__queue_input = Queue()

        # Initialize local variables
        # Variables used to keep track of the last sent and received symbols and associated messages
        self.last_sent_symbol = None
        self.last_sent_message = None
        self.last_sent_structure = None
        self.last_received_symbol = None
        self.last_received_message = None
        self.last_received_structure = None

    @typeCheck(Symbol)
    def writeSymbol(self, symbol, rate=None, duration=None, preset=None, cbk_action=None):
        """Write the specified symbol on the communication channel
        after specializing it into a contextualized message.

        :param symbol: The symbol to write on the channel.
        :param rate: This specifies the bandwidth in octets to respect
                     during traffic emission (should be used with
                     :attr:`duration` parameter). Default value is None (no
                     rate).
        :param duration: This indicates for how many seconds the symbol is
                         continuously written on the channel. Default
                         value is None (write only once).
        :param preset: A preset configuration used during the specialization process. Values
                       in this configuration will override any field
                       definition, constraints or relationship dependencies. See
                       :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
                       for a complete explanation of its usage.
                       Default is None.
        :type symbol: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`, required
        :type rate: :class:`int`, optional
        :type duration: :class:`int`, optional
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :raise: :class:`TypeError` if a parameter is not valid and :class:`Exception` if an exception occurs.

        """

        if cbk_action is None:
            cbk_action = []

        if symbol is None:
            raise TypeError("The symbol to write on the channel cannot be None")

        data = b''
        data_len = 0
        data_structure = {}
        if duration is None:
            (data, data_len, data_structure) = self._writeSymbol(symbol, preset=preset, cbk_action=cbk_action)
        else:

            t_start = time.time()
            t_elapsed = 0
            t_delta = 0
            while True:

                t_elapsed = time.time() - t_start
                if t_elapsed > duration:
                    break

                # Specialize the symbol and send it over the channel
                (data, data_len_tmp, data_structure) = self._writeSymbol(symbol, preset=preset, cbk_action=cbk_action)
                data_len += data_len_tmp

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

                        if (data_len / t_elapsed) > rate:
                            time.sleep(0.001)
                        else:
                            break

                # Show some log every seconds
                if t_delta > 1:
                    t_delta = 0
                    if rate is None:
                        self._logger.debug("Current rate: {} ko/s, sent data: {} ko, nb seconds elapsed: {}".format(round((data_len / t_elapsed) / 1024, 2),
                                                                                                                    round(data_len / 1024, 2),
                                                                                                                    round(t_elapsed, 2)))
                    else:
                        self._logger.debug("Rate rule: {} ko/s, current rate: {} ko/s, sent data: {} ko, nb seconds elapsed: {}".format(round(rate / 1024, 2),
                                                                                                                                        round((data_len / t_elapsed) / 1024, 2),
                                                                                                                                        round(data_len / 1024, 2),
                                                                                                                                        round(t_elapsed, 2)))
        return (data, data_len, data_structure)

    def _writeSymbol(self, symbol, preset=None, cbk_action=None):
        if cbk_action is None:
            cbk_action = []

        data_len = 0
        if isinstance(symbol, EmptySymbol):
            self._logger.debug("Symbol to write is an EmptySymbol. So nothing to do.".format(symbol.name))
            return (b'', data_len, OrderedDict())

        self._logger.debug("Specializing symbol '{0}' (id={1}).".format(symbol.name, id(symbol)))

        self.__specializer.preset = preset
        path = next(self.__specializer.specializeSymbol(symbol))

        data = path.generatedContent.tobytes()

        # Build data structure (i.e. a dict containing data content for each field)
        data_structure = OrderedDict()
        for field in symbol.getLeafFields():
            if path.hasData(field.domain):
                field_data = path.getData(field.domain).tobytes()
            else:
                field_data = b''
            data_structure[field.name] = field_data

        self.__specializer.preset = None  # This is needed, in order to avoid applying the preset configuration on an already preseted symbol

        self.memory = self.__specializer.memory
        self.__parser.memory = self.memory

        self._logger.debug("Writing the following data to the commnunication channel: '{}'".format(data))
        self._logger.debug("Writing the following symbol to the commnunication channel: '{}'".format(symbol.name))

        try:
            data_len = self.channel.write(data)
        except socket.timeout:
            self._logger.debug("Timeout on channel.write(...)")
            raise
        except Exception as e:
            self._logger.debug("Exception on channel.write(...): '{}'".format(e))
            raise

        self.last_sent_symbol = symbol
        self.last_sent_message = data
        self.last_sent_structure = data_structure

        for cbk in cbk_action:
            self._logger.debug("[actor='{}'] A callback function is defined for the write symbol event".format(self.actor))
            cbk(symbol, data, data_structure, Operation.SPECIALIZE, self.actor.current_state, self.actor.memory)

        return (data, data_len, data_structure)

    def is_data_interesting(self, data):
        """Tells if the current abstraction layer is concerned by the given data."""
        if self.actor is not None and self.actor.cbk_select_data is not None:
            return self.actor.cbk_select_data(data)
        else:
            return True

    def readSymbols(self):
        """Read a flow from the abstraction layer and abstract it in one or
        more consecutive symbols.

        The timeout attribute of the underlying channel is important
        as it represents the amount of time (in seconds) above which
        no receipt of a message triggers the receipt of an
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
                symbols_and_data = self.__flow_parser.parseFlow(
                    RawMessage(data), self.symbols)
                for (symbol, alignment) in symbols_and_data:
                    symbols.append(symbol)
            except Exception as e:
                self._logger.error(e)

            if len(symbols) > 0:
                self.memory = self.__flow_parser.memory
                self.__specializer.memory = self.memory
        else:
            symbols.append(EmptySymbol())

        if len(symbols) == 0 and len(data) > 0:
            msg = RawMessage(data)
            symbols.append(UnknownSymbol(message=msg))

        return (symbols, data)

    def readSymbol(self, symbols_preset=None, timeout=5.0):
        """Read a message from the abstraction layer and abstract it
        into a symbol.

        The timeout attribute of the underlying channel is important
        as it represents the amount of time (in seconds) above which
        no receipt of a message triggers the receipt of an
        :class:`EmptySymbol
        <netzob.Model.Vocabulary.EmptySymbol.EmptySymbol>`.
        """

        self._logger.debug("Reading data from communication channel...")

        data = b""
        try:
            if self.channel.threaded_mode:
                elapsed_time = 0
                while True:
                    if self.actor is not None and not self.actor.isActive() and not self.actor.keep_open:
                        self._logger.debug("Actor is not active, so we break the abstraction layer readSymbol() loop")
                        from netzob.Simulator.Actor import ActorStopException
                        raise ActorStopException()
                    if not self.queue_input.empty():
                        self._logger.debug("Poping data from input queue")
                        data = self.queue_input.get()
                        self.queue_input.task_done()
                        break
                    time.sleep(0.1)
                    elapsed_time += 0.1
                    if elapsed_time > timeout:
                        self._logger.debug("Timeout during symbol read")
                        raise socket.timeout("timed out")
            else:
                data = self.channel.read()
        except Empty:
            self._logger.debug("Error on queue_input poping")
            raise
        except socket.timeout:
            self._logger.debug("Timeout on channel.read()")
            raise
        except Exception as e:
            self._logger.debug("Exception on channel.read(): '{}'".format(e))
            raise

        self._logger.debug("Received: {}".format(repr(data)))

        symbol = None
        data_structure = {}

        # if we read some bytes, we try to abstract them in a symbol
        if len(data) > 0:
            for potentialSymbol in self.symbols:
                try:
                    aligned_data = DataAlignment.align([data], potentialSymbol, encoded=False, messageParser=self.__parser)

                    symbol = potentialSymbol
                    self.memory = self.__parser.memory
                    self.__specializer.memory = self.memory
                    break
                except Exception as e:
                    self._logger.debug(e)

        # Build data structure (i.e. a dict containing data content for each field)
        if symbol is not None:
            data_structure = OrderedDict()
            for fields_value in aligned_data:
                for i, field_value in enumerate(fields_value):
                    data_structure[aligned_data.headers[i]] = field_value

        if symbol is None and len(data) > 0:
            msg = RawMessage(data)
            symbol = UnknownSymbol(message=msg)
        elif symbol is None and len(data) == 0:
            symbol = EmptySymbol()

        self.last_received_symbol = symbol
        self.last_received_message = data
        self.last_received_structure = data_structure

        self._logger.debug("Receiving the following data from the commnunication channel: '{}'".format(data))
        self._logger.debug("Receiving the following symbol from the commnunication channel: '{}'".format(symbol.name))

        return (symbol, data, data_structure)

    def check_received(self):
        r"""Check is a message has been received on the underlying
        communicaton channel and which concerns the current actor.

        """
        if self.channel is not None and self.channel.threaded_mode:
            if not self.queue_input.empty():
                self._logger.debug("Input queue contains messages")
                return True
        return False

    def openChannel(self):
        """Open the underlying communication channel.

        """

        if self.channel.threaded_mode:
            # The channel should be already open
            self.channel.register_abstraction_layer(self)
            self._logger.debug("Registering current abstraction layer on underlying communication channel.")
        else:
            self.channel.open()
            self._logger.debug("Communication channel opened.")

    def closeChannel(self):
        """Close the underlying communication channel.

        """

        if self.channel.threaded_mode:
            # The channel will be close later
            self.channel.unregister_abstraction_layer(self)
            self._logger.debug("Unregistering current abstraction layer from underlying communication channel.")
        else:
            self.channel.close()
            self._logger.debug("Communication channel close.")

    def reset(self):
        """Reset the abstraction layer (i.e. its internal memory as well as the internal parsers).

        """

        self._logger.debug("Reseting abstraction layer")
        self.memory = Memory()
        self.__specializer = MessageSpecializer(memory=self.memory)
        self.__parser = MessageParser(memory=self.memory)
        self.__flow_parser = FlowParser(memory=self.memory)

    @property
    def queue_input(self):
        return self.__queue_input

    @queue_input.setter  # type: ignore
    def queue_input(self, queue_input):
        self.__queue_input = queue_input

    @property
    def memory(self):
        if self.actor is not None:
            return self.actor.memory
        else:
            return self.__memory

    @memory.setter  # type: ignore
    def memory(self, memory):
        if self.actor is not None:
            self.actor.memory = memory
        else:
            self.__memory = memory

        # Update other instance variables
        if self.__specializer is not None:
            self.__specializer.memory = self.memory
        if self.__parser is not None:
            self.__parser.memory = self.memory
        if self.__flow_parser is not None:
            self.__flow_parser.memory = self.memory


def _test():
    r"""
    >>> from netzob.all import *
    >>> channel = IPChannel(remoteIP="127.0.0.1")
    >>> automata = Automata(State(), [Symbol()])
    >>> actor_c = Actor(automata, channel=channel)
    >>> actor_d = Actor(automata, channel=channel)
    >>>
    >>> # Verify that similar actors have the same channel
    >>> id(actor_d.abstractionLayer.channel) == id(actor_c.abstractionLayer.channel)
    True
    >>>
    >>> # Verify that similar actors have different abstraction layers
    >>> id(actor_d.abstractionLayer) != id(actor_c.abstractionLayer)
    True
    >>>
    """
