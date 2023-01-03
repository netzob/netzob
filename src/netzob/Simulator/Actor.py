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
from threading import Thread, Event
#from multiprocessing import Process, Event
import traceback
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Grammar.Automata import Automata
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Model.Vocabulary.Preset import Preset


class ActorStopException(Exception):
    pass


@NetzobLogger
class Actor(Thread):
    r"""An actor is a component which, given a automaton and a list of
    symbols, can visit the automaton, and generate and parse messages
    in respect to the states and transitions.

    An actor is implemented as a Python thread. An actor should be
    launched with the :meth:`start <netzob.Simulator.Actor.Actor.start>` method. When an actor starts, it
    automatically visits the associated automaton, and exchanges
    symbols with a remote peer. This capability to automatically
    travel the automaton is called the **visit loop**.

    Without any special directive, the visit loop will stop if it
    reaches one of the terminal states of the automaton.

    It is possible to stop the visit loop using the
    :meth:`stop <netzob.Simulator.Actor.Actor.stop>` method. An actor always stops its visit loop at a
    state, and never during a transition. This means that when calling
    the :meth:`stop <netzob.Simulator.Actor.Actor.stop>` method, if the actor is currently executing a
    transition, it will finish the transition and will reach the
    ending state of the transition.

    It is also possible to define exit conditions where the actor
    exits the visit loop if specific conditions are met. Currently available exit conditions are
    :attr:`nbMaxTransitions` and :attr:`target_state` (see explanation below).

    When an actor either reaches an exit condition, a terminal state, or is forced to
    stop the visit loop, we then get manual control over the visit of
    the automaton. For example, we can indicate to execute the next
    transition through the :meth:`execute_transition <netzob.Simulator.Actor.Actor.execute_transition>` method.

    The Actor constructor expects some parameters:

    :param automata: This parameter is the automaton the actor will visit.
    :param channel: This parameter is the underlying communication channel.
    :param initiator: This parameter, if ``True``, indicates that the actor initiates the
                      communication and emits the input symbol.
                      If ``False``, indicates that the actor is waiting for another
                      peer to initiate the connection. Default value is ``True``.
    :param name: The name of the actor. Default value is 'Actor'.
    :type automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`,
                    required
    :type channel: :class:`AbstractChannel <netzob.Model.Simulator.AbstractChannel.AbstractChannel>`, required
    :type name: :class:`str`, optional
    :type initiator: :class:`bool`, optional

    The Actor class provides the following public variables:

    :var automata: The automaton the actor will visit.
    :var channel: The underlying communication channel.
    :var name: The name of the actor.
    :var fuzzing_presets: A list of preset configurations, used for fuzzing purpose at
                         specific states (see ``fuzzing_states`` attribute), only when sending symbols.
                         Values in this fuzzing configuration will
                         override any field definition, constraints or
                         relationship dependencies. See :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
                         for a complete explanation of its usage for fuzzing purpose.
    :var fuzzing_states: A list of states on which format message
                         fuzzing is applied.
    :var memory: A memory context used to store variable values during specialization
                 and abstraction of successive symbols. This context is notably used to handle
                 inter-symbol relationships and relationships with the environment.
    :var presets: A :class:`list` of preset configurations used during specialization and abstraction of symbols emitted and received by the actor. Values
                 in this configuration will override any field
                 definition, constraints or relationship dependencies. See
                 :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
                 for a complete explanation of its usage.
    :var cbk_select_data: A callback used to tell if the current actor is concerned by the data received on the communication channel.
    :var current_state: The current state of the actor.
    :var target_state: A state at which position the actor will exit the visit loop. This is an exit condition of the visit loop. ``None`` (the default value) means no targeted state.
    :var nbMaxTransitions: The maximum number of transitions the actor will visit. This is an exit condition of the visit loop. ``None`` (the default value) means no limit.

    :vartype automata: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`
    :vartype channel: :class:`AbstractChannel <netzob.Model.Simulator.AbstractChannel.AbstractChannel>`
    :vartype name: :class:`str`
    :vartype fuzzing_presets: :class:`list` of :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
    :vartype fuzzing_states: :class:`list` of :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype memory: :class:`Memory <netzob.Model.Vocabular.Domain.Variables.Memory.Memory>`
    :vartype presets: :class:`list` of :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
    :vartype cbk_select_data: :class:`Callable <collections.abc.Callable>`
    :vartype current_state: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype target_state: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype nbMaxTransitions: :class:`int`


    **Callback prototype**

    A callback function can be used to tell if the current actor is concerned by the received data on the communication channel. The callback function that can be used in the
    ``cbk_select_data`` parameter has the following prototype:

    .. function:: cbk_select_data(data)
       :noindex:

       :param data: contains the current data received on the communication channel.
       :type data: :class:`bytes`

       :return: The callback function should return a :class:`bool`
                telling if the current actor is concerned by the
                received data (should be set to ``True`` in such case).
       :rtype: :class:`bool`


    **Actor methods**

    .. automethod:: netzob.Simulator.Actor.Actor.start

    .. automethod:: netzob.Simulator.Actor.Actor.stop

    .. automethod:: netzob.Simulator.Actor.Actor.wait

    .. automethod:: netzob.Simulator.Actor.Actor.execute_transition

    .. automethod:: netzob.Simulator.Actor.Actor.isActive

    .. automethod:: netzob.Simulator.Actor.Actor.generateLog


    **List of actor examples**

    Several illustrations of actor usages are provided below:

    * Common automaton for a client and a server (see ActorExample1_).
    * Dedicated automaton for a client and a server (see ActorExample2_).
    * Modification of the emitted symbol by a client through a callback (see ActorExample3_).
    * Modification of the emitted symbol by a server through a callback (see ActorExample4_).
    * Modification of the current transition by a client through a callback (see ActorExample5_).
    * Modification of the current transition of a server through a callback (see ActorExample6_).
    * Transition with no input symbol (see ActorExample7_).
    * How to catch all read symbol timeout (see ActorExample8_).
    * How to catch all receptions of unexpected symbols (see ActorExample9_).
    * How to catch all receptions of unknown messages (see ActorExample10_).
    * Message format fuzzing from an actor (see ActorExample11_).
    * Message format fuzzing from an actor, at a specific state (see ActorExample12_).
    * Several actors on the same communication channel (see ActorExample13_).


    .. _ActorExample1:

    **Common automaton for a client and a server**

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
    >>> Conf.seed = 10
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field("bob>hello")])
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field("alice>hello")])
    >>> symbolList = [aliceSymbol, bobSymbol]
    >>>
    >>> # Create the automaton
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
    >>> alice = Actor(automata=automata, channel=channel, initiator=False, name='Alice')
    >>>
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> bob = Actor(automata=automata, channel=channel, name='Bob')
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'hello' (initiator)
      [+]   During transition 'hello', sending input symbol ('Bob-Hello')
      [+]   During transition 'hello', receiving expected output symbol ('Alice-Hello')
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'hello' (initiator)
      [+]   During transition 'hello', sending input symbol ('Bob-Hello')
      [+]   During transition 'hello', receiving expected output symbol ('Alice-Hello')
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Bob-Hello' corresponds to transition 'hello'
      [+]   During transition 'hello', choosing an output symbol ('Alice-Hello')
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Bob-Hello' corresponds to transition 'hello'
      [+]   During transition 'hello', choosing an output symbol ('Alice-Hello')
      [+]   Transition 'hello' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample2:

    **Dedicated automaton for a client and a server**

    The two actors are Alice and Bob. Bob is the initiator of the
    communication, meaning he sends the input symbols while Alice
    answers with its output symbols. The automaton here is
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello')
      [+]   During transition 'T1', receiving expected output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Hello')
      [+]   During transition 'T2', receiving expected output symbol ('Hello')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample3:

    **Modification of the emitted symbol by a client through a callback**

    The following example shows how to modify the symbol that is sent
    by the client to the server, through a callback method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifySymbol(available_symbols, current_symbol, current_preset, current_state,
    ...                     last_sent_symbol, last_sent_message, last_sent_structure,
    ...                     last_received_symbol, last_received_message, last_received_structure, memory):
    ...
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
    ...    preset = Preset(current_symbol)
    ...
    ...    # Building the output symbol by incrementing the value of the last
    ...    # received symbol
    ...    if last_received_symbol is not None and last_received_message is not None:
    ...        field_data = last_received_structure[last_received_symbol.fields[0].name]
    ...        field_data_int = int.from_bytes(field_data, byteorder='big')
    ...        field_data = int(field_data_int + 1).to_bytes(length=1, byteorder='big')
    ...        preset[current_symbol.fields[0]] = field_data
    ...    else:
    ...        preset[current_symbol.fields[0]] = b'\x02'
    ...
    ...    # Sending current symbol with specific preset
    ...    return (current_symbol, preset)
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'main transition' (initiator)
      [+]   During transition 'main transition', sending input symbol ('Symbol')
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol ('Symbol')
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'main transition' (initiator)
      [+]   During transition 'main transition', sending input symbol ('Symbol')
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol ('Symbol')
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T2'
      [+]   During transition 'T2', choosing an output symbol ('Symbol')
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Going to execute transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol


    .. _ActorExample4:

    **Modification of the emitted symbol by a server through a callback**

    The following example shows how to modify the symbol that is sent
    by the server in response to a client request, through a callback
    method.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new symbol
    >>> def cbk_modifySymbol(available_symbols, current_symbol, current_preset, current_state,
    ...                      last_sent_symbol, last_sent_message, last_sent_structure,
    ...                      last_received_symbol, last_received_message, last_received_structure, memory):
    ...
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
    ...    preset = Preset(current_symbol)
    ...
    ...    # Building the output symbol by incrementing the value of the last received symbol
    ...    if last_received_symbol is not None and last_received_message is not None:
    ...        field_data = last_received_structure[last_received_symbol.fields[0].name]
    ...        field_data_int = int.from_bytes(field_data, byteorder='big')
    ...        field_data = int(field_data_int + 1).to_bytes(length=1, byteorder='big')
    ...        preset[current_symbol.fields[0]] = field_data
    ...    else:
    ...        preset[current_symbol.fields[0]] = b'\x02'
    ...
    ...    # Sending current symbol with specific preset
    ...    return (current_symbol, preset)
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
    >>>
    >>> alice.start()
    >>> bob.start()
    >>>
    >>> time.sleep(1)
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog()) # doctest: +SKIP
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('symbol2')
      [+]   During transition 'T1', receiving expected output symbol ('symbol1')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('symbol2')
      [+]   During transition 'T2', receiving expected output symbol ('symbol1')
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog()) # doctest: +SKIP
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'symbol1' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('symbol1')
      [+]   During transition 'T1', modifying output symbol to 'symbol1', through callback
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'symbol1' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('symbol1')
      [+]   During transition 'T1', modifying output symbol to 'symbol1', through callback
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample5:

    **Modification of the current transition by a client through a callback**

    The following example shows how to modify the current transition
    of a client in its automaton, through a callback method.

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> import random
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message, last_sent_structure,
    ...                          last_received_symbol, last_received_message, last_received_structure, memory):
    ...
    ...     # Modify the selected transition
    ...     if nextTransition in availableTransitions:
    ...         availableTransitions.remove(nextTransition)
    ...     nextTransition = random.choice(availableTransitions)
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   Changing transition to 'T1' (initiator), through callback
      [+]   During transition 'T1', sending input symbol ('Symbol')
      [+]   During transition 'T1', receiving expected output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   Changing transition to 'T1' (initiator), through callback
      [+]   During transition 'T1', sending input symbol ('Symbol')
      [+]   During transition 'T1', receiving expected output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   Changing transition to 'T2' (initiator), through callback
      [+]   During transition 'T2', sending input symbol ('Symbol')
      [+]   During transition 'T2', receiving expected output symbol ('Symbol')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T3' (initiator)
      [+]   Changing transition to 'T4' (initiator), through callback
      [+]   During transition 'T4', sending input symbol ('Symbol')
      [+]   During transition 'T4', receiving expected output symbol ('Symbol')
      [+]   Transition 'T4' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample6:

    **Modification of the current transition of a server through a callback**

    The following example shows how to modify the current transition
    of a server in its automaton, through a callback method.

    >>> from netzob.all import *
    >>> Conf.apply()
    >>> import time
    >>> import random
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
    ...                          last_sent_symbol, last_sent_message, last_sent_structure,
    ...                          last_received_symbol, last_received_message, last_received_structure, memory):
    ...
    ...     # Modify the selected transition so that we change the next state
    ...     initialTransition = nextTransition
    ...     while True:
    ...         if len(availableTransitions) == 0:
    ...             break
    ...         if nextTransition.endState != current_state and initialTransition != nextTransition:
    ...             break
    ...         if nextTransition in availableTransitions:
    ...             availableTransitions.remove(nextTransition)
    ...         if len(availableTransitions) == 0:
    ...             break
    ...         nextTransition = random.choice(availableTransitions)
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a client)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Symbol')
      [+]   During transition 'T1', receiving expected output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Symbol')
      [+]   During transition 'T1', receiving expected output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   Changing transition to 'T2' (not initiator), through callback
      [+]   During transition 'T2', choosing an output symbol ('Symbol')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T3'
      [+]   Changing transition to 'T4' (not initiator), through callback
      [+]   During transition 'T4', choosing an output symbol ('Symbol')
      [+]   Transition 'T4' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Going to execute transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol


    .. _ActorExample7:

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
    >>> # Create the automaton
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
    >>> t2 = Transition(alice_s2, alice_s3, inputSymbol=None, outputSymbols=[bye], name="Bye")
    >>> t2.outputSymbolsReactionTime = {bye: 0.5}
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
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
    >>>
    >>> # Bob
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=3.)
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('HelloAlice')
      [+]   During transition 'T1', receiving expected output symbol ('HelloBob')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Empty Symbol')
      [+]   During transition 'T2', receiving expected output symbol ('Bye')
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'HelloAlice' corresponds to transition 'Hello'
      [+]   During transition 'Hello', choosing an output symbol ('HelloBob')
      [+]   Transition 'Hello' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Receiving no symbol (EmptySymbol) corresponds to transition 'Bye'
      [+]   During transition 'Bye', choosing an output symbol ('Bye')
      [+]   Transition 'Bye' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Going to execute transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol


    .. _ActorExample8:

    **How to catch all read symbol timeout**

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
    >>> # Create the automaton
    >>> s0 = State(name="Start state")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="Close state")
    >>> error_state = State(name="Error state")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> mainTransition = Transition(startState=s1, endState=s1,
    ...                             inputSymbol=symbol,
    ...                             outputSymbols=[symbol],
    ...                             name="T1")
    >>> mainTransition.outputSymbolsReactionTime = {symbol: 2.0}
    >>> closeTransition1 = CloseChannelTransition(startState=error_state, endState=s2, name="Close with error")
    >>> closeTransition2 = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> automata = Automata(s0, symbolList)
    >>>
    >>> def cbk_method(current_state, current_transition):
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
    >>> alice = Actor(automata=automata, channel=channel, initiator=False, name='Alice')
    >>>
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> bob = Actor(automata=automata, channel=channel, name='Bob')
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'Start state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello')
      [+]   During transition 'T1', timeout in reception triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close with error' (close channel)
      [+]   Transition 'Close with error' lead to state 'Close state'
      [+] At state 'Close state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'Start state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample9:

    **How to catch all receptions of unexpected symbols**

    The following example shows how to specify a global behavior, on
    all states and transitions, in order to catch reception of unexpected symbols (i.e. symbols that are known but not expected at this state/transition). In this example, we set a callback through the method :meth:`set_cbk_read_unexpected_symbol`. When an unexpected symbol is received, the defined callback will move the current
    position in the state machine to a specific state called 'error_state'.

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
    >>> def cbk_method(current_state, current_transition, received_symbol, received_message, received_structure):
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello1')
      [+]   During transition 'T1', receiving unexpected symbol triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Transition 'Close' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello1' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello1')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample10:

    **How to catch all receptions of unknown messages**

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
    >>> def cbk_method(current_state, current_transition, received_message):
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 10
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello1')
      [+]   During transition 'T1', receiving unknown symbol triggered a callback that lead to state 'Error state'
      [+] At state 'Error state'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Transition 'Close' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello1' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello2')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample11:

    **Message format fuzzing from an actor**

    This example shows the creation of a fuzzing actor, Bob, that will
    exchange messages with a Target, Alice. Messages generated from
    'Symbol 1' will be specifically fuzzed, but not those generated from
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
    ...                          last_sent_symbol, last_sent_message, last_sent_structure,
    ...                          last_received_symbol, last_received_message, last_received_structure, memory):
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
    >>> preset_symbol1 = Preset(symbol1)
    >>> preset_symbol1.fuzz(symbol1)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>> bob.fuzzing_presets = [preset_symbol1]
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Symbol 1')
      [+]   During transition 'T1', fuzzing activated
      [+]   During transition 'T1', receiving expected output symbol ('Symbol 2')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Symbol 2')
      [+]   During transition 'T2', receiving expected output symbol ('Symbol 2')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Unknown message b'\x00'' corresponds to transition 'None'
      [+]   Changing transition to 'T2' (not initiator), through callback
      [+]   During transition 'T2', choosing an output symbol ('Symbol 2')
      [+]   Transition 'T2' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol 2' corresponds to transition 'T2'
      [+]   Changing transition to 'T2' (not initiator), through callback
      [+]   During transition 'T2', choosing an output symbol ('Symbol 2')
      [+]   Transition 'T2' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample12:

    **Message format fuzzing from an actor, at a specific state**

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
    ...                          last_sent_symbol, last_sent_message, last_sent_structure,
    ...                          last_received_symbol, last_received_message, last_received_structure, memory):
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
    >>> preset_symbol1 = Preset(symbol1)
    >>> preset_symbol1.fuzz(symbol1)
    >>> preset_symbol2 = Preset(symbol2)
    >>> preset_symbol2.fuzz(symbol2)
    >>>
    >>> # Create Bob actor (a client)
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.fuzzing_presets = [preset_symbol1, preset_symbol2]
    >>> bob.fuzzing_states = ['S2']
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Symbol 1')
      [+]   During transition 'T1', receiving expected output symbol ('Symbol 1')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Symbol 2')
      [+]   During transition 'T2', fuzzing activated
      [+]   During transition 'T2', receiving expected output symbol ('Symbol 2')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol 1' corresponds to transition 'T1'
      [+]   Changing transition to 'T1' (not initiator), through callback
      [+]   During transition 'T1', choosing an output symbol ('Symbol 1')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Unknown message b'\x00'' corresponds to transition 'None'
      [+]   Changing transition to 'T2' (not initiator), through callback
      [+]   During transition 'T2', choosing an output symbol ('Symbol 2')
      [+]   Transition 'T2' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)


    .. _ActorExample13:

    **Several actors on the same communication channel**

    The following example shows the capability to create several
    actors that share the same underlying communication channel. In
    order for the communication channel to retrieve the actor
    concerned by received packets, a :attr:`cbk_select_data` callback
    is used.

    >>> from netzob.all import *
    >>> import time
    >>>
    >>> # First we create the symbols
    >>> bobSymbol = Symbol(name="Bob-Hello", fields=[Field(b"bob>hello")])
    >>> aliceSymbol = Symbol(name="Alice-Hello", fields=[Field(b"alice>hello")])
    >>> symbolList = [aliceSymbol, bobSymbol]
    >>>
    >>> # Create the automaton
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
    >>> def cbk_select_data_bob(data):
    ...     if data[:6] == b"alice>":
    ...         return True
    ...     else:
    ...         return False
    >>>
    >>> def cbk_select_data_alice(data):
    ...     if data[:4] == b"bob>":
    ...         return True
    ...     else:
    ...         return False
    >>>
    >>> # Create actors: Alice (a server) and Bob (a client)
    >>> channel = IPChannel(localIP="127.0.0.1", remoteIP="127.0.0.1")
    >>> alice = Actor(automata=automata, channel=channel, name='Alice')
    >>> alice.cbk_select_data = cbk_select_data_alice
    >>> alice.initiator = False
    >>>
    >>> bob = Actor(automata=automata, channel=channel, name='Bob')
    >>> bob.cbk_select_data = cbk_select_data_bob
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> channel.start()
    >>> time.sleep(0.5)
    >>> if channel.isActive():
    ...     alice.start()
    ...     time.sleep(0.5)
    ...     bob.start()
    ...     time.sleep(1)
    ...     bob.wait()
    ...     alice.stop()
    >>> channel.stop()

    """

    @public_api
    def __init__(self,
                 automata,          # type: Automata
                 channel,           # type: AbstractType
                 initiator=True,    # type: bool
                 name="Actor",      # type: str
                 ):
        # type: (...) -> None
        Thread.__init__(self)

        # Initialize public variables from parameters
        self.automata = automata.copy()
        self.initiator = initiator
        self.name = name

        # Initialize other public variables
        self.fuzzing_presets = []      # Fuzzing configuration used at dedicated states
        self.fuzzing_states = []       # Tell the actor in which states fuzzing should be activated
        self.memory = None             # Context of the actor
        self.presets = []              # Variable used for Actor symbol configuration
        self.cbk_select_data = None    # Variable used to tell if received data is interesting for the actor
        self.target_state = None       # Variable used to tell the actor to return at a specific state
        self.current_state = None      # Variable used to keep track of the current state
        self.nbMaxTransitions = None   # Max number of transitions the actor can browse (None means no limit)

        # Initialize local private variables
        self.keep_open = True         # Tell the actor to stay open after it has exiting the visit loop
        self.__stopEvent = Event()
        self.__currentnbTransitions = 0  # Used to track the current number of transitions

        # Initialize local variables
        self.visit_log = []  # Visit log, which contains the information regarding the different transitions and states visited by the actor
        self.abstractionLayer = AbstractionLayer(channel, self.automata.symbols, actor=self)
        self.current_state = self.automata.initialState

    def __str__(self):
        return str(self.name)

    def run(self):
        """Start the visit of the automaton from its initial state."""

        while not self.__stopEvent.is_set():
            try:
                do_stop = self.execute_transition()
                if do_stop:
                    self.stop()
                    break
            except ActorStopException:
                break
            except Exception as e:
                self._logger.debug("Exception raised for actor '{}' when on the execution of state {}.".format(self.name, self.current_state))
                self._logger.error("Exception error for actor '{}': {}".format(self.name, str(e)))
                self._logger.warning(traceback.format_exc())
                self.stop()
                break
        self._logger.debug("Actor '{}' has finished to execute".format(self.name))

    @public_api
    def execute_transition(self):
        r"""Execute the next transition in the automaton.

        :return: A boolean telling if the transition execution triggered an exit condition of the visit loop of the automaton. Return ``True`` if an exit condition is triggered.
        :rtype: :class:`bool`

        """

        self._logger.debug("Current state for actor '{}': '{}'.".format(self.name, self.current_state))

        if self.current_state is None:
            self._logger.debug("Cannot execute transition as current state is None, for actor '{}'".format(self.name))
            return True

        # Execute state action
        self.current_state = self.current_state.execute(self)

        if self.current_state is None:
            self._logger.debug("The execution of transition did not returned a state, for actor '{}'".format(self.name))
            return True

        if self.current_state is not None and self.target_state is not None and self.target_state.name == self.current_state.name:
            self._logger.debug("[actor='{}'] Reaching the targeted state '{}'".format(self.name, self.target_state))
            self.visit_log.append("  [+] At state '{}', we reached the targeted state '{}', so we stop".format(self.current_state, self.target_state))
            return True

        self.__currentnbTransitions += 1
        if self.nbMaxTransitions is not None and self.__currentnbTransitions >= self.nbMaxTransitions:
            self._logger.debug("[actor='{}'] Max number of transitions ({}) reached".format(self.name, self.nbMaxTransitions))
            self.visit_log.append("  [+] At state '{}', we reached the max number of transitions ({}), so we stop".format(self.current_state, self.nbMaxTransitions))
            return True

        return False

    @public_api
    def stop(self):
        """Stop the visit loop of the automaton.

        """
        self._logger.debug("[actor='{}'] Stopping the current actor".format(self.name))

        self.__stopEvent.set()

        # By default, we don't close the communication channel when
        # stoping the actor visit loop, because we want by default to
        # be able to then get manual control of the automata.
        if self.keep_open:
            return

        try:
            self.abstractionLayer.closeChannel()
        except Exception as e:
            self._logger.error(e)

    @public_api
    def wait(self):
        """Wait for the current actor to finish the visit loop of the automaton.

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

        :return: An string containing the visit log.
        :rtype: :class:`str`

        """
        result = "Activity log for actor '{}' ({}):\n".format(self.name, "initiator" if self.initiator else "not initiator")
        result += "\n".join(self.visit_log)
        return result

    ## Public properties ##

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
    def name(self):
        return self.__name

    @name.setter  # type: ignore
    @typeCheck(str)
    def name(self, name):
        self.__name = name

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
    def fuzzing_presets(self):
        return self.__fuzzing_presets

    @fuzzing_presets.setter  # type: ignore
    @typeCheck(list)
    def fuzzing_presets(self, fuzzing_presets):
        for preset in fuzzing_presets:
            if not isinstance(preset, Preset):
                raise TypeError("The configuration should be a list of Preset objects, not a '{}'".format(fuzzing_presets))
        self.__fuzzing_presets = fuzzing_presets

    @public_api
    @property
    def fuzzing_states(self):
        return self.__fuzzing_states

    @fuzzing_states.setter  # type: ignore
    @typeCheck(list)
    def fuzzing_states(self, fuzzing_states):
        self.__fuzzing_states = fuzzing_states

    @public_api
    @property
    def memory(self):
        return self.__memory

    @memory.setter  # type: ignore
    @typeCheck(Memory)
    def memory(self, memory):
        if memory is None:
            memory = Memory()
        self.__memory = memory

    @public_api
    @property
    def presets(self):
        return self.__presets

    @presets.setter  # type: ignore
    @typeCheck(list)
    def presets(self, presets):
        for preset in presets:
            if not isinstance(preset, Preset):
                raise TypeError("The configuration should be a list of Preset objects, not a '{}'".format(presets))
        self.__presets = presets

    @public_api
    @property
    def cbk_select_data(self):
        return self.__cbk_select_data

    @cbk_select_data.setter  # type: ignore
    def cbk_select_data(self, cbk_select_data):
        self.__cbk_select_data = cbk_select_data

    @public_api
    @property
    def target_state(self):
        return self.__target_state

    @target_state.setter  # type: ignore
    @typeCheck(AbstractState)
    def target_state(self, target_state):
        self.__target_state = target_state

    @public_api
    @property
    def current_state(self):
        return self.__current_state

    @current_state.setter  # type: ignore
    @typeCheck(AbstractState)
    def current_state(self, current_state):
        self.__current_state = current_state

    @public_api
    @property
    def nbMaxTransitions(self):
        return self.__nbMaxTransitions

    @nbMaxTransitions.setter  # type: ignore
    @typeCheck(int)
    def nbMaxTransitions(self, nbMaxTransitions):
        self.__nbMaxTransitions = nbMaxTransitions


def _test_client_and_server_actors():
    r"""

    Two actors are created: Alice and Bob. Bob is the initiator of the
    communication (he's a client), meaning he sends the input symbols while Alice
    answers with its output symbols (she's a server). The automaton is
    very simple, and different for each actor. We first open the
    channel, and allow Bob to send the data ``"hello"`` multiple
    times. Alice answers every time with the data ``"hello"``.

    >>> from netzob.all import *
    >>> Conf.seed = 10
    >>> Conf.apply()
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello')
      [+]   During transition 'T1', receiving expected output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Hello')
      [+]   During transition 'T2', receiving expected output symbol ('Hello')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Hello' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)

    """


def _test_context():
    r"""

    Two actors are created: Alice and Bob. Bob is the initiator of the
    communication (he's a client), meaning he sends the input symbols while Alice
    answers with its output symbols (she's a server). The automaton is
    very simple, and different for each actor. We first open the
    channel, and allow Bob to send the data ``"hello"`` multiple
    times. Alice answers every time with the data ``"hello"``.

    We also create a context, through a Memory object, that allows to persist a variable accross states and transitions changes.
    An integer variable is created and memorized for Alice actor. Its value is incremented at each transition.

    >>> from netzob.all import *
    >>> Conf.seed = 10
    >>> Conf.apply()
    >>> import time
    >>>
    >>> # We create bob's symbol
    >>> f1 = Field("hello", name="Bob hello")
    >>> f2 = Field(uint32(), name="Bob integer")
    >>> symbol = Symbol(name="Hello", fields=[f1, f2])
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
    >>>
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
    >>> # We create alice's symbols
    >>>
    >>> # Input symbol
    >>> alice_f1_input = Field("hello", name="Alice Field f1")
    >>> alice_f2_input = Field(uint32(), name="Alice Field f2")
    >>> alice_symbol_input = Symbol(name="Alice Input Symbol", fields=[alice_f1_input, alice_f2_input])
    >>> alice_symbolList = [alice_symbol_input]
    >>>
    >>> # Output symbol
    >>> alice_var_integer = Data(uint32(default=1), scope=Scope.MESSAGE, name='Alice integer')
    >>> alice_f1_output = Field("hello", name="Alice Field f1")
    >>> alice_f2_output = Field(alice_var_integer, name="Alice Field f2")
    >>> alice_symbol_output = Symbol(name="Alice Output Symbol", fields=[alice_f1_output, alice_f2_output])
    >>> alice_symbolList = [alice_symbol_input, alice_symbol_output]
    >>>
    >>> # Create Alice's automaton
    >>> alice_s0 = State(name="S0")
    >>> alice_s1 = State(name="S1")
    >>> alice_s2 = State(name="S2")
    >>>
    >>> # Creation of the context
    >>> alice_memory = Memory()
    >>> alice_memory.memorize(alice_var_integer, alice_var_integer.dataType.generate())
    >>>
    >>> # Creation of a callback function that will be called after each transition, to update the context
    >>> def cbk_action(symbol_to_send, data, data_structure, operation, current_state, memory):
    ...     if operation == Operation.SPECIALIZE:
    ...         var_integer_bytes = data_structure['Alice Field f2']
    ...         var_integer = int.from_bytes(var_integer_bytes, byteorder='big')
    ...         print("[WRITE] Current value for f2: {}".format(var_integer))
    ...         var_integer += 1
    ...         var_integer_bytes = var_integer.to_bytes(4, byteorder='big')
    ...         memory.memorize(alice_var_integer, var_integer_bytes)
    >>>
    >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
    >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
    ...                                   inputSymbol=alice_symbol_input, outputSymbols=[alice_symbol_output],
    ...                                   name="T1")
    >>> # Set callback function on transitions
    >>> alice_mainTransition.add_cbk_action(cbk_action)
    >>>
    >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
    >>> alice_automata = Automata(alice_s0, alice_symbolList)
    >>>
    >>> automata_ascii = alice_automata.generateASCII()
    >>> print(automata_ascii)
    #=========================#
    H           S0            H
    #=========================#
      |
      | OpenChannelTransition
      v
    +-------------------------+   T1 (Alice Input Symbol;{Alice Output Symbol})
    |                         | ------------------------------------------------+
    |           S1            |                                                 |
    |                         | <-----------------------------------------------+
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 5
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
    >>> alice.memory = alice_memory
    >>>
    >>> import io, contextlib
    >>> stdout = io.StringIO()
    >>> with contextlib.redirect_stdout(stdout):
    ...     alice.start()
    ...     time.sleep(0.5)
    ...     bob.start()
    ...     time.sleep(1)
    >>> print(stdout.getvalue(), end='')
    [WRITE] Current value for f2: 1
    [WRITE] Current value for f2: 2
    [WRITE] Current value for f2: 3
    [WRITE] Current value for f2: 4
    >>>
    >>> bob.stop()
    >>> alice.stop()
    >>>
    >>> print(bob.generateLog())
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T1' (initiator)
      [+]   During transition 'T1', sending input symbol ('Hello')
      [+]   During transition 'T1', receiving expected output symbol ('Hello')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Hello')
      [+]   During transition 'T2', receiving expected output symbol ('Hello')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Hello')
      [+]   During transition 'T2', receiving expected output symbol ('Hello')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'T2' (initiator)
      [+]   During transition 'T2', sending input symbol ('Hello')
      [+]   During transition 'T2', receiving expected output symbol ('Hello')
      [+]   Transition 'T2' lead to state 'S2'
      [+] At state 'S2', we reached the max number of transitions (5), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Alice Input Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Alice Output Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Alice Input Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Alice Output Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Alice Input Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Alice Output Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Alice Input Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Alice Output Symbol')
      [+]   Transition 'T1' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)

    """


def _test_callback_modify_symbol():
    r"""

    The following example shows how to modify the symbol that is sent
    by the client to the server, through a callback method.

    >>> from netzob.all import *
    >>> Conf.seed = 10
    >>> Conf.apply()
    >>> import time
    >>>
    >>> # Creation of a callback function that returns a new transition
    >>> def cbk_modifySymbol(available_symbols, current_symbol, current_preset, current_state,
    ...                     last_sent_symbol, last_sent_message, last_sent_structure,
    ...                     last_received_symbol, last_received_message, last_received_structure, memory):
    ...
    ...    if last_received_symbol:
    ...        last_received_symbol_name = last_received_symbol.name
    ...    else:
    ...        last_received_symbol_name = None
    ...    preset = Preset(current_symbol)
    ...
    ...    # Building the output symbol by incrementing the value of the last
    ...    # received symbol
    ...    if last_received_symbol is not None and last_received_message is not None:
    ...        field_data = last_received_structure[last_received_symbol.fields[0].name]
    ...        field_data_int = int.from_bytes(field_data, byteorder='big')
    ...        field_data = int(field_data_int + 1).to_bytes(length=1, byteorder='big')
    ...        preset[current_symbol.fields[0]] = field_data
    ...    else:
    ...        preset[current_symbol.fields[0]] = b'\x02'
    ...
    ...    # Sending current symbol with specific preset
    ...    return (current_symbol, preset)
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
    >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
    >>> bob.nbMaxTransitions = 3
    >>>
    >>> # Create Alice actor (a server)
    >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
    >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
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
    Activity log for actor 'Bob' (initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'main transition' (initiator)
      [+]   During transition 'main transition', sending input symbol ('Symbol')
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol ('Symbol')
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'main transition' (initiator)
      [+]   During transition 'main transition', sending input symbol ('Symbol')
      [+]   During transition 'main transition', modifying input symbol to 'Symbol', through callback
      [+]   During transition 'main transition', receiving expected output symbol ('Symbol')
      [+]   Transition 'main transition' lead to state 'S1'
      [+] At state 'S1', we reached the max number of transitions (3), so we stop
    >>> print(alice.generateLog())
    Activity log for actor 'Alice' (not initiator):
      [+] At state 'S0'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Open' (open channel)
      [+]   Going to execute transition 'Open'
      [+]   Transition 'Open' lead to state 'S1'
      [+] At state 'S1'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T1'
      [+]   During transition 'T1', choosing an output symbol ('Symbol')
      [+]   Transition 'T1' lead to state 'S2'
      [+] At state 'S2'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Waiting for an input symbol to decide the transition (not initiator)
      [+]   Input symbol 'Symbol' corresponds to transition 'T2'
      [+]   During transition 'T2', choosing an output symbol ('Symbol')
      [+]   Transition 'T2' lead to state 'S3'
      [+] At state 'S3'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol
      [+]   Picking transition 'Close' (close channel)
      [+]   Going to execute transition 'Close'
      [+]   Transition 'Close' lead to state 'S4'
      [+] At state 'S4'
      [+]   Randomly choosing a transition to execute or to wait for an input symbol

    """
