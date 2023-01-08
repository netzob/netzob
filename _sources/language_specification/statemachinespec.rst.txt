.. _statemachinespec:

State Machine Modeling
======================

State Machine Modeling Concepts
-------------------------------

The ZDL language can be used to specify a **state machine**, or automaton, for a protocol. A state machine is based on two components: **States** and **Transitions**. A state represents the status of a service, and expects conditions to trigger the execution of a transition. A transition is a list of actions that will be executed when a condition is met at a specific state (such as the receipt of a network message). The list of actions may contain sending a network message, changing the value of session or global variables, moving to another state in the automaton, etc.

The language defines three kinds of transition in an automaton:

* **Standard transitions**: this represents a transition between two
  states (an initial state and an end state) in an automaton. The
  initial state and the end state can be the same.
* **Opening channel transitions**: this represents a transition which, when
  executed, requests to open the current underlying communication channel.
* **Closing channel transitions**: this represents a transition which, when
  executed, requests to close the current underlying communication channel.

In the Netzob library, a state machine relies on symbols to trigger transitions between states. In order to represent the state machine structure, the library relies on a mathematical model based on a **Mealy machine** (cf. https://en.wikipedia.org/wiki/Mealy_machine). The library leverages this model by associating, for each transition, an input symbol and a list of output symbols, as shown on the figure below.

.. figure:: img/state_machine.*
   :align: center

   Example of State Machine modeling with states, transitions, input and output symbols.

Depending on the peer point of view, either an initiator (e.g. a client that starts a communication with a remote service) or a non initiator (e.g. a service that waits for input messages), the interpretation of the state machine is different. This intepretation is done with a state machine visitor that is called an :class:`~netzob.Simulator.Actor.Actor` in the API.

From an **initiator point of view**, when the actor is at a specific state in the automaton, a random transition is taken amongst the available transitions. In the above example, two transitions, ``T1`` and ``T2``, are available at the state ``S1``. Then, the input symbol of the picked transition is specialized into a message and this message is emitted to the target. If the target replies, the actor abstracts the received message into a symbol, and checks if this symbol corresponds to one of the expected output symbols. If it matches, the transition succeeds and thus leads to the end state of the transition. In the above example, the transition ``T2`` would lead to the state ``S3``. If no response comes from the target, or if a wrong message is received, we leave the automaton.

From a **non initiator point of view**, when at a specific state in the automaton, the actor waits for a network message. When one network message is received, it is abstracted into a symbol. Then, we retrieve the transition that has this symbol as input symbol. When a transition is retrieved, we randomly pick one symbol amongst the output symbols, and send this symbol to the remote peer. Finally, the transition leads to the end state of the transition.

When the actor has to select a transition, or when the actor has to identify the current transition according to the received message, it is possible to influence this choice through the help of callback functions.

Likewise, when the actor sends the input symbol, or when the actor sends an output symbol, it is possible to influence the selection of the symbol, through the help of callback functions or selection probability weight.

In order to model hybrid state machines where a peer is able to send or receive symbols depending on the context, it is possible to change the initiator behavior at specific transitions. This is done through the :attr:`~netzob.Model.Grammar.Transitions.Transition.Transition.inverseInitiator` attribute on :class:`~netzob.Model.Grammar.Transitions.Transition.Transition` objects. When setting this attribute to ``True`` on a transition, an actor will inverse the way symbols are exchanged (e.g. an initiator actor will first wait for an input symbol and then send one of the output symbols).

A **Memory** (see :class:`~netzob.Model.Vocabulary.Domain.Variables.Memory.Memory`) is used to keep track of a context for a specific communication. This memory can leverage variable from the protocol or even the environment. The memory is initialized at the beginning of the communication, and its internal state evolves throughout the exchanged messages.


.. Besides, two extensions allow refining the state machine model:

.. * The capability to define a reaction time on a transition. This reaction time between receiving a specific symbol and sending the output symbol will be enforced by the library.
.. * The capability to provide indeterminism on output symbols. The library enables the user to model a transition which, for a sequence of input symbols, associates many sequences of output symbols. The chosen sequence of output symbol is selected randomly.

.. raw:: latex

   \newpage


Modeling States
---------------

In the API, automaton states are modeled through the State class.

.. autoclass:: netzob.Model.Grammar.States.State.State
   :members: copy

.. raw:: latex

   \newpage

Modeling Transitions
--------------------

The available transitions are detailed in this chapter.

.. autoclass:: netzob.Model.Grammar.Transitions.Transition.Transition(startState, endState, inputSymbol=None, outputSymbols=None, name=None)
   :members: copy

.. autoclass:: netzob.Model.Grammar.Transitions.OpenChannelTransition.OpenChannelTransition(startState, endState, name=None)
   :members: copy

.. autoclass:: netzob.Model.Grammar.Transitions.CloseChannelTransition.CloseChannelTransition(startState, endState, name=None)
   :members: copy

.. raw:: latex

   \newpage


Taking Control over Emitted Symbol and Selected Transition
----------------------------------------------------------

A state may have different available transitions to other states. It
is possible to filter those available transitions in order to limit
them or to force a specific transition to be taken. The filtering
capability works by adding callbacks through the
:meth:`add_cbk_filter_transitions` method on a
:class:`~netzob.Model.Grammar.States.State.State` instance.


.. automethod:: netzob.Model.Grammar.States.State.State.add_cbk_filter_transitions

When a transition is selected, it is possible to modify it by adding
callbacks through the :meth:`add_cbk_modify_transition` method on a
:class:`~netzob.Model.Grammar.States.State.State` instance.


.. automethod:: netzob.Model.Grammar.States.State.State.add_cbk_modify_transition

Besides, during execution of a transition, it is possible to change
the symbol that will be sent to the remote peer, by adding callbacks
through the :meth:`add_cbk_modify_symbol` method on a
:class:`~netzob.Model.Grammar.Transitions.Transition.Transition` instance.

.. automethod:: netzob.Model.Grammar.Transitions.Transition.Transition.add_cbk_modify_symbol


Executing Actions during Transitions
------------------------------------

It is possible to execute specific actions during transitions, after sending or receiving a symbol, by adding
callbacks through the :meth:`add_cbk_action` method on a
:class:`~netzob.Model.Grammar.Transitions.Transition.Transition` instance. The typical usage of this callback is that it is possible to manipulate the memory context of the automaton after sending or receiving a symbol.

When specifying such callback on a transition, this callback is then called twice for a transition: in an initiator context, the callback is first called after sending the input symbol, and then called after receiving one of the output symbols; while in a non initiator context, the callback is called after receiving the input symbol, and then called after sending one of the output symbols.

.. automethod:: netzob.Model.Grammar.Transitions.Transition.Transition.add_cbk_action


Summary of States and Transitions Processing
--------------------------------------------

The following figure gives a summary of the sequence of operations during states and transitions processing.

.. figure:: img/Grammar_procedure.*
   :align: center
   :scale: 70 %

   Sequence of operations during states and transitions processing


Modeling Automata
-----------------

In the API, an automaton is made of a list of permitted symbols
and an initial state. An automaton is modeled using the Automata class.

.. autoclass:: netzob.Model.Grammar.Automata.Automata
   :members: getStates, getState, getTransitions, getTransition, set_cbk_read_symbol_timeout,
             set_cbk_read_unexpected_symbol, set_cbk_read_unknown_symbol,
             generateDotCode, generateASCII, copy

.. raw:: latex

   \newpage
