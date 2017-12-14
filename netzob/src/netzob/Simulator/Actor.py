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
import traceback
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Grammar.Automata import Automata
from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Fuzzing.Fuzz import Fuzz


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
    :param fuzz: A fuzzing configuration used during the
                 specialization process when writing symbols over the
                 abstraction layer. Values in this configuration will
                 override any field definition, constraints,
                 relationship dependencies or parameterized
                 fields. See :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`
                 for a complete explanation of its use for fuzzing
                 purpose. The default value is :const:`None`.
    :param fuzz_states: A list of states on which format message
                        fuzzing is applied. Default is ``[]``,
                        which means that the fuzzing configuration
                        is applied on each state.
    :param name: The name of the actor. Default value is 'Actor'.
    :type automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`,
                    required
    :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`, required
    :type initiator: :class:`bool`, optional
    :type fuzz: :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`, optional
    :param fuzz_states: :class:`dict` of :class:`State <netzob.Model.Grammar.States.State.State>`, optional
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
    :var name: The name of the actor.
    :vartype automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`
    :vartype abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
    :vartype initiator: :class:`bool`
    :vartype name: :class:`str`


    .. automethod:: netzob.Simulator.Actor.Actor.start

    .. automethod:: netzob.Simulator.Actor.Actor.stop

    .. automethod:: netzob.Simulator.Actor.Actor.isActive

    .. automethod:: netzob.Simulator.Actor.Actor.generateLog


    **Example with a common automaton for a client and a server**

    For instance, we can create two very simple network Actors which
    communicate together through a TCP channel and exchange their
    names until one stops.

    The two actors are Alice and Bob. Bob is the initiator of the
    communication. This means that Bob is the first actor to
    communicate with the remote peer, and Alice is listening for
    incoming messages. Bob sends an input symbol containing the string
    "bob>hello". Alice is waiting for this input symbol. When Alice
    receives this input symbol, she responds with an output symbol
    containing the string "alice>hello". Bob is then waiting for this
    output symbol.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field("bob>hello")])
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])
    >>> symbolList = [aliceSymbol, bobSymbol]
    >>>
    >>> # Create the grammar
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> mainTransition = Transition(startState=s1, endState=s1,
    ...                             inputSymbol=bobSymbol, outputSymbols=[aliceSymbol],
    ...                             name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> automata = Automata(s0, symbolList)
    >>>
    >>> automata_ascii = automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   hello (Bob-Hello;{Alice-Hello})
    |                         | ----------------------------------+
    |           S1            |                                   |
    |                         | <---------------------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create actors: Alice (a server) and Bob (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=automata, abstractionLayer=abstractionLayer, initiator=False, name='Alice')
    >>>
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=automata, abstractionLayer=abstractionLayer, name='Bob')
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> #time.sleep(1)
    >>>
    >>> bob.wait()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'hello'
      [+]   During transition 'hello', sending input symbol 'Bob-Hello'
      [+]   During transition 'hello', receiving expected output symbol 'Alice-Hello'
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'hello'
      [+]   During transition 'hello', sending input symbol 'Bob-Hello'
      [+]   During transition 'hello', receiving expected output symbol 'Alice-Hello'
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Bob-Hello', which corresponds to transition 'hello'
      [+]   During transition 'hello', choosing output symbol 'Alice-Hello'
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Bob-Hello', which corresponds to transition 'hello'
      [+]   During transition 'hello', choosing output symbol 'Alice-Hello'
      [+]   Transition 'hello' lead to state 'S1'


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
    >>> symbol = Symbol(name="Hello", fields=[Field("hello")])
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
    ...                                  name="T1")
    >>> bob_secondTransition = Transition(startState=bob_s2, endState=bob_s2,
    ...                                   inputSymbol=symbol, outputSymbols=[symbol],
    ...                                   name="T2")
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+
    |           S1            |
    +-------------------------+
      |
      | T1 (Hello;{Hello})
      v
    +-------------------------+   T2 (Hello;{Hello})
    |                         | ---------------------+
    |           S2            |                      |
    |                         | <--------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S3            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol, outputSymbols=[symbol],
    ...                                   name="T1")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   T1 (Hello;{Hello})
    |                         | ---------------------+
    |           S1            |                      |
    |                         | <--------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Hello'
      [+]   During transition 'T1', receiving expected output symbol 'Hello'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T2'
      [+]   During transition 'T2', sending input symbol 'Hello'
      [+]   During transition 'T2', receiving expected output symbol 'Hello'
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Hello', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Hello'
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Hello', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Hello'
      [+]   Transition 'T1' lead to state 'S1'


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
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
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
    ...    # Sending current symbol with specific preset
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
    ...                                 name="main transition")
    >>>
    >>> # Apply the callback on the main transition
    >>> bob_mainTransition.add_cbk_modify_symbol(cbk_modifySymbol)
    >>>
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #========================#
    H           S0           H
    #========================#
      |
      | OpenChannelTransition
      v
    +------------------------+   main transition (Symbol;{Symbol}) [CBK modify symbol]
    |                        | --------------------------------------------------------+
    |           S1           |                                                         |
    |                        | <-------------------------------------------------------+
    +------------------------+
    <BLANKLINE>
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
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+
    |           S1            |
    +-------------------------+
      |
      | T1 (Symbol;{Symbol})
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
      |
      | T2 (Symbol;{Symbol})
      v
    +-------------------------+
    |           S3            |
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S4            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'main transition'
      [+]   During transition 'main transition', sending input symbol 'Symbol'
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol 'Symbol'
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'main transition'
      [+]   During transition 'main transition', sending input symbol 'Symbol'
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol 'Symbol'
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'main transition'
      [+]   During transition 'main transition', sending input symbol 'Symbol'
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Symbol'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T2'
      [+]   During transition 'T2', choosing output symbol 'Symbol'
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'


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
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
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
    ...    # Sending current symbol with specific presets
    ...    return (current_symbol, presets)
    >>>
    >>> # We create the symbols
    >>> symbol1 = Symbol(fields=[Field(Raw(nbBytes=1))], name='symbol1')
    >>> symbol2 = Symbol(fields=[Field(Raw(b'\x00'))], name='symbol2')
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
    ...                              name="T1")
    >>> bob_transition2 = Transition(startState=bob_s2, endState=bob_s3,
    ...                              inputSymbol=symbol2, outputSymbols=[symbol1],
    ...                              name="T2")
    >>> bob_closeTransition = CloseChannelTransition(startState=bob_s3, endState=bob_s4, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+
    |           S1            |
    +-------------------------+
      |
      | T1 (symbol2;{symbol1})
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
      |
      | T2 (symbol2;{symbol1})
      v
    +-------------------------+
    |           S3            |
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S4            |
    +-------------------------+
    <BLANKLINE>
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
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #========================#
    H           S0           H
    #========================#
      |
      | OpenChannelTransition
      v
    +------------------------+   T1 (symbol1;{symbol1}) [CBK modify symbol]
    |                        | ---------------------------------------------+
    |           S1           |                                              |
    |                        | <--------------------------------------------+
    +------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'symbol2'
      [+]   During transition 'T1', receiving expected output symbol 'symbol1'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T2'
      [+]   During transition 'T2', sending input symbol 'symbol2'
      [+]   During transition 'T2', receiving expected output symbol 'symbol1'
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'symbol1', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'symbol1'
      [+]   During transition 'T1', modifying output symbol to 'symbol1', through callback
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'symbol1', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'symbol1'
      [+]   During transition 'T1', modifying output symbol to 'symbol1', through callback
      [+]   Transition 'T1' lead to state 'S1'



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
    ...     # Modify the selected transition so that we change the next state
    ...     if nextTransition.endState == nextTransition.startState:
    ...         availableTransitions.remove(nextTransition)
    ...         if len(availableTransitions) > 0:
    ...             nextTransition = random.choice(availableTransitions)
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
    >>> # Apply the callback on the main states
    >>> bob_s1.add_cbk_modify_transition(cbk_modifyTransition)
    >>> bob_s2.add_cbk_modify_transition(cbk_modifyTransition)
    >>>
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #============================#
    H             S0             H
    #============================#
      |
      | OpenChannelTransition
      v
    +----------------------------+   T1 (Symbol;{Symbol})
    |                            | -----------------------+
    | S1 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T2 (Symbol;{Symbol})
      v
    +----------------------------+   T3 (Symbol;{Symbol})
    |                            | -----------------------+
    | S2 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T4 (Symbol;{Symbol})
      v
    +----------------------------+
    |             S3             |
    +----------------------------+
      |
      | CloseChannelTransition
      v
    +----------------------------+
    |             S4             |
    +----------------------------+
    <BLANKLINE>
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
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #============================#
    H             S0             H
    #============================#
      |
      | OpenChannelTransition
      v
    +----------------------------+   T1 (Symbol;{Symbol})
    |                            | -----------------------+
    | S1 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T2 (Symbol;{Symbol})
      v
    +----------------------------+   T3 (Symbol;{Symbol})
    |                            | -----------------------+
    | S2 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T4 (Symbol;{Symbol})
      v
    +----------------------------+
    |             S3             |
    +----------------------------+
      |
      | CloseChannelTransition
      v
    +----------------------------+
    |             S4             |
    +----------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T2'
      [+]   Changing transition to 'T2', through callback
      [+]   During transition 'T2', sending input symbol 'Symbol'
      [+]   During transition 'T2', receiving expected output symbol 'Symbol'
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T4'
      [+]   Changing transition to 'T4', through callback
      [+]   During transition 'T4', sending input symbol 'Symbol'
      [+]   During transition 'T4', receiving expected output symbol 'Symbol'
      [+]   Transition 'T4' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Symbol'
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Symbol'
      [+]   Transition 'T1' lead to state 'S1'


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
    ...     # Modify the selected transition so that we change the next state
    ...     if nextTransition.endState == nextTransition.startState:
    ...         availableTransitions.remove(nextTransition)
    ...         if len(availableTransitions) > 0:
    ...             nextTransition = random.choice(availableTransitions)
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
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #========================#
    H           S0           H
    #========================#
      |
      | OpenChannelTransition
      v
    +------------------------+   T1 (Symbol;{Symbol})
    |                        | -----------------------+
    |           S1           |                        |
    |                        | <----------------------+
    +------------------------+
    <BLANKLINE>
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
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #============================#
    H             S0             H
    #============================#
      |
      | OpenChannelTransition
      v
    +----------------------------+   T1 (Symbol;{Symbol})
    |                            | -----------------------+
    | S1 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T2 (Symbol;{Symbol})
      v
    +----------------------------+   T3 (Symbol;{Symbol})
    |                            | -----------------------+
    | S2 [CBK modify transition] |                        |
    |                            | <----------------------+
    +----------------------------+
      |
      | T4 (Symbol;{Symbol})
      v
    +----------------------------+
    |             S3             |
    +----------------------------+
      |
      | CloseChannelTransition
      v
    +----------------------------+
    |             S4             |
    +----------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a server)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Symbol'
      [+]   During transition 'T1', receiving expected output symbol 'Symbol'
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Symbol'
      [+]   During transition 'T1', receiving expected output symbol 'Symbol'
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Symbol'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T1'
      [+]   Changing transition to 'T2', through callback
      [+]   During transition 'T2', choosing output symbol 'Symbol'
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Receiving input symbol 'Symbol', which corresponds to transition 'T3'
      [+]   Changing transition to 'T4', through callback
      [+]   During transition 'T4', choosing output symbol 'Symbol'
      [+]   Transition 'T4' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'


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
    >>> topen = OpenChannelTransition(bob_s0, bob_s1, name="Open")
    >>> t1 = Transition(bob_s1, bob_s2, inputSymbol=helloAlice, outputSymbols=[helloBob], name="T1")
    >>> t2 = Transition(bob_s2, bob_s3, inputSymbol=None, outputSymbols=[bye], name="T2")
    >>> tclose = CloseChannelTransition(bob_s3, bob_s4, name="Close")
    >>> bob_automata = Automata(bob_s0, allSymbols)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #=============================#
    H             S0              H
    #=============================#
      |
      | OpenChannelTransition
      v
    +-----------------------------+
    |             S1              |
    +-----------------------------+
      |
      | T1 (HelloAlice;{HelloBob})
      v
    +-----------------------------+
    |             S2              |
    +-----------------------------+
      |
      | T2 (Empty Symbol;{Bye})
      v
    +-----------------------------+
    |             S3              |
    +-----------------------------+
      |
      | CloseChannelTransition
      v
    +-----------------------------+
    |             S4              |
    +-----------------------------+
    <BLANKLINE>
    >>>
    >>> # Alice
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_s3 = State(name="S3")
    >>> alice_s4 = State(name="S4")
    >>> t0 = OpenChannelTransition(alice_s0, alice_s1, name="Open")
    >>> t1 = Transition(alice_s1, alice_s2, inputSymbol=helloAlice, outputSymbols=[helloBob], name="Hello")
    >>> outputSymbolsReactionTime = {bye: 0.5}
    >>> t2 = Transition(alice_s2, alice_s3, inputSymbol=None, outputSymbols=[bye], outputSymbolsReactionTime=outputSymbolsReactionTime, name="Bye")
    >>> t3 = CloseChannelTransition(alice_s3, alice_s4, name="Close")
    >>> alice_automata = Automata(alice_s0, allSymbols)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #================================#
    H               S0               H
    #================================#
      |
      | OpenChannelTransition
      v
    +--------------------------------+
    |               S1               |
    +--------------------------------+
      |
      | Hello (HelloAlice;{HelloBob})
      v
    +--------------------------------+
    |               S2               |
    +--------------------------------+
      |
      | Bye (Empty Symbol;{Bye})
      v
    +--------------------------------+
    |               S3               |
    +--------------------------------+
      |
      | CloseChannelTransition
      v
    +--------------------------------+
    |               S4               |
    +--------------------------------+
    <BLANKLINE>
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
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=3.)
    >>> abstractionLayer = AbstractionLayer(channel, allSymbols)
    >>> abstractionLayer.timeout = .5
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer,
    ...             initiator=True, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(2)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'HelloAlice'
      [+]   During transition 'T1', receiving expected output symbol 'HelloBob'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T2'
      [+]   During transition 'T2', sending input symbol 'Empty Symbol'
      [+]   During transition 'T2', receiving expected output symbol 'Bye'
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'HelloAlice', which corresponds to transition 'Hello'
      [+]   During transition 'Hello', choosing output symbol 'HelloBob'
      [+]   Transition 'Hello' lead to state 'S2'
      [+] At state 'S2'
      [+]   Receiving no symbol (EmptySymbol), which corresponds to transition 'Bye'
      [+]   During transition 'Bye', choosing output symbol 'Bye'
      [+]   Transition 'Bye' lead to state 'S3'
      [+] At state 'S3'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'


    **Example on how to catch all read symbol timeout**

    The following example shows how to specify a global behavior, on
    all states and transitions, in order to catch timeouts when
    listening for symbols. In this example, we set a callback through the method :meth:`set_cbk_read_symbol_timeout`. when a timeout occurs on
    reception of a symbol, the defined callback will move the current
    position in the state machine to a specific state called
    'error_state'.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create a symbol
    >>> symbol = Symbol(name="Hello", fields=[Field("hello")])
    >>> symbolList = [symbol]
    >>>
    >>> # Create the grammar
    >>> s0 = State(name="Start state")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="Close state")
    >>> error_state = State(name="Error state")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> outputSymbolsReactionTime = {symbol: 2.0}
    >>> mainTransition = Transition(startState=s1, endState=s1,
    ...                             inputSymbol=symbol,
    ...                             outputSymbols=[symbol],
    ...                             outputSymbolsReactionTime=outputSymbolsReactionTime,
    ...                             name="T1")
    >>> closeTransition1 = CloseChannelTransition(startState=error_state, endState=s2, name="Close with error")
    >>> closeTransition2 = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> automata = Automata(s0, symbolList)
    >>>
    >>> def cbk_method(current_state, current_transition=None):
    ...     return error_state
    >>> automata.set_cbk_read_symbol_timeout(cbk_method)
    >>>
    >>> automata_ascii = automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H       Start state       H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   T1 (Hello;{Hello})
    |                         | ---------------------+
    |           S1            |                      |
    |                         | <--------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |       Close state       |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create actors: Alice (a server) and Bob (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=automata, abstractionLayer=abstractionLayer, initiator=False, name='Alice')
    >>>
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=automata, abstractionLayer=abstractionLayer, name='Bob')
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(5)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'Start state'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Hello'
      [+]   During transition 'T1', timeout in reception triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Picking transition 'Close with error'
      [+]   Transition 'Close with error' lead to state 'Close state'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'Start state'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Hello', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Hello'
      [+]   Transition 'T1' lead to state 'S1'


    **Example on how to catch all receptions of unexpected symbols**

    The following example shows how to specify a global behavior, on
    all states and transitions, in order to catch reception of unexpected symbols (i.e. symbols that are known but not expected at this state/transition). In this example, we set a callback through the method :meth:`set_cbk_read_unexpected_symbol`. When an unexpected symbol is received, the defined callback will move the current
    position in the state machine to a specific state called
    'error_state'.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> symbol1 = Symbol(name="Hello1", fields=[Field("hello1")])
    >>> symbol2 = Symbol(name="Hello2", fields=[Field("hello2")])
    >>> symbolList = [symbol1, symbol2]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_error_state = State(name="Error state")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_mainTransition = Transition(startState=bob_s1, endState=bob_s2,
    ...                                 inputSymbol=symbol1, outputSymbols=[symbol2],
    ...                                 name="T1")
    >>> bob_closeTransition1 = CloseChannelTransition(startState=bob_error_state, endState=bob_s3, name="Close")
    >>> bob_closeTransition2 = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> def cbk_method(current_state, current_transition=None, received_symbol=None, received_message=None):
    ...     return bob_error_state
    >>> bob_automata.set_cbk_read_unexpected_symbol(cbk_method)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+
    |           S1            |
    +-------------------------+
      |
      | T1 (Hello1;{Hello2})
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S3            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                   name="T1")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   T1 (Hello1;{Hello1})
    |                         | -----------------------+
    |           S1            |                        |
    |                         | <----------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Hello1'
      [+]   During transition 'T1', receiving unexpected symbol triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S3'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Hello1', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Hello1'
      [+]   Transition 'T1' lead to state 'S1'


    **Example on how to catch all receptions of unknown messages**

    The following example shows how to specify a global behavior, on
    all states and transitions, in order to catch reception of unknown messages (i.e. messages that cannot be abstracted to a symbol). In this example, we set a callback through the method :meth:`set_cbk_read_unknown_symbol`. When an unknown message is received, the defined callback will move the current
    position in the state machine to a specific state called
    'error_state'.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> symbol1 = Symbol(name="Hello1", fields=[Field("hello1")])
    >>> symbol2 = Symbol(name="Hello2", fields=[Field("hello2")])
    >>> symbolList = [symbol1]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_s3 = State(name="S3")
    >>> bob_error_state = State(name="Error state")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_mainTransition = Transition(startState=bob_s1, endState=bob_s2,
    ...                                 inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                 name="T1")
    >>> bob_closeTransition1 = CloseChannelTransition(startState=bob_error_state, endState=bob_s3, name="Close")
    >>> bob_closeTransition2 = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> def cbk_method(current_state, current_transition=None, received_symbol=None, received_message=None):
    ...     return bob_error_state
    >>> bob_automata.set_cbk_read_unknown_symbol(cbk_method)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+
    |           S1            |
    +-------------------------+
      |
      | T1 (Hello1;{Hello1})
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S3            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=symbol1, outputSymbols=[symbol2],
    ...                                   name="T1")
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   T1 (Hello1;{Hello2})
    |                         | -----------------------+
    |           S1            |                        |
    |                         | <----------------------+
    +-------------------------+
      |
      | CloseChannelTransition
      v
    +-------------------------+
    |           S2            |
    +-------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Hello1'
      [+]   During transition 'T1', receiving unknown symbol triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Picking transition 'Close'
      [+]   Transition 'Close' lead to state 'S3'
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Hello1', which corresponds to transition 'T1'
      [+]   During transition 'T1', choosing output symbol 'Hello2'
      [+]   Transition 'T1' lead to state 'S1'


    **Example of message format fuzzing from an actor**

    This example shows the creation of a fuzzing actor, Bob, that will
    exchange messages with a Target, Alice. Messages generated from
    'Symbol 1' will be specifically fuzzed, but not messages generated from
    'Symbol 2'.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> symbol1 = Symbol([Field(uint8(interval=(4, 8)))], name="Symbol 1")
    >>> symbol2 = Symbol([Field(uint8(interval=(10, 12)))], name="Symbol 2")
    >>> symbolList = [symbol1, symbol2]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_firstTransition = Transition(startState=bob_s1, endState=bob_s2,
    ...                                  inputSymbol=symbol1, outputSymbols=[symbol1, symbol2],
    ...                                  name="T1")
    >>> bob_secondTransition = Transition(startState=bob_s2, endState=bob_s2,
    ...                                   inputSymbol=symbol2, outputSymbols=[symbol1, symbol2],
    ...                                   name="T2")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
    #====================================#
    H                 S0                 H
    #====================================#
      |
      | OpenChannelTransition
      v
    +------------------------------------+
    |                 S1                 |
    +------------------------------------+
      |
      | T1 (Symbol 1;{Symbol 1,Symbol 2})
      v
    +------------------------------------+   T2 (Symbol 2;{Symbol 1,Symbol 2})
    |                                    | ------------------------------------+
    |                 S2                 |                                     |
    |                                    | <-----------------------------------+
    +------------------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s1,
    ...                                inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                name="T1")
    >>> alice_transition2 = Transition(startState=alice_s1, endState=alice_s1,
    ...                                inputSymbol=symbol2, outputSymbols=[symbol2],
    ...                                name="T2")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Creation of a callback function that always returns alice_transition2 to handle reception of fuzzed messages
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message,
    ...                          last_received_symbol, last_received_message):
    ...     if nextTransition is None:
    ...         return alice_transition2
    ...     else:
    ...         return nextTransition
    >>>
    >>> alice_automata.getState('S1').add_cbk_modify_transition(cbk_modifyTransition)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
                                   #============================#
                                   H             S0             H
                                   #============================#
                                     |
                                     | OpenChannelTransition
                                     v
        T2 (Symbol 2;{Symbol 2})   +----------------------------+   T1 (Symbol 1;{Symbol 1})
      +--------------------------- |                            | ---------------------------+
      |                            | S1 [CBK modify transition] |                            |
      +--------------------------> |                            | <--------------------------+
                                   +----------------------------+
    <BLANKLINE>
    >>>
    >>> # Define fuzzing configuration
    >>> fuzz = Fuzz()
    >>> fuzz.set(symbol1)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, fuzz=fuzz, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Symbol 1'
      [+]   During transition 'T1', fuzzing activated
      [+]   During transition 'T1', receiving expected output symbol 'Symbol 2'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T2'
      [+]   During transition 'T2', sending input symbol 'Symbol 2'
      [+]   During transition 'T2', fuzzing activated
      [+]   During transition 'T2', receiving expected output symbol 'Symbol 2'
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Unknown message b'\xc5'', which corresponds to transition 'None'
      [+]   Changing transition to 'T2', through callback
      [+]   During transition 'T2', choosing output symbol 'Symbol 2'
      [+]   Transition 'T2' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol 2', which corresponds to transition 'T2'
      [+]   Changing transition to 'T2', through callback
      [+]   During transition 'T2', choosing output symbol 'Symbol 2'
      [+]   Transition 'T2' lead to state 'S1'


    **Example of message format fuzzing from an actor, at a specific state**

    This example shows the creation of a fuzzing actor, Bob, that will
    exchange messages with a Target, Alice. Only messages sent at a
    specific state, S2, will be fuzzed.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> symbol1 = Symbol([Field(uint8(interval=(4, 8)))], name="Symbol 1")
    >>> symbol2 = Symbol([Field(uint8(interval=(10, 12)))], name="Symbol 2")
    >>> symbolList = [symbol1, symbol2]
    >>>
    >>> # Create Bob's automaton
    >>> bob_s0 = State(name="S0")
    >>> bob_s1 = State(name="S1")
    >>> bob_s2 = State(name="S2")
    >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
    >>> bob_firstTransition = Transition(startState=bob_s1, endState=bob_s2,
    ...                                  inputSymbol=symbol1, outputSymbols=[symbol1, symbol2],
    ...                                  name="T1")
    >>> bob_secondTransition = Transition(startState=bob_s2, endState=bob_s2,
    ...                                   inputSymbol=symbol2, outputSymbols=[symbol1, symbol2],
    ...                                   name="T2")
    >>> bob_thirdTransition = Transition(startState=bob_s2, endState=bob_s2,
    ...                                  inputSymbol=symbol1, outputSymbols=[symbol1, symbol2],
    ...                                  name="T3")
    >>> bob_automata = Automata(bob_s0, symbolList)
    >>>
    >>> automata_ascii = bob_automata.generateASCII()
    >>> print(automata_ascii)
                                            #====================================#
                                            H                 S0                 H
                                            #====================================#
                                              |
                                              | OpenChannelTransition
                                              v
                                            +------------------------------------+
                                            |                 S1                 |
                                            +------------------------------------+
                                              |
                                              | T1 (Symbol 1;{Symbol 1,Symbol 2})
                                              v
        T3 (Symbol 1;{Symbol 1,Symbol 2})   +------------------------------------+   T2 (Symbol 2;{Symbol 1,Symbol 2})
      +------------------------------------ |                                    | ------------------------------------+
      |                                     |                 S2                 |                                     |
      +-----------------------------------> |                                    | <-----------------------------------+
                                            +------------------------------------+
    <BLANKLINE>
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s1,
    ...                                inputSymbol=symbol1, outputSymbols=[symbol1],
    ...                                name="T1")
    >>> alice_transition2 = Transition(startState=alice_s1, endState=alice_s1,
    ...                                inputSymbol=symbol2, outputSymbols=[symbol2],
    ...                                name="T2")
    >>> alice_automata = Automata(alice_s0, symbolList)
    >>>
    >>> # Creation of a callback function that always returns alice_transition2 to handle reception of fuzzed messages
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message,
    ...                          last_received_symbol, last_received_message):
    ...     if nextTransition is None:
    ...         return alice_transition2
    ...     else:
    ...         return nextTransition
    >>>
    >>> alice_automata.getState('S1').add_cbk_modify_transition(cbk_modifyTransition)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
                                   #============================#
                                   H             S0             H
                                   #============================#
                                     |
                                     | OpenChannelTransition
                                     v
        T2 (Symbol 2;{Symbol 2})   +----------------------------+   T1 (Symbol 1;{Symbol 1})
      +--------------------------- |                            | ---------------------------+
      |                            | S1 [CBK modify transition] |                            |
      +--------------------------> |                            | <--------------------------+
                                   +----------------------------+
    <BLANKLINE>
    >>>
    >>> # Define fuzzing configuration
    >>> fuzz = Fuzz()
    >>> fuzz.set(symbol1)
    >>> fuzz.set(symbol2)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> bob = Actor(automata=bob_automata, abstractionLayer=abstractionLayer, fuzz=fuzz, fuzz_states=['S2'], name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> abstractionLayer = AbstractionLayer(channel, symbolList)
    >>> alice = Actor(automata=alice_automata, abstractionLayer=abstractionLayer, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> time.sleep(0.5)
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Picking transition 'T1'
      [+]   During transition 'T1', sending input symbol 'Symbol 1'
      [+]   During transition 'T1', receiving expected output symbol 'Symbol 1'
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Picking transition 'T2'
      [+]   During transition 'T2', sending input symbol 'Symbol 2'
      [+]   During transition 'T2', fuzzing activated
      [+]   During transition 'T2', receiving expected output symbol 'Symbol 2'
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice':
      [+] At state 'S0'
      [+]   Picking transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Symbol 1', which corresponds to transition 'T1'
      [+]   Changing transition to 'T1', through callback
      [+]   During transition 'T1', choosing output symbol 'Symbol 1'
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Receiving input symbol 'Unknown message b'\xc5'', which corresponds to transition 'None'
      [+]   Changing transition to 'T2', through callback
      [+]   During transition 'T2', choosing output symbol 'Symbol 2'
      [+]   Transition 'T2' lead to state 'S1'

    """

    def __init__(self,
                 automata,          # type: Automata
                 abstractionLayer,  # type: AbstractionLayer
                 initiator=True,    # type: bool
                 fuzz=None,         # type: Fuzz
                 fuzz_states=[],    # type: dict
                 name="Actor",      # type: str
                 ):
        # type: (...) -> None
        super(Actor, self).__init__()
        self.automata = automata
        self.initiator = initiator
        self.fuzz = fuzz
        self.fuzz_states = fuzz_states
        self.name = name
        self.abstractionLayer = abstractionLayer
        self.__stopEvent = threading.Event()

        # Max number of transitions the actor can browse
        self.__nbMaxTransitions = None   # None means no limit
        self._currentnbTransitions = 0

        # Initiate visit log, which contains the information regarding the different transitions and states visited by the actor
        self.visit_log = []

    def __str__(self):
        return str(self.name)

    def run(self):
        """Start the visit of the automaton from its initial state."""

        currentState = self.automata.initialState
        while not self.__stopEvent.isSet():
            try:
                self._logger.debug("Current state for actor '{}': '{}'.".format(self.name, currentState))
                if self.initiator:
                    currentState = currentState.executeAsInitiator(self.abstractionLayer, self)
                else:
                    currentState = currentState.executeAsNotInitiator(self.abstractionLayer, self)

                if currentState is None:
                    self._logger.debug("The execution of transition did not returned a state, for actor '{}'".format(self.name))
                    self.stop()

                self._currentnbTransitions += 1
                if self.nbMaxTransitions is not None and self._currentnbTransitions >= self.nbMaxTransitions:
                    self._logger.debug("[actor='{}'] Max number of transitions ({}) reached".format(self.name, self.nbMaxTransitions))
                    self.visit_log.append("  [+] At state '{}', we reached the max number of transitions ({}), so we stop".format(currentState, self.nbMaxTransitions))
                    self.stop()

            except Exception as e:
                self._logger.debug("Exception raised for actor '{}' when on the execution of state {}.".format(self.name, currentState))
                self._logger.error("Exception error for actor '{}': {}".format(self.name, str(e)))
                self._logger.warn(traceback.format_exc())
                self.stop()

        self._logger.debug("Actor '{}' has finished to execute".format(self.name))

    @public_api
    def stop(self):
        """Stop the visit of the automaton.

        This operation is not immediate because we try to stop the
        thread as cleanly as possible.

        """
        self._logger.debug("[actor='{}'] Stopping the current actor".format(self.name))

        self.__stopEvent.set()
        try:
            self.abstractionLayer.closeChannel()
        except Exception as e:
            self._logger.error(e)

    @public_api
    def wait(self):
        """Wait for the current actor to finish the visit of the automaton.

        """
        self._logger.debug("[actor='{}'] Waiting for the current actor to finish".format(self.name))

        while self.isActive():
            time.sleep(0.5)

        self._logger.debug("[actor='{}'] The current actor has finished".format(self.name))

    @public_api
    def isActive(self):
        """Indicate if the current actor is active (i.e. if the automaton
        visit is still processing).

        :return: True if the actor has not finished.
        :rtype: :class:`bool`
        """
        return not self.__stopEvent.is_set()

    @public_api
    def generateLog(self):
        """Return the log of the transitions and states visited by the actor.

        """
        result = "Activity log for actor '{}':\n".format(self.name)
        result += "\n".join(self.visit_log)
        return result


    ## Properties

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

    @property
    def fuzz(self):
        return self.__fuzz

    @fuzz.setter  # type: ignore
    @typeCheck(Fuzz)
    def fuzz(self, fuzz):
        self.__fuzz = fuzz

    @property
    def fuzz_states(self):
        return self.__fuzz_states

    @fuzz_states.setter  # type: ignore
    @typeCheck(list)
    def fuzz_states(self, fuzz_states):
        self.__fuzz_states = fuzz_states

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

    @public_api
    @property
    def nbMaxTransitions(self):
        return self.__nbMaxTransitions

    @nbMaxTransitions.setter  # type: ignore
    @typeCheck(int)
    def nbMaxTransitions(self, nbMaxTransitions):
        self.__nbMaxTransitions = nbMaxTransitions
