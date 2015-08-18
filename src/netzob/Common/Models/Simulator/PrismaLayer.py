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
        self.symbolBuffer = 5*horizonLength*[e]
        self.sesSym = [[]]
        self.sesSta = [[]]
        self.unknowns = []
        self.unknownCount = -2
        self.removed = []

    def reInit(self):
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = len(self.symbolBuffer)*[e]

    def reset(self):
        self.reInit()
        self.sesSym = [[]]
        self.sesSta = [[]]
        self.unknowns = []
        self.unknownCount = -2
        return

    def updateSymbolBuffer(self, nextSymbol):
        self.symbolBuffer = self.symbolBuffer[1:] + [nextSymbol]

    def sessionOver(self, msg):
        self._logger.critical('The session is over: {}'.format(msg))
        # rule out errors
        # last sent message
        ds = self.sesSym[-1][-1]
        ds.faulty += 1
        si = self.sesSym[-1][-3]
        si.faulty += 0.05
        self._logger.critical('incrementing faulty of symNo.{} faulty:{} emitted:{} ratio:{}'.format(
            ds.name, ds.faulty, ds.emitted, float(ds.faulty)/ds.emitted))
        self._logger.critical('incrementing faulty of symNo.{} faulty:{} emitted:{} ratio:{}'.format(
            si.name, si.faulty, si.emitted, float(si.faulty)/si.emitted))
        self.sesSym.append([])
        self.sesSta.append([])

    def readSymbol(self):
        try:
            symbol, data = super(PrismaLayer, self).readSymbol()
        except Exception:
            self.sessionOver(msg='broken channel?')
            raise Exception("socket is not available")
        if data == '':
            self.sessionOver(msg='no data received')
            raise Exception("socket is not available")
        if 'Unknown' in symbol.name:
            self._logger.info("having unknown")
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
        self._logger.warning("going on as usual")
        self.sesSym[-1].append(symbol)
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
        # apply rules to symbol (the big show) NOT TO BE DONE HERE
        # muahhahahahhahahah
        # emit as usual
        self.sesSym[-1].append(symbol)
        symbol.emitted += 1
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
        data = symbol.specialize()
        # except Exception as e:
        #     print e.message
        #     self._logger.error('could not specialize sym{}'.format(symbol.name))
        #     try:
        #         symbol.messages = [RawMessage(symbol.specialize(noRules=True))]
        #         data = symbol.specialize()
        #     except Exception:
        #         self._logger.critical('could not specialize sym{} twice'.format(symbol.name))
        # self._logger.critical('data: {}'.format(data))
        symbol.messages = [RawMessage(data)]
        self._logger.info("Data generated from symbol '{0}': {1}.".format(symbol.name, repr(data)))

        self._logger.info("Going to write to communication channel...")
        try:
            self.channel.write(data)
        except Exception:
            self.sessionOver(role='client')
            raise Exception("error on writing to channel")
        self._logger.info("Writing to communication channel done..")
        return data
