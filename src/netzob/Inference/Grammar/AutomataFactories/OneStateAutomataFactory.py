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
class OneStateAutomataFactory(object):
    @staticmethod
    @typeCheck(list, list)
    def generate(abstractSession, symbolList):
        """Generate an automata that, according to an abstract
        session, contains a main state where each request-response
        couples are permitted.
        """

        if len(abstractSession) < 1:
            return
        (client, server, symbol) = abstractSession[
            0]  # We expect that the first message/symbol is emitted by the client.
        # So we consider it as the initiator of the session.
        sStart = State(name="Start state")
        sMain = State(name="Main state")
        sEnd = State(name="End state")
        openTransition = OpenChannelTransition(
            startState=sStart, endState=sMain, name="Open")
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
                    mainTransition = Transition(
                        startState=sMain,
                        endState=sMain,
                        inputSymbol=inputSymbol,
                        outputSymbols=outputSymbols,
                        name="Transition")
                    inputSymbol = None
                    outputSymbols = None
            except StopIteration:
                break

        closeTransition = CloseChannelTransition(
            startState=sMain, endState=sEnd, name="Close")

        from netzob.Model.Grammar.Automata import Automata
        return Automata(sStart, symbolList)
