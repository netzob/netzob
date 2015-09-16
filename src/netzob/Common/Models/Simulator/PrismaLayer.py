from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol
from copy import copy


@NetzobLogger
class PrismaLayer(AbstractionLayer):
    def __init__(self, channel, symbols, horizonLength):
        super(PrismaLayer, self).__init__(channel, symbols)
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = horizonLength*[e]

    def reInit(self):
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = len(self.symbolBuffer)*[e]

    def updateSymbolBuffer(self, nextSymbol):
        # save a copy here
        # idea: the message wont be overwritten if symbol more than once in the horizon
        self.symbolBuffer = self.symbolBuffer[1:] + [copy(nextSymbol)]

    def readSymbol(self):
        try:
            symbol, data = super(PrismaLayer, self).readSymbol()
        except Exception:
            raise Exception("socket is not available")
        if data == '':
            raise Exception("socket is not available")
        if 'Unknown' in symbol.name:
            self._logger.info("having unknown")
            symbol = PrismaSymbol(name='{}'.format(self.unknownCount), messages=[RawMessage(data)])
        self._logger.critical('received from the channel sym{}:'.format(symbol.name))
        print symbol.messages
        self._logger.warning("going on as usual")
        self.updateSymbolBuffer(symbol)
        symbol.setHorizon(self.symbolBuffer)
        symbol.messages = [RawMessage(data)]
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        return symbol, data

    def writeSymbol(self, symbol):
        # update symbolBuffer
        self.updateSymbolBuffer(symbol)
        # set horizon
        symbol.setHorizon(self.symbolBuffer)
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        self._writeSymbol(symbol)

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
        # apply Prisma rules in specializing process
        data = symbol.specialize()
        # update symbols message with what we send over the wire
        symbol.messages = [RawMessage(data)]
        self._logger.critical('sending over the channel sym{}:'.format(symbol.name))
        print '{}'.format(symbol.messages)
        self._logger.info("Data generated from symbol '{0}': {1}.".format(symbol.name, repr(data)))

        self._logger.info("Going to write to communication channel...")
        try:
            self.channel.write(data)
        except Exception:
            raise Exception("error on writing to channel")
        self._logger.info("Writing to communication channel done..")
        return
