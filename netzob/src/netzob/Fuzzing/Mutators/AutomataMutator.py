# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
from enum import Enum

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Fuzzing.Mutator import Mutator, MutatorMode
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Grammar.Automata import Automata
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.Transitions.OpenChannelTransition import OpenChannelTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition
from netzob.Model.Grammar.States.State import State  # noqa: F401


class AutomataMutatorStrategy(Enum):
    """The :class:`AutomataMutator` strategy enumeration."""
    __repr__ = Enum.__str__
    RANDOM = 1
    """Randomly insert transitions between states of the original automaton."""
    FULL = 2
    """At each state of the automaton, it is possible to reach any states with any input symbols."""
    ONESTATE = 3
    """Build an automaton with one main state that accepts every symbols."""
    TARGETED = 4
    """Build an automaton similar to the original one, where a list of targeted states, given in parameters, will accept every symbols."""


class AutomataMutator(Mutator):
    """The AutomataMutator is used to mutate an existing state machine.

    """

    def __init__(self,
                 automata,  # type: Automata
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT):
        super().__init__(mode=MutatorMode.MUTATE, generator=generator, seed=seed)

        # Initialize variable from parameters
        self.automata = automata

        # Initialize random generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed)


    ## Public API

    @public_api
    def mutate(self,
               strategy=AutomataMutatorStrategy.RANDOM,  # type: AutomataMutatorStrategy
               target_states=None
               ) -> Automata:
        r"""This is the mutation method of the automaton. This method returns
        a new automaton that may be used for fuzzing purpose.

        The mutate method expects some parameters:

        :param strategy: The strategy used to build the new automaton.

                         The following strategies are available:

                         * :attr:`AutomataMutatorStrategy.RANDOM`: Randomly insert and remove transitions between states of the original automaton,
                         * :attr:`AutomataMutatorStrategy.FULL`: At each state of the automaton, it is possible to reach any states,
                         * :attr:`AutomataMutatorStrategy.ONESTATE`: Build an automaton with one main state that accepts every symbols.
                         * :attr:`AutomataMutatorStrategy.TARGETED`: Build an automaton similar to the original one, where a targeted state, given in parameters, will accept every symbols.

                         Default strategy is :attr:`AutomataMutatorStrategy.RANDOM`.
        :param target_states: The states considered for targeted fuzzing (should be used with :attr:`AutomataMutatorStrategy.TARGETED`).
        :type strategy: :class:`AutomataMutatorStrategy`, optional
        :type target_states: :class:`list` of :class:`str`, optional
        :return: The mutated automata.
        :rtype: :class:`Automata <netzob.Model.Grammar.Automata>`


        **Basic example of automata fuzzing**

        Mutators may be used in order to create fuzzed/mutated automaton.

        The following code shows the creation of the new automaton with
        random transitions between the existing states:

        >>> from netzob.all import *
        >>> import time
        >>> sym1 = Symbol([Field(String(nbChars=3))], name='Sym1')
        >>> sym2 = Symbol([Field(String(nbChars=5))], name='Sym2')
        >>> vocabulary = [sym1, sym2]
        >>> s0 = State(name="s0")
        >>> s1 = State(name="s1")
        >>> s2 = State(name="s2")
        >>> s3 = State(name="s3")
        >>> s4 = State(name="s4")
        >>> t0 = OpenChannelTransition(startState=s0, endState=s1,
        ...                            name="t0")
        >>> t1 = Transition(startState=s1, endState=s1,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t1")
        >>> t2 = Transition(startState=s1, endState=s2,
        ...                 inputSymbol=sym2, outputSymbols=[sym2],
        ...                 name="t2")
        >>> t3 = Transition(startState=s2, endState=s3,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t3")
        >>> t4 = CloseChannelTransition(startState=s2, endState=s4,
        ...                             name="t4")
        >>>
        >>> automata = Automata(s0, vocabulary=vocabulary)
        >>> automata_ascii = automata.generateASCII()
        >>> print(automata_ascii)
                                         #========================#
                                         H           s0           H
                                         #========================#
                                           |
                                           | OpenChannelTransition
                                           v
                                         +------------------------+   t1 (Sym1;{Sym1})
                                         |                        | -------------------+
                                         |           s1           |                    |
                                         |                        | <------------------+
                                         +------------------------+
                                           |
                                           | t2 (Sym2;{Sym2})
                                           v
        +----+  CloseChannelTransition   +------------------------+
        | s4 | <------------------------ |           s2           |
        +----+                           +------------------------+
                                           |
                                           | t3 (Sym1;{Sym1})
                                           v
                                         +------------------------+
                                         |           s3           |
                                         +------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate a random automaton
        >>>
        >>> mutator = AutomataMutator(automata)
        >>> mutatedAutomata = mutator.mutate()
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
                                                #==============================#
                                                H              s0              H
                                                #==============================#
                                                  |
                                                  | OpenChannelTransition
                                                  v
                  t_random (Sym2;{Sym1,Sym2})   +------------------------------+   t1 (Sym1;{Sym1})
                +------------------------------ |                              | -------------------+
                |                               |              s1              |                    |
                +-----------------------------> |                              | <------------------+
                                                +------------------------------+
                                                  |
                                                  | t2 (Sym2;{Sym2})
                                                  v
        +----+  CloseChannelTransition          +------------------------------+
        | s4 | <------------------------------- |              s2              | -+
        +----+                                  +------------------------------+  |
                                                  |                               |
                                                  | t_random (Sym2;{Sym1,Sym2})   | t3 (Sym1;{Sym1})
                                                  v                               |
                                                +------------------------------+  |
                                                |              s3              | <+
                                                +------------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate a full automaton
        >>>
        >>> mutator = AutomataMutator(automata)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.FULL)
        >>>
        >>> # The ASCII representation is not displayed as it is too big
        >>>
        >>> # Generate an automaton with one main state
        >>>
        >>> mutator = AutomataMutator(automata)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.ONESTATE)
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
                                          #========================#
                                          H     Initial state      H
                                          #========================#
                                            |
                                            | OpenChannelTransition
                                            v
            t_random (Sym2;{Sym1,Sym2})   +------------------------+   t_random (Sym1;{Sym1,Sym2})
          +------------------------------ |                        | ------------------------------+
          |                               |       Main state       |                               |
          +-----------------------------> |                        | <-----------------------------+
                                          +------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate an automaton with targeted fuzzing on one specific state
        >>>
        >>> mutator = AutomataMutator(automata)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.TARGETED, target_states=['s2'])
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
                                          #========================#
                                          H           s0           H
                                          #========================#
                                            |
                                            | OpenChannelTransition
                                            v
                                          +------------------------+   t1 (Sym1;{Sym1})
                                          |                        | ------------------------------+
                                          |           s1           |                               |
                                          |                        | <-----------------------------+
                                          +------------------------+
                                            |
                                            | t2 (Sym2;{Sym2})
                                            v
            t_random (Sym2;{Sym1,Sym2})   +------------------------+   t_random (Sym1;{Sym1,Sym2})
          +------------------------------ |                        | ------------------------------+
          |                               |           s2           |                               |
          +-----------------------------> |                        | <-----------------------------+
                                          +------------------------+
        <BLANKLINE>


        **Combining message formats and automata fuzzing**

        By combining message formats and automata fuzzing, it is possible
        to fuzz specific message formats at specific states in the
        automaton.

        The following code shows the creation of a mutated automaton
        (based on the previous example automaton) with targeted
        automaton mutations at state 's2', and with a precision concerning the
        state at which fuzzing of message formats will be
        performed. Here, the message format fuzzing only applies at
        state 's2'. An actor is also created to simulate a target.

        >>> # Creation of a mutated automaton
        >>> mutator = AutomataMutator(automata, seed=42)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.TARGETED, target_states=[s2.name])
        >>>
        >>> # Define fuzzing configuration
        >>> fuzz = Fuzz()
        >>> fuzz.set(sym1)
        >>> fuzz.set(sym2)
        >>>
        >>> # Creation of an automaton visitor/actor and a channel on which to emit the fuzzed symbol
        >>> bob_channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
        >>> bob_abstractionLayer = AbstractionLayer(bob_channel, vocabulary)
        >>> bob_actor = Actor(automata=mutatedAutomata, initiator=True, abstractionLayer=bob_abstractionLayer, fuzz=fuzz, fuzz_states=[s2.name], name='Fuzzer')
        >>> bob_actor.nbMaxTransitions = 3
        >>>
        >>> # Create Alice's automaton
        >>> alice_s0 = State(name="s0")
        >>> alice_s1 = State(name="s1")
        >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
        >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s1,
        ...                                inputSymbol=sym1, outputSymbols=[sym1, sym2],
        ...                                name="T1")
        >>> alice_transition2 = Transition(startState=alice_s1, endState=alice_s1,
        ...                                inputSymbol=sym2, outputSymbols=[sym2, sym2],
        ...                                name="T2")
        >>> alice_automata = Automata(alice_s0, vocabulary)
        >>>
        >>> # Creation of an automaton visitor/actor and a channel on which to receive the fuzzing traffic
        >>> alice_channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
        >>> alice_abstractionLayer = AbstractionLayer(alice_channel, vocabulary)
        >>>
        >>> # Creation of a callback function that returns a new transition
        >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
        ...                          last_sent_symbol, last_sent_message,
        ...                          last_received_symbol, last_received_message):
        ...     if nextTransition is None:
        ...         return t2
        ...     else:
        ...         return nextTransition
        >>>
        >>> alice_automata.getState('s1').add_cbk_modify_transition(cbk_modifyTransition)
        >>>
        >>> alice_actor = Actor(automata=alice_automata, initiator=False, abstractionLayer=alice_abstractionLayer, name='Target')
        >>>
        >>> # We start the targeted actor
        >>> alice_actor.start()
        >>> time.sleep(0.5)
        >>>
        >>> # We start the visitor, thus the fuzzing of message formats will be applied when specific states are reached
        >>> bob_actor.start()
        >>> time.sleep(1)
        >>>
        >>> bob_actor.stop()
        >>> alice_actor.stop()
        >>>
        >>> print(bob_actor.generateLog())
        Activity log for actor 'Fuzzer':
          [+] At state 's0'
          [+]   Picking transition 't0'
          [+]   Transition 't0' lead to state 's1'
          [+] At state 's1'
          [+]   Picking transition 't2'
          [+]   During transition 't2', sending input symbol 'Sym2'
          [+]   During transition 't2', receiving expected output symbol 'Sym2'
          [+]   Transition 't2' lead to state 's2'
          [+] At state 's2'
          [+]   Picking transition 't_random'
          [+]   During transition 't_random', sending input symbol 'Sym1'
          [+]   During transition 't_random', fuzzing activated
          [+]   During transition 't_random', receiving expected output symbol 'Sym2'
          [+]   Transition 't_random' lead to state 's2'
          [+] At state 's2', we reached the max number of transitions (3), so we stop
        >>> print(alice_actor.generateLog())
        Activity log for actor 'Target':
          [+] At state 's0'
          [+]   Picking transition 'Open'
          [+]   Transition 'Open' lead to state 's1'
          [+] At state 's1'
          [+]   Receiving input symbol 'Sym2', which corresponds to transition 'T2'
          [+]   Changing transition to 'T2', through callback
          [+]   During transition 'T2', choosing output symbol 'Sym2'
          [+]   Transition 'T2' lead to state 's1'
          [+] At state 's1'
          [+]   Receiving input symbol 'Unknown message b'$ENV{"HOME"}\x00       '', which corresponds to transition 'None'
          [+]   Changing transition to 't2', through callback
          [+]   During transition 't2', choosing output symbol 'Sym2'
          [+]   Transition 't2' lead to state 's2'

        """
        if strategy == AutomataMutatorStrategy.RANDOM:
            return self._mutate_random()
        elif strategy == AutomataMutatorStrategy.FULL:
            return self._mutate_full()
        elif strategy == AutomataMutatorStrategy.ONESTATE:
            return self._mutate_onestate()
        elif strategy == AutomataMutatorStrategy.TARGETED:
            if target_states is None:
                raise Exception("'target_states' parameter should be a list of State named, not None")
            return self._mutate_targeted(target_states)
        else:
            raise ValueError("Unknown automata mutator strategy: '{}'".format(strategy))

    def _mutate_random(self):
        r"""Generate an automaton that randomely links states together, and
        where a transition is accepted for every symbols.

        """

        new_automata = self.automata.duplicate()
        states = new_automata.getStates(main_states=True)

        for state in states:

            # Randomely decide if we create a transition
            if (round(next(self.generator)) % 2) == 0:
                continue

            # Randomely select an end state
            ending_state_idx = (next(self.generator) * len(states)) % len(states)
            ending_state = states[int(ending_state_idx)]

            for symbol in new_automata.vocabulary:

                # Do not add a new transition between 2 states, if it already exists with the same input symbol
                stop = False
                for t in state.transitions:
                    if t.endState == ending_state and t.inputSymbol == symbol:
                        stop = True
                        break
                if stop:
                    continue

                # Create a transition between current state and selected end state
                Transition(startState=state, endState=ending_state,
                           inputSymbol=symbol, outputSymbols=new_automata.vocabulary,
                           name="t_random")

        return new_automata

    def _mutate_full(self):
        r"""Generate an automaton that links all the states together, and where
        a transition is accepted for every symbols.

        """

        new_automata = self.automata.duplicate()
        states = new_automata.getStates(main_states=True)

        for state in states:
            for t in state.transitions:
                if isinstance(t, Transition):
                    t.outputSymbols = new_automata.vocabulary
                    t.description = None  # Force re-computation of transition description

        for initial_state in states:

            for ending_state in states:

                for symbol in new_automata.vocabulary:

                    # Do not add a new transition between 2 states, if it already exists with the same input symbol
                    stop = False
                    for t in initial_state.transitions:
                        if t.endState == ending_state and t.inputSymbol == symbol:
                            stop = True
                            break
                    if stop:
                        continue

                    # Create a transition between current state and selected end state
                    Transition(startState=initial_state, endState=ending_state,
                               inputSymbol=symbol, outputSymbols=new_automata.vocabulary,
                               name="t_random")

        return new_automata

    def _mutate_onestate(self):
        r"""Generate an automaton with one main state that accepts every symbols.

        """
        init_state = State("Initial state")
        state = State(name="Main state")
        t = OpenChannelTransition(startState=init_state, endState=state, name='Transition open channel')

        for symbol in self.automata.vocabulary:

            # Create a transition
            Transition(startState=state, endState=state,
                       inputSymbol=symbol, outputSymbols=self.automata.vocabulary,
                       name="t_random")

        return Automata(init_state, self.automata.vocabulary)

    def _mutate_targeted(self, target_states):
        r"""Build an automaton similar to the original one, where a targeted
        state, given in parameters, will accept every symbols.
        """

        if not isinstance(target_states, list):
            raise TypeError("'target_states' parameter should be a list of state names, not '{}' of type '{}'".format(target_states, type(target_states)))
        if not all(isinstance(x, str) for x in target_states):
            raise TypeError("'target_states' parameter should be a list of state names, not '{}'".format(target_states))

        new_automata = self.automata.duplicate()
        new_states = new_automata.getStates(main_states=True)

        for state in new_states:

            if state.name not in target_states:
                continue

            state.transitions = []

            for symbol in new_automata.vocabulary:

                # Create a transition between current state and selected end state
                Transition(startState=state, endState=state,
                           inputSymbol=symbol, outputSymbols=new_automata.vocabulary,
                           name="t_random")

        return new_automata

    def generate(self):
        raise NotImplementedError


    ## Properties
    
    @property
    def automata(self):
        return self._automata

    @automata.setter  # type: ignore
    def automata(self, automata):
        # Sanity checks
        if not isinstance(automata, Automata):
            raise TypeError("Mutator automata should be of type Automata. Received object: '{}'"
                            .format(automata))
        self._automata = automata
