from netzob.Common.Models.Grammar.Transitions.Transition import Transition
from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol
from netzob.Import.PrismaImporter.prisma.Hist import Hist

import uuid
import random
import time


@NetzobLogger
class PrismaTransition(Transition):

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
            pickedSymbol = self.__pickOutputSymbol(abstractionLayer.symbolBuffer)

            if pickedSymbol is None:
                self._logger.debug("Something is wrong here. Got outState without outSymbol..")
                return None  # self.endState

            # Emit the symbol
            abstractionLayer.writeSymbol(pickedSymbol)
            # we gonna sleep here for a while..
            time.sleep(1)

            # Return the endState
            self.active = False
            return self.endState
        # handle inputStates
        else:
            self._logger.info("Expecting Symbol(s): {}".format(map(lambda x: x.name, self.outputSymbols)))
            # Waits for the reception of a symbol
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()
            # we gonna sleep here for a while..
            time.sleep(1)

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
        self._logger.info("picking symbol")
        # emit Symbol which previously was not emitted
        # what we 'want' to output
        pos = set(self.outputSymbols)-set(self.emitted)
        # check which Symbols are emittable w.r.t. the current horizon
        # what we 'can' output
        # print(pos)
        Horizon = Hist(map(lambda x: [int(x.name)], Horizon))
        # print(Horizon)
        posH = set([oS for oS in self.outputSymbols if (not oS.absoluteFields) or Horizon in oS.horizons])
        # print(posH)
        if posH:
            # would be nice to have something we want to output, which can be output ;)
            pos = pos.intersection(posH)
            if not pos:
                self._logger.critical("hist does not match")
                # no? ok, stick to what we can
                pos = posH
            self._logger.critical("matching hist")
        # print(pos)
        c = random.choice(list(pos))
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
