# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
import logging
from netzob.Common.MMSTD.States.impl.NormalState import NormalState

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.MMSTD.Transitions.impl.SimpleTransition import SimpleTransition
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import CloseChannelTransition
from netzob.Common.MMSTD.MMSTD import MMSTD

#+----------------------------------------------
#| MembershipQuery:
#| Represents a set of query which will be submited to
#| an oracle
#+----------------------------------------------
class MembershipQuery(object):

    def __init__(self, symbols):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.Queries.MembershipQuery.py')
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

    def toMMSTD(self, dictionary):
        # We create an MMSTD which will submit the following symbols

        # Create the transition which opens the connection
        rootState = NormalState(0, "State 0")
        initialState = NormalState(1, "State 1")
        openingTransition = OpenChannelTransition(0, "Connection", rootState, initialState, 1000, 3)
        rootState.registerTransition(openingTransition)

        previousState = initialState
        idState = 2
        for symbol in self.symbols:
            # we create the current state
            currentState = NormalState(idState, "State " + str(idState))
            # we create a normal transition between it and the previous state
            idTransition = idState - 1
            transition = SimpleTransition(idTransition, "Transition " + str(idTransition), previousState, currentState, 3000, symbol)
            previousState.registerTransition(transition)
            idState = idState + 1
            previousState = currentState

        # Create the transition which close the connection
        endState = NormalState(idState, "State " + str(idState))
        closingTransition = CloseChannelTransition(idState - 1, "Disconnection", currentState, endState, 1000)
        currentState.registerTransition(closingTransition)

        mmstd = MMSTD(rootState, dictionary)
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
        if (len(self.getSymbolsWhichAreNotEmpty()) == len(other.getSymbolsWhichAreNotEmpty())):
            symbols = self.getSymbolsWhichAreNotEmpty()
            symbols2 = other.getSymbolsWhichAreNotEmpty()

            nbSymbol = len(symbols)

            for i in range(0, nbSymbol):
                if symbols[i].getID() != symbols2[i].getID():
                    return False
            return True
        else:
            return False






    def __cmp__(self, other):
        if other == None:
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
