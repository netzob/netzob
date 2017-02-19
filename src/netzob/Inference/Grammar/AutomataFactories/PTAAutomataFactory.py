# -*- coding: utf-8 -*-

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

#+----------------------------------------------
#| Standard library imports
#+----------------------------------------------

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Grammar.States.State import State
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.Transitions.OpenChannelTransition import OpenChannelTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition


@NetzobLogger
class PTAAutomataFactory(object):
    @staticmethod
    @typeCheck(list, list)
    def generate(abstractSessions, symbolList):
        """Generate an automata by merging different abstract sessions
        in a Prefix Tree Acceptor (PTA).
        """

        # Generate chained automatons from the provided list of abstract sessions
        from netzob.Inference.Grammar.AutomataFactories.ChainedStatesAutomataFactory import ChainedStatesAutomataFactory
        chainedAutomatons = []
        for abstractSession in abstractSessions:
            chainedAutomaton = ChainedStatesAutomataFactory.generate(
                abstractSession, symbolList)
            chainedAutomatons.append(chainedAutomaton)
        if len(chainedAutomatons) <= 1:
            return chainedAutomatons[0]

        # Create an initial state/transition for the PTA automaton
        ptaInitialState = State("Start state")
        idx_state = 0
        ptaStateA = State("State " + str(idx_state))
        ptaStateA_saved = ptaStateA
        ptaTransition = OpenChannelTransition(
            startState=ptaInitialState,
            endState=ptaStateA,
            name="Open transition")

        # Merge the other automatons in the PTA automaton
        for automaton in chainedAutomatons:
            # Restore the first main state of the PTA
            ptaStateA = ptaStateA_saved

            # We go through the first transition (which should be an OpenChannelTransition)
            initialState = automaton.initialState
            if initialState is not None and len(initialState.transitions) > 0:
                transition = initialState.transitions[0]
                if isinstance(transition, OpenChannelTransition):
                    transition = PTAAutomataFactory._getNextChainedTransition(
                        transition)
                    if transition is None:
                        break

                # We loop over each state to compare inputSymbol/outputSymbols with the states of the PTA automaton
                while True:
                    # We handle the closing state
                    if isinstance(transition, CloseChannelTransition):
                        if len(ptaStateA.transitions) > 0 and isinstance(
                                ptaStateA.transitions[0],
                                CloseChannelTransition):
                            # The transition is equivalent in the PTA
                            break
                        else:
                            # This is a new transition
                            idx_state += 1
                            ptaStateB = State("End state " + str(idx_state))
                            ptaTransition = CloseChannelTransition(
                                startState=ptaStateA,
                                endState=ptaStateB,
                                name="Close transition")
                            break
                    inputSymbol = transition.inputSymbol
                    outputSymbols = transition.outputSymbols

                    # We do the comparison with the PTA automaton at the transition level
                    newTransition = True
                    if len(ptaStateA.transitions) > 0 and isinstance(
                            ptaStateA.transitions[0], Transition):
                        if ptaStateA.transitions[0].inputSymbol == inputSymbol:
                            if len(ptaStateA.transitions[0].outputSymbols
                                   ) > 0 and ptaStateA.transitions[
                                       0].outputSymbols[0] == outputSymbols[0]:
                                # The transition is equivalent in the PTA
                                newTransition = False
                                ptaStateA = ptaStateA.transitions[0].endState
                    if newTransition == True:
                        idx_state += 1
                        ptaStateB = State("State " + str(idx_state))
                        ptaTransition = Transition(
                            startState=ptaStateA,
                            endState=ptaStateB,
                            inputSymbol=inputSymbol,
                            outputSymbols=[outputSymbols[0]],
                            name="Transition")
                        ptaStateA = ptaStateB

                    transition = PTAAutomataFactory._getNextChainedTransition(
                        transition)
                    if transition is None:
                        break

        from netzob.Model.Grammar.Automata import Automata
        return Automata(ptaInitialState, symbolList)

    @staticmethod
    @typeCheck(AbstractTransition)
    def _getNextChainedTransition(transition):
        if transition is None:
            return None
        endState = transition.endState
        if endState is not None:
            if len(endState.transitions) > 0:
                return endState.transitions[0]
        return None
