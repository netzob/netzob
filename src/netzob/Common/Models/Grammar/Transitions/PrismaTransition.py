import uuid
import random
import time

from netzob.Common.Models.Grammar.Transitions.Transition import Transition
from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class PrismaTransition(Transition):

    TYPE = "PrismaTransition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[], _id=uuid.uuid4(), name=None):
        super(PrismaTransition, self).__init__(startState, endState, inputSymbol, outputSymbols, _id, name)

        if 'UAC' in startState.name.split('|')[-1]:
            self.ROLE = 'client'
        else:
            self.ROLE = 'server'

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        if self.startState.name.split('|')[-1] == 'START':
            abstractionLayer.sesSta[-1].append(self.endState.name)
            return self.endState

        if not self.outputSymbols:
            abstractionLayer.sesSta[-1].append(self.endState.name)
            return self.endState

        self.active = True
        # manage outputStates
        if self.ROLE == 'client':
            pickedSymbol = self.__pickOutputSymbol()

            if pickedSymbol is None:
                self._logger.debug("Something is wrong here. Got outState without outSymbol..")
                abstractionLayer.sesSta[-1].append(self.endState.name)
                return self.endState

            # Emit the symbol
            abstractionLayer.writeSymbol(pickedSymbol)
            # we gonna sleep here for a while..
            time.sleep(0.1)

            # Return the endState
            self.active = False
            abstractionLayer.sesSta[-1].append(self.endState.name)
            return self.endState
        # handle inputStates
        else:
            self._logger.info("Expecting Symbol(s): {}".format(map(lambda x: x.name, self.outputSymbols)))
            # Waits for the reception of a symbol
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()
            # we gonna sleep here for a while..
            time.sleep(0.1)

            # hopefully we did a good job at learning
            if receivedSymbol in self.outputSymbols:
                self.active = False
                receivedSymbol.messages = [RawMessage(receivedMessage)]
                abstractionLayer.sesSta[-1].append(self.endState.name)
                return self.endState
            # hopefully we then did a semi-good job at learning
            elif receivedSymbol in abstractionLayer.symbols:
                self.active = False
                self._logger.warning("Received symbol No.{} was not excepted. Try to keep session going..".format(
                    receivedSymbol.name))
                abstractionLayer.sesSta[-1].append(self.endState.name)
                return self.endState
            # unfortunately we did not at all
            else:
                self.active = False
                self._logger.warning("Received Symbol entire unknown; still trying to go on")
                abstractionLayer.sesSta[-1].append(self.endState.name)
                return self.endState

    def __pickOutputSymbol(self):
        return random.choice(self.outputSymbols)
