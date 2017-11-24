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
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Grammar.Automata import Automata
from netzob.Simulator.AbstractionLayer import AbstractionLayer


@NetzobLogger
class Actor(threading.Thread):
    r"""An actor is an instance of a traffic generator which, given a
    grammar and a vocabulary, can visit the underlying automaton, and
    generate and parse messages from a specified abstraction layer.

    The Actor constructor expects some parameters:

    :param automata: The automaton the actor will visit.
    :param abstractionLayer: The underlying abstraction layer used to abstract
                             and specialize symbols.
    :param initiator: If True, indicates that the actor is a client, and thus initiates the
                      communication and emits the input symbol.  If
                      False, indicates that the actor is a server, and is thus waiting for
                      another peer to initiate the connection. Default
                      value is :const:`True`. The value can be changed
                      during a communication, in order to reverse the
                      way the actors communicate together.
    :param name: The name of the actor.
    :type automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`,
                    required
    :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`, required
    :type initiator: :class:`bool`, optional
    :type name: :class:`str`, optional


    The Actor class provides the following public variables:

    :var automata: The automaton the actor will visit.
    :var abstractionLayer: The underlying abstraction layer used to abstract
                           and specialize symbols.
    :var initiator: If True, indicates that the actor initiates the
                    communication and emits the input symbol.
                    If False, indicates that the actor is waiting for another
                    peer to initiate the connection. Default value is
                    :const:`True`. The value can be changed
                    during a communication, in order to reverse the
                    way the actors communicate together.
    :var name: The name of the actor. Default value is 'Actor'.
    :vartype automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`
    :vartype abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
    :vartype initiator: :class:`bool`
    :vartype name: :class:`str`


    **Example with a common automaton for a client and a server**

    For instance, we can create two very simple network Actors which
    communicate together through a TCP channel and exchange their
    names until one stops.

    The two actors are Alice and Bob. Bob is the initiator of the
    communication, meaning he sends the input symbols, while Alice
    answers with the output symbols of the grammar. The grammar is
    very simple: we first open the channel, and allow Bob to send
    ``"Bob> hello"``. At each received message, Alice answers
    ``"Alice> hello"``.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field("bob>hello")])
    >>> symbolList = [aliceSymbol, bobSymbol]
    >>>
    >>> # Create the grammar
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> mainTransition = Transition(startState=s1, endState=s1,
    ...                             inputSymbol=aliceSymbol, outputSymbols=[bobSymbol],
    ...                             name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> automata = Automata(s0, symbolList)
    >>>
    >>> # Create actors: Alice (a server) and Bob (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=automata, abstractionLayer=abstractionLayer, initiator=False)
    >>>
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=automata, abstractionLayer=abstractionLayer)
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Example with a dedicated automaton for a client and a server**

    The two actors are Alice and Bob. Bob is the initiator of the
    communication, meaning he sends the input symbols while Alice
    answers with the output symbols of the grammar. The grammar is
    very simple, and different for each actor. We first open the
    channel, and allow Bob to send the data ``"hello"`` multiple
    times. Alice answers every time with the data ``"hello"``.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> symbol = Symbol(name="Main-symbol", fields=[Field("hello")])
    >>> symbolList = [symbol]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_firstTransition = Transition(startState=bob_s1, endState=bob_s2,
    ...                                  inputSymbol=symbol, outputSymbols=[symbol],
    ...                                  name="hello")
    >>> bob_secondTransition = Transition(startState=bob_s2, endState=bob_s2,
    ...                                   inputSymbol=symbol, outputSymbols=[symbol],
    ...                                   name="hello")
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s2, endState=bob_s2, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol, outputSymbols=[symbol],
    ...                                   name="hello")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer)
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False)
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Modification of the emitted symbol by a client through a callback**

    The following example shows how to modify the symbol that is sent
    by the client to the server, through a callback method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifySymbol(available_symbols, current_symbol, current_state,
    ...                     last_sent_symbol, last_sent_message,
    ...                     last_received_symbol, last_received_message):
    ...
    ...    # Just printing some data accessible within the callback
    ...    print("Current state: '{}'".format(current_state))
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
    ...    print("[+] Last received symbol: '{}' with message: '{}'"
    ...          .format(last_received_symbol_name, last_received_message))
    ...    presets = {}
    ...
    ...    # Building the output symbol by incrementing the value of the last
    ...    # received symbol
    ...    if last_received_symbol is not None and last_received_message is not None:
    ...        (dummy, structured_data) = Symbol.abstract(last_received_message,
    ...                                                   [last_received_symbol])
    ...        field_data = structured_data[last_received_symbol.fields[0].name]
    ...        field_data_int = int.from_bytes(field_data, byteorder='big')
    ...        field_data = int(field_data_int + 1).to_bytes(length=1, byteorder='big')
    ...        presets[current_symbol.fields[0]] = field_data
    ...    else:
    ...        presets[current_symbol.fields[0]] = b'\x02'
    ...
    ...    print("[+] Sending symbol '{}' with presets: '{}'"
    ...          .format(current_symbol.name, presets))
    ...    return (current_symbol, presets)
    >>>
    >>> # We create the symbols
    >>> symbol1 = Symbol(fields=[Field(Raw(nbBytes=1))])
    >>> symbol2 = Symbol(fields=[Field(Raw(b'\x00'))])
    >>> symbolList = [symbol1, symbol2]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_mainTransition = Transition(startState=bob_s1, endState=bob_s1,
    ...                                 inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                 name="hello")
    >>>
    >>> # Apply the callback on the main transition
    >>> bob_mainTransition.add_cbk_modify_symbol(cbk_modifySymbol)
    >>>
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_s3 = State(name="S3")
    >>> alice_s4 = State(name="S4")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s2,
    ...                                inputSymbol=symbol1, outputSymbols=[symbol2],
    ...                                name="T1")
    >>> alice_transition2 = Transition(startState=alice_s2, endState=alice_s3,
    ...                                inputSymbol=symbol1, outputSymbols=[symbol2],
    ...                                name="T2")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s3,
    ...     endState=alice_s4, name="Close")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer)
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False)
    >>>
    >>> alice.start()
    >>> bob.start()  # doctest: +SKIP
    >>>
    >>> time.sleep(1)  # doctest: +SKIP
    Current state: 'S1'
    [+] Last received symbol: 'None' with message: 'None'
    [+] Sending symbol 'Symbol' with presets: '{Field: b'\x02'}'
    Current state: 'S1'
    [+] Last received symbol: 'Symbol' with message: 'b'\x00''
    [+] Sending symbol 'Symbol' with presets: '{Field: b'\x01'}'
    Current state: 'S1'
    [+] Last received symbol: 'Symbol' with message: 'b'\x00''
    [+] Sending symbol 'Symbol' with presets: '{Field: b'\x01'}'
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Modification of the emitted symbol by a server through a callback**

    The following example shows how to modify the symbol that is sent
    by the server in response to a client request, through a callback
    method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new symbol
    >>> def cbk_modifySymbol(available_symbols, current_symbol, current_state,
    ...                      last_sent_symbol, last_sent_message,
    ...                      last_received_symbol, last_received_message):
    ...
    ...    # Just printing some data accessible within the callback
    ...    print("Current state: '{}'".format(current_state))
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
    ...    print("[+] Last received symbol: '{}' with message: '{}'"
    ...          .format(last_received_symbol_name, last_received_message))
    ...    presets = {}
    ...
    ...    # Building the output symbol by incrementing the value of the last received symbol
    ...    if last_received_symbol is not None and last_received_message is not None:
    ...        (dummy, structured_data) = Symbol.abstract(last_received_message,
    ...                                                   [last_received_symbol])
    ...        field_data = structured_data[last_received_symbol.fields[0].name]
    ...        field_data_int = int.from_bytes(field_data, byteorder='big')
    ...        field_data = int(field_data_int + 1).to_bytes(length=1, byteorder='big')
    ...        presets[current_symbol.fields[0]] = field_data
    ...    else:
    ...        presets[current_symbol.fields[0]] = b'\x02'
    ...
    ...    print("[+] Sending symbol '{}' with presets: '{}'"
    ...          .format(current_symbol.name, presets))
    ...    return (current_symbol, presets)
    >>>
    >>> # We create the symbols
    >>> symbol1 = Symbol(fields=[Field(Raw(nbBytes=1))])
    >>> symbol2 = Symbol(fields=[Field(Raw(b'\x00'))])
    >>> symbolList = [symbol1, symbol2]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_s4 = State(name="S4")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_transition1 = Transition(startState=bob_s1, endState=bob_s2,
    ...                              inputSymbol=symbol2, outputSymbols=[symbol1],
    ...                              name="hello")
    >>> bob_transition2 = Transition(startState=bob_s2, endState=bob_s3,
    ...                              inputSymbol=symbol2, outputSymbols=[symbol1],
    ...                              name="hello")
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s3, endState=bob_s4, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                   name="T1")
    >>>
    >>> # Apply the callback on the main transition
    >>> alice_mainTransition.add_cbk_modify_symbol(cbk_modifySymbol)
    >>>
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer)
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False)
    >>>
    >>> alice.start()  # doctest: +SKIP
    >>> bob.start()
    >>>
    >>> time.sleep(1)  # doctest: +SKIP
    Current state: 'S1'
    [+] Last received symbol: 'Symbol' with message: 'b'\x00''
    [+] Sending symbol 'Symbol' with presets: '{Field: b'\x01'}'
    Current state: 'S1'
    [+] Last received symbol: 'Symbol' with message: 'b'\x00''
    [+] Sending symbol 'Symbol' with presets: '{Field: b'\x01'}'
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Modification of the selected transition by a client through a callback**

    The following example shows how to modify the selected transition
    of a client in its automaton, through a callback method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message,
    ...                          last_received_symbol, last_received_message):
    ...
    ...     # Just printing some data accessible within the callback
    ...     print("In cbk_modifyTransition()")
    ...     print("[+] Current state: '{}'".format(nextTransition.startState))
    ...     print("[+] Available transitions: '{}'".format(availableTransitions))
    ...     print("[+] Selected transition: '{}' with nextState: '{}'"
    ...           .format(nextTransition, nextTransition.endState))
    ...
    ...     # Modify the selected transition so that we change the next state
    ...     if nextTransition.endState == nextTransition.startState:
    ...         print("[+] Next state is similar as the current state. "
    ...               "We change this behavior by picking another transition")
    ...         availableTransitions.remove(nextTransition)
    ...         if len(availableTransitions) > 0:
    ...             nextTransition = random.choice(availableTransitions)
    ...             print("[+] Changed transition: '{}' with nextState: '{}'"
    ...                   .format(nextTransition, nextTransition.endState))
    ...     return nextTransition
    >>>
    >>> # We create the symbols
    >>> symbol1 = Symbol(fields=[Field(Raw(nbBytes=1))])
    >>> symbolList = [symbol1]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_s4 = State(name="S4")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_transition1 = Transition(startState=bob_s1, endState=bob_s1,
    ...                              inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                              name="T1")
    >>> bob_transition2 = Transition(startState=bob_s1, endState=bob_s2,
    ...                              inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                              name="T2")
    >>> bob_transition3 = Transition(startState=bob_s2, endState=bob_s2,
    ...                              inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                              name="T3")
    >>> bob_transition4 = Transition(startState=bob_s2, endState=bob_s3,
    ...                              inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                              name="T4")
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s3, endState=bob_s4, name="Close")
    >>>
    >>> # Apply the callback on the main states, which is the main state
    >>> bob_s1.add_cbk_modify_transition(cbk_modifyTransition)
    >>> bob_s2.add_cbk_modify_transition(cbk_modifyTransition)
    >>>
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol1, outputSymbols=symbolList,
    ...                                   name="T1")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer)
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False)
    >>>
    >>> alice.start()
    >>> bob.start()  # doctest: +SKIP
    >>>
    >>> time.sleep(1)  # doctest: +SKIP
    In cbk_modifyTransition()
    [+] Current state: 'S1'
    [+] Available transitions: '[T1, T2]'
    [+] Selected transition: 'T2' with nextState: 'S2'
    In cbk_modifyTransition()
    [+] Current state: 'S2'
    [+] Available transitions: '[T3, T4]'
    [+] Selected transition: 'T3' with nextState: 'S2'
    [+] Next state is similar as the current state. We change this behavior by picking another transition
    [+] Changed transition: 'T4' with nextState: 'S3'
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Modification of the current transition of a server through a callback**

    The following example shows how to modify the current transition
    of a server in its automaton, through a callback method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message,
    ...                          last_received_symbol, last_received_message):
    ...
    ...     # Just printing some data accessible within the callback
    ...     print("In cbk_modifyTransition()")
    ...     print("[+] Current state: '{}'".format(nextTransition.startState))
    ...     print("[+] Available transitions: '{}'".format(availableTransitions))
    ...     print("[+] Selected transition: '{}' with nextState: '{}'"
    ...           .format(nextTransition, nextTransition.endState))
    ...
    ...     # Modify the selected transition so that we change the next state
    ...     if nextTransition.endState == nextTransition.startState:
    ...         print("[+] Next state is similar as the current state. "
    ...               "We change this behavior by picking another transition")
    ...         availableTransitions.remove(nextTransition)
    ...         if len(availableTransitions) > 0:
    ...             nextTransition = random.choice(availableTransitions)
    ...             print("[+] Changed transition: '{}' with nextState: '{}'"
    ...                   .format(nextTransition, nextTransition.endState))
    ...     return nextTransition
    >>>
    >>> # We create the symbols
    >>> symbol1 = Symbol(fields=[Field(Raw(nbBytes=1))])
    >>> symbolList = [symbol1]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_mainTransition = Transition(startState=bob_s1,endState=bob_s1,
    ...                                 inputSymbol=symbol1, outputSymbols=symbolList,
    ...                                 name="T1")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_s3 = State(name="S3")
    >>> alice_s4 = State(name="S4")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s1,
    ...                               inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                               name="T1")
    >>> alice_transition2 = Transition(startState=alice_s1, endState=alice_s2,
    ...                               inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                               name="T2")
    >>> alice_transition3 = Transition(startState=alice_s2, endState=alice_s2,
    ...                               inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                               name="T3")
    >>> alice_transition4 = Transition(startState=alice_s2,  endState=alice_s3,
    ...                               inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                               name="T4")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s3, endState=alice_s4, name="Close")
    >>>
    >>> # Apply the callback on the main states, which is the main state
    >>> alice_s1.add_cbk_modify_transition(cbk_modifyTransition)
    >>> alice_s2.add_cbk_modify_transition(cbk_modifyTransition)
    >>>
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Create Bob actor (a server)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>>
    >>> # Create Alice actor (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    In cbk_modifyTransition()
    [+] Current state: 'S1'
    [+] Available transitions: '[T1, T2]'
    [+] Selected transition: 'T1' with nextState: 'S1'
    [+] Next state is similar as the current state. We change this behavior by picking another transition
    [+] Changed transition: 'T2' with nextState: 'S2'
    In cbk_modifyTransition()
    [+] Current state: 'S2'
    [+] Available transitions: '[T3, T4]'
    [+] Selected transition: 'T3' with nextState: 'S2'
    [+] Next state is similar as the current state. We change this behavior by picking another transition
    [+] Changed transition: 'T4' with nextState: 'S3'
    >>>
    >>> bob.stop()
    >>> alice.stop()


    **Transition with no input symbol**

    The following example shows how to specify no input symbol, for
    both a sender (Bob) and a receiver (Alice), at the state ``S1``.
    This example makes it possible to automatically transit to the next state ``S2``.
    Thus, Bob does not need to send a message (using
    :attr:`~netzob.Model.Grammar.Transitions.Transition.Transition.inputSymbol`)
    in transition between ``S2`` and ``S3`` to expect a message from Alice.

    This sequence temporarily puts Bob in receiving mode only, until this
    transition is active.

    >>> import time
    >>> from netzob.all import *
    >>>
    >>> # First, we create the symbols
    >>> helloAlice = Symbol(name="HelloAlice", fields=[Field("hello alice")])
    >>> helloBob = Symbol(name="HelloBob", fields=[Field("hello bob")])
    >>> bye = Symbol(name="Bye", fields=[Field("bye")])
    >>> bobSymbols = [helloAlice]
    >>> aliceSymbols = [helloBob]
    >>> allSymbols = bobSymbols + aliceSymbols + [bye]
    >>>
    >>> # Create the grammar
    >>> # Bob
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_s4 = State(name="S4")
    >>> OpenChannelTransition(bob_s0, bob_s1, name="Open")
    Open
    >>> Transition(bob_s1, bob_s2, inputSymbol=helloAlice, outputSymbols=[helloBob], name="Hello")
    Hello
    >>> Transition(bob_s2, bob_s3, inputSymbol=None, outputSymbols=[bye], name="Wait for bye")
    Wait for bye
    >>> CloseChannelTransition(bob_s3, bob_s4, name="Close")
    Close
    >>> bob_automata = Automata(bob_s0, allSymbols)
    >>>
    >>> # Alice
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_s3 = State(name="S3")
    >>> alice_s4 = State(name="S4")
    >>> OpenChannelTransition(alice_s0, alice_s1, name="Open")
    Open
    >>> Transition(alice_s1, alice_s2, inputSymbol=helloAlice, outputSymbols=[helloBob], name="Hello")
    Hello
    >>> Transition(alice_s2, alice_s3, inputSymbol=None, outputSymbols=[bye], name="Bye")
    Bye
    >>> CloseChannelTransition(alice_s3, alice_s4, name="Close")
    Close
    >>> alice_automata = Automata(alice_s0, allSymbols)
    >>>
    >>> # Create actors: Alice (a UDP server) and Bob (a UDP client)
    >>> # Alice
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, allSymbols)
    >>> abstractionLayer.timeout = .5
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer,
    ...               initiator=False, name="Alice")
    >>>
    >>> # Bob
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, allSymbols)
    >>> abstractionLayer.timeout = .5
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer,
    ...             initiator=True, name="Bob")
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(2)
    >>>
    >>> bob.stop()
    >>> alice.stop()


    """

    def __init__(self,
                 automata,          # type: Automata
                 abstractionLayer,  # type: AbstractionLayer
                 initiator=True,    # type: bool
                 name="Actor",      # type: str
                 ):
        # type: (...) -> None
        super(Actor, self).__init__()
        self.automata = automata
        self.initiator = initiator
        self.name = name
        self.abstractionLayer = abstractionLayer
        self.__stopEvent = threading.Event()

    def run(self):
        """Start the visit of the automaton from its initial state."""

        currentState = self.automata.initialState
        while not self.__stopEvent.isSet():
            try:
                self._logger.debug("Current state for actor '{}': '{}'.".format(self.name, currentState))
                if self.initiator:
                    currentState = currentState.executeAsInitiator(self.abstractionLayer)
                else:
                    currentState = currentState.executeAsNotInitiator(self.abstractionLayer)

                if currentState is None:
                    self._logger.debug("The execution of transition did not returned a state, for actor '{}'".format(self.name))
                    self.stop()

            except Exception as e:
                self._logger.warning("Exception raised for actor '{}' when on the execution of state {}.".format(self.name, currentState.name))
                self._logger.warning("Exception error for actor '{}': {}".format(self.name, str(e)))
                #self._logger.warning(traceback.format_exc())
                self.stop()

        self._logger.debug("Actor '{}' has finished to execute".format(self.name))

    @public_api
    def stop(self):
        """Stop the visit of the automaton.

        This operation is not immediate because we try to stop the
        thread as cleanly as possible.

        """
        self.__stopEvent.set()
        try:
            self.abstractionLayer.closeChannel()
        except Exception as e:
            self._logger.error(e)

    @public_api
    def isActive(self):
        """Indicate if the current actor is active (i.e. if the automaton
        visit is still processing).

        :return: True if the actor has not finished.
        :rtype: :class:`bool`
        """
        return not self.__stopEvent.is_set()

    @public_api
    @property
    def automata(self):
        return self.__automata

    @automata.setter  # type: ignore
    @typeCheck(Automata)
    def automata(self, automata):
        if automata is None:
            raise TypeError("Automata cannot be None")
        self.__automata = automata

    @public_api
    @property
    def initiator(self):
        return self.__initiator

    @initiator.setter  # type: ignore
    @typeCheck(bool)
    def initiator(self, initiator):
        if initiator is None:
            raise TypeError("Initiator  cannot be None")
        self.__initiator = initiator

    @public_api
    @property
    def abstractionLayer(self):
        return self.__abstractionLayer

    @abstractionLayer.setter  # type: ignore
    @typeCheck(AbstractionLayer)
    def abstractionLayer(self, abstractionLayer):
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")
        self.__abstractionLayer = abstractionLayer
