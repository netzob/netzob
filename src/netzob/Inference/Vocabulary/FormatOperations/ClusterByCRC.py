#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import collections
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Inference.Vocabulary.CRCFinder import CRCFinder
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Utils.TypedList import TypedList

@NetzobLogger
class ClusterByCRC(object):
    """This clustering process regroups messages that have equivalent
        size.
    """

    def cluster(self, symbol):
        """Create and return new symbols according to wether the previous symbol or messages contained a CRC or not.
        Args:
            :param symbol: the symbol which has messages to cluster.
            :type symbol: :class:`netzob.Model.Vocabulary.Symbol.Symbol`
            :raise Exception if something bad happens
        Returns: list: Returns a list of :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        """
        sym = None
        if isinstance(symbol,Symbol):
            if not symbol.messages:
                raise "Symbol has no messages. Aborting"
            else:
                symbol_name = symbol.name
                messages = symbol.messages.list
                sym = symbol
        elif isinstance(symbol,list):
            if isinstance(symbol[0],AbstractMessage):
                messages = symbol
                symbol_name = "Symbol"
        elif isinstance(symbol, TypedList):
            if isinstance(symbol[0], AbstractMessage):
                messages = symbol
                symbol_name = "Symbol"
            else:
                raise TypeError("Typecheck failed. Aborting")
        else:
            raise TypeError("Typecheck failed. Aborting")
        return self.__executeOnMessages(messages,symbol_name,sym)

    def __executeOnMessages(self, messages,symbol_name,symbol):
        """
        Clusters messages by CRC32 type. Takes a symbol which contains messages as input
        Args:
            symbol:  :class:`netzob.Model.Vocabulary.Symbol.Symbol`

        Returns: list: Returns a list of :class:`netzob.Model.Vocabulary.Symbol.Symbol`

        """
        crcfinder = CRCFinder()
        messageByCRC = dict()
        for message in messages:
            results = collections.namedtuple('Results', ['CRC_be', 'CRC_le', 'CRC_mid_be', 'CRC_mid_le'])
            searched_string = message.data
            results.CRC_be, results.CRC_le = crcfinder._search_CRC(searched_string)
            results.CRC_mid_be, results.CRC_mid_le = crcfinder._search_mid_CRC(searched_string)
            self._logger.debug("Found the following results:")
            self._logger.debug("CRC_BE : " + str(results.CRC_be) + "")
            self._logger.debug("CRC_LE : " + str(results.CRC_le) + "")
            self._logger.debug("CRC_mid_be : " + str(results.CRC_mid_be) + "")
            self._logger.debug("CRC_mid_le : " + str(results.CRC_mid_le) + "")
            # Cluster messages by CRC type
            if results.CRC_be:
                if "CRC_be" in messageByCRC:
                    messageByCRC["CRC_be"].append(message)
                else:
                    messageByCRC["CRC_be"] = [message]
            elif results.CRC_le:
                if "CRC_le" in messageByCRC:
                    messageByCRC["CRC_le"].append(message)
                else:
                    messageByCRC["CRC_le"] = [message]
            elif results.CRC_mid_be:
                if "CRC_mid_be" in messageByCRC:
                    messageByCRC["CRC_mid_be"].append(message)
                else:
                    messageByCRC["CRC_mid_be"] = [message]
            elif results.CRC_mid_le:
                if "CRC_mid_le" in messageByCRC:
                    messageByCRC["CRC_mid_le"].append(message)
                else:
                    messageByCRC["CRC_mid_le"] = [message]
            else:
                if "No_CRC" in messageByCRC:
                    messageByCRC["No_CRC"].append(message)
                else:
                    messageByCRC["No_CRC"] = [message]
            # Create new symbols for each group of equivalent message CRC
            newSymbols = []
        for sym_name,msgs in messageByCRC.items():
            s = Symbol(messages=msgs, name=symbol_name+"_"+sym_name)
            if symbol is not None:
                s.fields = symbol.fields
            newSymbols.append(s)
        return newSymbols

