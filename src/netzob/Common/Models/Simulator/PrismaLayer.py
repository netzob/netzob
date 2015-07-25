from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol


class PrismaLayer(AbstractionLayer):
    def __init__(self, channel, symbols, horizonLength):
        super(PrismaLayer, self).__init__(channel, symbols)
        self.symbolBuffer = horizonLength*[EmptySymbol()]

    def updateSymbolBuffer(self, nextSymbol):
        self.symbolBuffer = self.symbolBuffer[1:] + [nextSymbol]

    def readSymbol(self):
        symbol, data = super(PrismaLayer, self).readSymbol()
        self.updateSymbolBuffer(symbol)
        return symbol, data

    # def writeSymbol(self):
    # actually pick symbol as usual
    # update symbolBuffer
    # check horizon/rules
    # apply rules to symbol (the big show)
    # emit as usual