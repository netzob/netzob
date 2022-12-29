.. _actor:

Visiting a State Machine with an Actor
======================================

An **actor** (see :class:`~netzob.Simulator.Actor.Actor`) is a high-level representation of an entity that participates in a communication. An actor communicates with remote peers, in respect to an automaton (an actor is in fact a visitor of an automaton), and exchanges abstract representation of messages called Symbols.

In the API, a visitor of a state machine is modeled using the Actor
class.

.. autoclass:: netzob.Simulator.Actor.Actor

.. Note: we comment this section, as the figure is not referenced in the language specification.

   .. figure:: ./img/transition_without_input_symbol_sequence.png
      :align: center

      Sequence diagram showing state transitions according to messages exchanged
      between Alice and Bob.

.. raw:: latex

   \newpage
