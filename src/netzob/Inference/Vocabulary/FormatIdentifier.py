#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByAlignment import ClusterByAlignment
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByKeyField import ClusterByKeyField
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByApplicativeData import ClusterByApplicativeData
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterBySize import ClusterBySize
from netzob.Inference.Vocabulary.FormatIdentifierOperations.FindKeyFields import FindKeyFields


class FormatIdentifier(object):
    """This class is a wrapper for all the various tools
    which allow to infer the different message formats contained in one or multiple symbols.

    """

    @staticmethod
    @typeCheck(list)
    def clusterByAlignment(messages, minEquivalence=50, internalSlick=True):
        """This clustering process regroups messages in groups that maximes
        their alignement. It provides the required methods to compute clustering
        between multiple symbols/messages using UPGMA algorithms (see U{http://en.wikipedia.org/wiki/UPGMA}).
        When processing, the matrix of scores is computed by the C extensions (L{_libScoreComputation}
        and used to regroup messages and symbols into equivalent cluster.
        """
        clustering = ClusterByAlignment(minEquivalence=minEquivalence, internalSlick=internalSlick)
        return clustering.cluster(messages)

    @staticmethod
    @typeCheck(list)
    def clusterByApplicativeData(messages):
        """Regroup messages having the same applicative data in their content.

        >>> import time
        >>> import random
        >>> import operator
        >>> from netzob.all import *
        >>> # we create 3 types of messages:

        >>> messages = []
        >>> for x in range(5):
        ...     messages.append(RawMessage("ACK {0}".format(random.randint(0, 50)), source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:{0}:01".format(x), "%d %b %y %H:%M:%S"))))
        ...     messages.append(RawMessage("SYN {0}".format(random.randint(0, 50)), source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:{0}:02".format(x), "%d %b %y %H:%M:%S"))))
        ...     messages.append(RawMessage("SYN/ACK {0}".format(random.randint(0, 50)), source="B", destination="A", date=time.mktime(time.strptime("9 Aug 13 10:{0}:03".format(x), "%d %b %y %H:%M:%S"))))
        ...     time.sleep(0.2)
        >>> session = Session(messages=messages)
        >>> appDatas = []
        >>> appDatas.append(ApplicativeData("ACK", ASCII("ack")))
        >>> appDatas.append(ApplicativeData("SYN", ASCII("syn")))
        >>> session.applicativeData = appDatas
        >>> symbols = FormatIdentifier.clusterByApplicativeData(messages)
        >>> for symbol in sorted(symbols, key=operator.attrgetter("name")):
        ...     print "Symbol : {0} = {1} messages.".format(symbol.name, len(symbol.messages))
        Symbol : ACK = 5 messages.
        Symbol : ACK;SYN = 5 messages.
        Symbol : SYN = 5 messages.

        :param messages: the messages to cluster.
        :type messages: a list of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :return: a list of symbol representing all the computed clusters
        :rtype: a list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raises: a TypeError if symbol is not valid.
        """
        if (messages is None or len(messages) == 0):
            raise TypeError("At least one message should be specified.")

        # We retrieve all the applicative data
        appDatas = []
        sessions = []
        for message in messages:
            if message.session is not None and message.session not in sessions:
                sessions.append(message.session)

        for session in sessions:
            appDatas.extend(session.applicativeData)

        if len(appDatas) == 0:
            raise ValueError("There are no applicative data attached to the session from which the specified messages come from.")

        cluster = ClusterByApplicativeData()
        return cluster.cluster(messages, appDatas)

    @staticmethod
    @typeCheck(AbstractField, AbstractField)
    def clusterByKeyField(field, keyField):
        """Create and return new symbols according to a specific key
        field.
        This method is a wrapper for :class:`netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByKeyField.ClusterByKeyField`

        :param field: the field we want to split in new symbols
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :param keyField: the field used as a key during the splitting operation
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens

        """
        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if keyField is None:
            raise TypeError("'keyField' should not be None")
        if not keyField in field.children:
            raise TypeError("'keyField' is not a child of 'field'")

        clusterByKeyField = ClusterByKeyField()
        return clusterByKeyField.cluster(field, keyField)

    @staticmethod
    @typeCheck(AbstractField)
    def findKeyFields(field):
        """Try to identify potential key fields in a symbol/field.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000011",	"000010000000",	"00fe1f000000",	"000020000000", "00ff1f000000",	"00ff1f000000",	"00ff2f000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> FormatEditor.splitStatic(symbol)
        >>> results = FormatIdentifier.findKeyFields(symbol)
        >>> for result in results:
        ...     print "Field name: " + result["keyField"].name + ", number of clusters: " + str(result["nbClusters"])
        Field name: Field-1, number of clusters: 5
        Field name: Field-3, number of clusters: 2

        :param field: the field in which we want to identify key fields.
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens

        """
        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")

        keyFieldsFinder = FindKeyFields()
        return keyFieldsFinder.execute(field)

    @staticmethod
    @typeCheck(list)
    def clusterBySize(messages):
        """This clustering process regroups messages that have
        equivalent size.

        >>> from netzob.all import *
        >>> import binascii
        >>> samples = ["00ffff1100abcd", "00aaaa1100abcd", "00bbbb1100abcd", "001100abcd", "001100ffff", "00ffffffff1100abcd"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> newSymbols = FormatIdentifier.clusterBySize(messages)
        >>> for sym in newSymbols:
        ...     print "[" + sym.name + "]"
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print sym
        [symbol_9]
        00ffffffff1100abcd
        [symbol_5]
        001100abcd
        001100ffff
        [symbol_7]
        00ffff1100abcd
        00aaaa1100abcd
        00bbbb1100abcd

        :param messages: the messages to cluster.
        :type messages: a list of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :return: a list of symbol representing all the computed clusters
        :rtype: a list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        """

        # Safe checks
        if messages is None:
            raise TypeError("'messages' should not be None")

        clustering = ClusterBySize()
        return clustering.cluster(messages)
