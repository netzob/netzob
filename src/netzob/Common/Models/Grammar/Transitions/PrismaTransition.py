import uuid
import random

from netzob.Common.Models.Grammar.Transitions.Transition import Transition
from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


class PrismaTransition(Transition):

    TYPE = "PrismaTransition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[],
                 _id=uuid.uuid4(), name=None, allSymbols=[]):
        super(PrismaTransition, self).__init__(startState, endState, inputSymbol, outputSymbols, _id, name)

        if 'UAC' in startState.name.split('|')[-1]:
            self.ROLE = 'client'
        else:
            self.ROLE = 'server'
        self.allSymbols = allSymbols

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

            # print 'picked symbol {}'.format(pickedSymbol.name)

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

            print 'seen {}'.format(receivedSymbol.name)
            print 'expected:',
            for s in self.outputSymbols:
                print s.name,
            print

            # hopefully we did a good job at learning
            if receivedSymbol in self.outputSymbols:
                self.active = False
                return self.endState
            # hopefully we then did a semi-good job at learning
            elif receivedSymbol in self.allSymbols:
                self.active = False
                self._logger.warning("Received symbol was not excepted. Try to keep session going..")
                # raise Exception("Received symbol was not excepted.")
                return self.endState
            # unfortunately we did not at all
            else:
                self.active = False
                self.logger.warning("Received Symbol entire unknown")
                raise Exception("Received symbol is unknown to us.")

    def __pickOutputSymbol(self):

        return random.choice(self.outputSymbols)
