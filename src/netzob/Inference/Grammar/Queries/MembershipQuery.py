# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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


@NetzobLogger
class MembershipQuery(object):
    """Represents a membership queryset of query which will be submited to an oracle"""

    def __init__(self, symbols):
        self.symbols = symbols

    def addSymbol(self, symbol):
        self.symbols.append(symbol)

    def getSymbols(self):
        if len(self.symbols) <= 1:
            return self.symbols
        else:
            return self.getSymbolsWhichAreNotEmpty()

    def getSymbolsWhichAreNotEmpty(self):
        result = []
        for s in self.symbols:
            if s.getType() != "EmptySymbol":
                result.append(s)
        return result

    def toMMSTD(self, dictionary, isMaster):
        # We create an MMSTD which will submit the following symbols
        generatedStates = []

        # Create the transition which opens the connection
        rootState = NormalState(0, "State 0")
        generatedStates.append(rootState)
        initialState = NormalState(1, "State 1")
        generatedStates.append(initialState)
        openingTransition = OpenChannelTransition(0, "Connection", rootState, initialState, 15000, 3)
        rootState.registerTransition(openingTransition)
        previousState = initialState
        idState = 2

        for symbol in self.symbols:
            # we create the current state
            currentState = NormalState(idState, "State " + str(idState))
            generatedStates.append(currentState)
            # we create a normal transition between it and the previous state
            idTransition = idState - 1
            transition = SimpleTransition(idTransition, "Transition " + str(idTransition), previousState, currentState, 1000, symbol)
            previousState.registerTransition(transition)
            idState = idState + 1
            previousState = currentState

        if not isMaster:
            # We create the opening transition to listen for the first entry
            currentState = NormalState(idState, "State " + str(idState))
            generatedStates.append(currentState)
            transition = SimpleTransition(idState - 1, "Transition " + str(idState - 1), previousState, currentState, 1000, EmptySymbol())
            previousState.registerTransition(transition)
            previousState = currentState
            idState += 1

        # Create the transition which close the connection
        endState = NormalState(idState, "State " + str(idState))
        generatedStates.append(endState)
        closingTransition = CloseChannelTransition(idState - 1, "Disconnection", currentState, endState, 1000)
        currentState.registerTransition(closingTransition)

        mmstd = MMSTD(rootState, dictionary)
        for state in generatedStates:
            mmstd.addState(state)
        return mmstd

    def multiply(self, mqs):
        result = []
        for mq in mqs:
            result.append(self.getMQSuffixedWithMQ(mq))
        return result

    def getNotEmptyPrefixes(self):
        result = []
        for i in range(0, len(self.getSymbolsWhichAreNotEmpty())):
            result.append(MembershipQuery(self.getSymbolsWhichAreNotEmpty()[:i + 1]))
        return result

    def getMQSuffixedWithMQ(self, mq):
        result = MembershipQuery([])
        for s in self.getSymbols():
            result.addSymbol(s)

        for symbol in mq.getSymbols():
            result.addSymbol(symbol)
        return result

    def isStrictlyEqual(self, other):
        symbols = self.getSymbolsWhichAreNotEmpty()
        symbols2 = other.getSymbolsWhichAreNotEmpty()
        if len(symbols) == len(symbols2):
            nbSymbol = len(symbols)

            if (nbSymbol == 0):
                return True

#            if (symbols[len(symbols) - 1].getID() != symbols2[len(symbols2) - 1].getID()) :
#                return False
#            else :
#                return True

            for i in range(0, nbSymbol):
                if symbols[i].getID() != symbols2[i].getID():
                    return False
            return True
        else:
            return False

    def __cmp__(self, other):
        if other is None:
            return -1
        if self.isStrictlyEqual(other):
            return 0
        elif (len(self.getSymbolsWhichAreNotEmpty()) > len(other.getSymbolsWhichAreNotEmpty())):
            return 1
        else:
            return -1

    def __str__(self, *args, **kwargs):

        result = "MQ ("
        for symbol in self.getSymbols():
            result = result + str(symbol) + ", "

        return result + ")"
