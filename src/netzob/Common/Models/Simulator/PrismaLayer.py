import time

from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol


@NetzobLogger
class PrismaLayer(AbstractionLayer):
    def __init__(self, channel, symbols, horizonLength):
        super(PrismaLayer, self).__init__(channel, symbols)
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = horizonLength*[e]
        self.sesSym = [[]]
        self.sesSta = [[]]
        self.unknowns = []
        self.unknownCount = -2

    def reInit(self):
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = len(self.symbolBuffer)*[e]
        return

    def updateSymbolBuffer(self, nextSymbol):
        self.symbolBuffer = self.symbolBuffer[1:] + [nextSymbol]

    def fuzzyCrack(self, data):
        if data:
            l = len(data)
            for sym in self.symbols:
                m = sym.messages[0].data
                if len(m) == l:
                    pass

    def sessionOver(self):
        self._logger.critical('The session is over')
        self.sesSym.append([])
        self.sesSta.append([])
        time.sleep(0.75)

    def readSymbol(self):
        try:
            symbol, data = super(PrismaLayer, self).readSymbol()
        except Exception:
            self.sessionOver()
            raise Exception("socket is not available")
        if 'Unknown' in symbol.name:
            self._logger.info("having unknown")
            # s = self.fuzzyCrack(data)
            symbol = PrismaSymbol(name='{}'.format(self.unknownCount), messages=[RawMessage(data)])
            # maybe we saw this..
            seen = False
            for missingNo in self.unknowns:
                try:
                    if missingNo.getCells() == symbol.getCells():
                        self._logger.info("match {}".format(missingNo.name))
                        seen = True
                        symbol = missingNo
                        break
                except Exception:
                    pass
            if not seen:
                if data != '':
                    self._logger.info("record new unknown at ID{}".format(self.unknownCount))
                    self.unknownCount -= 1
                    self.unknowns.append(symbol)
                    # we then could add the unknown to our well-known templates
                    self.symbols.append(symbol)
                else:
                    self._logger.info("record new unknown at ID{}".format(-1))
        self._logger.error("going on as usual")
        self.sesSym[-1].append(symbol.name)
        self.updateSymbolBuffer(symbol)
        symbol.setHorizon(self.symbolBuffer)
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        return symbol, data

    def writeSymbol(self, symbol):
        # update symbolBuffer
        self.updateSymbolBuffer(symbol)
        # set horizon
        symbol.setHorizon(self.symbolBuffer)
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        # apply rules to symbol (the big show) NOT TO BE DONE HERE
        # muahhahahahhahahah
        # emit as usual
        self._writeSymbol(symbol)
        self.sesSym[-1].append(symbol.name)

    # copied from usal AbstractionLayer
    # need to get hands on the data generated during sending
    def _writeSymbol(self, symbol):
        """Write the specified symbol on the communication channel
        after specializing it into a contextualized message.

        :param symbol: the symbol to write on the channel
        :type symbol: :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raise TypeError if parameter is not valid and Exception if an exception occurs.
        """
        if symbol is None:
            raise TypeError("The symbol to write on the channel cannot be None")

        self._logger.info("Going to specialize symbol: '{0}' (id={1}).".format(symbol.name, symbol.id))
        data = symbol.specialize()
        symbol.messages = [RawMessage(data)]
        self._logger.info("Data generated from symbol '{0}': {1}.".format(symbol.name, repr(data)))

        self._logger.info("Going to write to communication channel...")
        try:
            self.channel.write(data)
        except Exception:
            self.sessionOver()
            raise Exception("socket is not available")
        self._logger.info("Writing to communication channel done..")
        return data
