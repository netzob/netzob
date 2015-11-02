#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2015 Christian Bruns                                        |
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
#|       - Christian Bruns <christian.bruns1 (a) stud.uni-goettingen.de>     |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

import uuid
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.Models.Grammar.Transitions.Transition import Transition
from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol
from netzob.Import.PrismaImporter.PrismaIO.Hist import Hist


@NetzobLogger
class PrismaTransition(Transition):
    """ Basically performs like original Transition; incorporates features of role (whether a Transition is client- or
        server-sided) and picking next outputSymbol cyclically

        PrismaTransition is not to be executed as not initiator

        ToDo: measure emitted-faulty ratio
    """

    TYPE = "PrismaTransition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[], _id=uuid.uuid4(), name=None):
        super(PrismaTransition, self).__init__(startState, endState, inputSymbol, outputSymbols, _id, name)

        self.inputSymbol = inputSymbol
        self.outputSymbols = outputSymbols
        self.outputSymbolProbabilities = {}  # TODO: not yet implemented
        self.outputSymbolReactionTimes = {}  # TODO: not yet implemented

        self.emitted = []
        self.invalid = False
        self.active = False
        if 'UAC' in startState.name.split('|')[-1]:
            self.ROLE = 'client'
        else:
            self.ROLE = 'server'

    def executeAsNotInitiator(self, abstractionLayer):
        pass

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """ Overrides parents executeAsInitiator; distinguished between input and output Transition

        :param abstractionLayer: the layer on which I/O's are performed
        :return: the EndState of the current Transition
        """
        self._logger.critical('current State {}'.format(self.startState.name))

        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        if self.startState.name.split('|')[-1] == 'START':
            return self.endState

        if not self.outputSymbols:
            return self.endState

        self.active = True
        # manage outputStates
        if self.ROLE == 'client':
            pickedSymbol = self.__pickOutputSymbol(abstractionLayer.symbolBuffer[:])

            if pickedSymbol is None:
                self._logger.debug("Something is wrong here. Got outState without outSymbol..")
                return None  # self.endState

            # Emit the symbol
            abstractionLayer.writeSymbol(pickedSymbol)
            # we gonna sleep here for a while..
            # time.sleep(1)

            # Return the endState
            self.active = False
            return self.endState
        # handle inputStates
        else:
            self._logger.info("Expecting Symbol(s): {}".format(map(lambda x: x.name, self.outputSymbols)))
            # Waits for the reception of a symbol
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()
            # we gonna sleep here for a while..
            # time.sleep(1)

            # hopefully we did a good job at learning
            if receivedSymbol in self.outputSymbols:
                self.active = False
                receivedSymbol.messages = [RawMessage(receivedMessage)]
                return self.endState
            # hopefully we then did a semi-good job at learning
            elif receivedSymbol in abstractionLayer.symbols:
                self.active = False
                self._logger.warning("Received symbol No.{} was not excepted. Try to keep session going..".format(
                    receivedSymbol.name))
                return self.endState
            # unfortunately we did not at all
            else:
                self.active = False
                self._logger.warning("Received Symbol entire unknown; still trying to go on")
                return self.endState

    def __pickOutputSymbol(self, Horizon):
        """ Advanced picking method; checks whether a Symbol is emittable in current Context (so-called Horizon),
            e.g. checks whether a Symbol has Rules AND those Rules can be applied in this very Context

            Method prefers not yet send Symbols, if possible

        :param Horizon: the Context in which the Communication happens
        :return: the Symbol to be emitted
        """
        self._logger.info("picking symbol")
        # what the horizon allows:
        horizon = Horizon[1:]+['x']
        emittable = []
        for sym in self.outputSymbols:
            horizon[-1] = sym
            h = Hist(map(lambda x: [int(x.name)], horizon))
            if (not sym.absoluteFields) or h in sym.horizons:
                emittable.append(sym)
        # what we want to emit:
        favorites = list(set(emittable) - set(self.emitted))
        if not favorites:
            favorites = emittable
        c = random.choice(favorites)
        if c not in self.emitted:
            self.emitted.append(c)
        if len(self.emitted) >= len(self.outputSymbols):
            self.emitted = []
        return c

    @property
    def outputSymbols(self):
        """Output symbols that can be generated when
        the current transition is executed.

        >>> from netzob.all import *
        >>> transition = Transition(State(), State())
        >>> transition.outputSymbols = None
        >>> len(transition.outputSymbols)
        0
        >>> transition.outputSymbols.append(Symbol())
        >>> transition.outputSymbols.extend([Symbol(), Symbol()])
        >>> print len(transition.outputSymbols)
        3
        >>> transition.outputSymbols = []
        >>> print len(transition.outputSymbols)
        0

        :type: list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raise: TypeError if not valid.
        """
        return self.__outputSymbols

    @outputSymbols.setter
    def outputSymbols(self, outputSymbols):
        if outputSymbols is None:
            self.__outputSymbols = []
        else:
            for symbol in outputSymbols:
                if not isinstance(symbol, PrismaSymbol):
                    raise TypeError("One of the output symbol is not a Symbol")
            self.__outputSymbols = []
            for symbol in outputSymbols:
                if symbol is not None:
                    self.__outputSymbols.append(symbol)

    @property
    def description(self):
        if self._description is not None:
            return self._description
        else:
            desc = []
            for outputSymbol in self.outputSymbols:
                desc.append(str(outputSymbol.name))
            return self.name + "\n" + "{" + ",".join(desc) + "}"
