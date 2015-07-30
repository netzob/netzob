from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol


class PrismaLayer(AbstractionLayer):
    def __init__(self, channel, symbols, horizonLength):
        super(PrismaLayer, self).__init__(channel, symbols)
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = horizonLength*[e]

    def updateSymbolBuffer(self, nextSymbol):
        self.symbolBuffer = self.symbolBuffer[1:] + [nextSymbol]

    def readSymbol(self):
        symbol, data = super(PrismaLayer, self).readSymbol()
        self.updateSymbolBuffer(symbol)
        return symbol, data

    def writeSymbol(self, symbol):
        # update symbolBuffer
        self.updateSymbolBuffer(symbol)
        # set horizon
        symbol.setHorizon(self.symbolBuffer)
        # apply rules to symbol (the big show) NOT TO BE DONE HERE
        # muahhahahahhahahah
        # emit as usual
        super(PrismaLayer, self).writeSymbol(symbol)