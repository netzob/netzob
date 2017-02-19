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


@NetzobLogger
class ChainedStatesAutomataFactory(object):
    @staticmethod
    @typeCheck(list, list)
    def generate(abstractSession, symbolList):
        """Generate an automata that contains as many states and
        transitions as the number of request-response couples in the
        abstract session. This automata has thus the shape of a uniq
        chain.
        """

        if len(abstractSession) < 1:
            return
        (client, server, symbol) = abstractSession[
            0]  # We expect that the first message/symbol is emitted by the client.
        # So we consider it as the initiator of the session.
        sStart = State(name="Start state")
        idx_states = 1
        sA = State(name="State " + str(idx_states))
        sB = None
        sEnd = State(name="End state")
        openTransition = OpenChannelTransition(
            startState=sStart, endState=sA, name="Open")
        it = iter(abstractSession)
        inputSymbol = None
        outputSymbols = None
        while True:
            try:
                (source, destination, symbol) = next(it)
                if source == client:
                    if symbol is not None:
                        inputSymbol = symbol
                        outputSymbols = None
                else:
                    if symbol is not None:
                        outputSymbols = [symbol]
                if inputSymbol is not None and outputSymbols is not None:
                    idx_states += 1
                    sB = State(name="State " + str(idx_states))
                    mainTransition = Transition(
                        startState=sA,
                        endState=sB,
                        inputSymbol=inputSymbol,
                        outputSymbols=outputSymbols,
                        name="Transition")
                    inputSymbol = None
                    outputSymbols = None
                    sA = sB
            except StopIteration:
                break

        if sB is not None:
            closeTransition = CloseChannelTransition(
                startState=sB, endState=sEnd, name="Close")
        else:
            closeTransition = CloseChannelTransition(
                startState=sA, endState=sEnd, name="Close")

        from netzob.Model.Grammar.Automata import Automata
        return Automata(sStart, symbolList)
