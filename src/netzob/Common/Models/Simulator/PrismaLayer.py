#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2015 Christian Bruns                                        |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Christian Bruns <christian.bruns1 (a) stud.uni-goettingen.de>     |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

from copy import copy

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

from netzob.Common.Models.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.PrismaSymbol import PrismaSymbol


@NetzobLogger
class PrismaLayer(AbstractionLayer):
    """ Performs as original abstractionLayer, so reads and writes to/from the Channel
        incorporates the feature of Context (so-called Horizon)

        ToDo: could have the power of learning new, during the learning process unseen Symbols
    """
    def __init__(self, channel, symbols, horizonLength):
        super(PrismaLayer, self).__init__(channel, symbols)
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = horizonLength*[e]
        self.horizonLength = horizonLength

    def reInit(self):
        e = EmptySymbol()
        e.name = '-1'
        self.symbolBuffer = self.horizonLength*[e]

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
        self._logger.warning("going on as usual")
        self.updateSymbolBuffer(symbol)
        symbol.setHorizon(self.symbolBuffer)
        symbol.messages = [RawMessage(data)]
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        return symbol, data

    def writeSymbol(self, symbol):
        """ applies the Horizon-updating in its own SymbolBuffer and in Symbols Horizon
        :param symbol: the Symbol to be emitted
        :return: None
        """
        # update symbolBuffer
        self.updateSymbolBuffer(symbol)
        # set horizon
        symbol.setHorizon(self.symbolBuffer)
        self._logger.info('current horizon {}'.format(symbol.horizon2ID()))
        self._writeSymbol(symbol)

    # copied from usual AbstractionLayer
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
        self._logger.info("Data generated from symbol '{0}': {1}.".format(symbol.name, repr(data)))

        self._logger.info("Going to write to communication channel...")
        try:
            self.channel.write(data)
        except Exception:
            raise Exception("error on writing to channel")
        self._logger.info("Writing to communication channel done..")
        return
