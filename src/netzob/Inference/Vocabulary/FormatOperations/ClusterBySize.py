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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.HexaString import HexaString
from netzob.Model.Types.Raw import Raw
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory


@NetzobLogger
class ClusterBySize(object):
    """This clustering process regroups messages that have equivalent
        size.
    """

    @typeCheck(list)
    def cluster(self, messages):
        """Create and return new symbols according to the messages size.

        >>> from netzob.all import *
        >>> import binascii
        >>> samples = ["00ffff1100abcd", "00aaaa1100abcd", "00bbbb1100abcd", "001100abcd", "001100ffff", "00ffffffff1100abcd"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> clusterer = ClusterBySize()
        >>> newSymbols = clusterer.cluster(messages)
        >>> for sym in newSymbols:
        ...     print("[" + sym.name + "]")
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print(sym)
        [symbol_9]
        Field               
        --------------------
        '00ffffffff1100abcd'
        --------------------
        [symbol_5]
        Field       
        ------------
        '001100abcd'
        '001100ffff'
        ------------
        [symbol_7]
        Field           
        ----------------
        '00ffff1100abcd'
        '00aaaa1100abcd'
        '00bbbb1100abcd'
        ----------------

        :param messages: the messages to cluster.
        :type messages: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :raise Exception if something bad happens
        """

        # Safe checks
        if messages is None:
            raise TypeError("'messages' should not be None")

        # Cluster messages by size
        messagesByLen = {}
        for msg in messages:
            l = len(msg.data)
            if not l in list(messagesByLen.keys()):
                messagesByLen[l] = []
            messagesByLen[l].append(msg)

        # Create new symbols for each group of equivalend message size
        newSymbols = []
        for (length, msgs) in list(messagesByLen.items()):
            s = Symbol(messages=msgs, name="symbol_{0}".format(str(length)))
            newSymbols.append(s)

        return newSymbols

