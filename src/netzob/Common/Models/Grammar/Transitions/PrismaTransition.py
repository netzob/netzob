import uuid

from netzob.Common.Models.Grammar.Transitions.Transition import Transition


class PrismaTransition(Transition):

    TYPE = "PrismaTransition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[], _id=uuid.uuid4(), name=None):
        super(PrismaTransition, self).__init__(startState, endState, inputSymbol, outputSymbols, _id, name)


