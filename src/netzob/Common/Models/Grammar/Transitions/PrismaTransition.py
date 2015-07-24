import uuid
import random

from netzob.Common.Models.Grammar.Transitions.Transition import Transition
from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


class PrismaTransition(Transition):

    TYPE = "PrismaTransition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[], _id=uuid.uuid4(), name=None):
        super(PrismaTransition, self).__init__(startState, endState, inputSymbol, outputSymbols, _id, name)

        if 'UAC' in startState.name.split('|')[-1]:
            self.ROLE = 'client'
        else:
            self.ROLE = 'server'

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer, receivedSymbol=None):
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        if self.startState.name.split('|')[-1] == 'START':
            return self.endState

        self.active = True
        # manage outputStates
        if self.ROLE == 'client':
            pickedSymbol = self.__pickOutputSymbol()

            if pickedSymbol is None:
                self._logger.debug("Something is wrong here. Got outState without outSymbol..")
                return self.endState

            # Emit the symbol
            abstractionLayer.writeSymbol(pickedSymbol)
            # (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()

            # print receivedSymbol.name, '\n', receivedMessage

            # Return the endState
            self.active = False
            return self.endState
        # handle inputStates
        else:
            # Waits for the reception of a symbol
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()

            if receivedSymbol in self.outputSymbols:
                self.active = False
                return self.endState
            else:
                self.active = False
                self._logger.warning("Received symbol was not excepted.")
                raise Exception("Received symbol was not excepted.")

    def __pickOutputSymbol(self):

        return random.choice(self.outputSymbols)
