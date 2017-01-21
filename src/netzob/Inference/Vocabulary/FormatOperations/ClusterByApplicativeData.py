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
import operator

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.ApplicativeData import ApplicativeData
from netzob.Inference.Vocabulary.Search.SearchEngine import SearchEngine


@NetzobLogger
class ClusterByApplicativeData(object):
    """This operations cluster messages in symbols following
    their embedded applicative data.

    The clustering by applicative data use the :class:`netzob.Inference.Search.SearchEngine.SearchEngine` to
    search applicative data in messages and cluster together message with the same applicative data.
    In the example below, we generate two types of messages. The first,
    contains the pseudo and the city of the user: two applicative datas. While the second
    type of message includes the IP address of the user another applicative data.


    >>> from netzob.all import *
    >>> pseudos = ["zoby", "ditrich", "toto", "carlito"]
    >>> cities = ["Paris", "Munich", "Barcelone", "Vienne"]
    >>> ips = ["192.168.0.10", "10.120.121.212", "78.167.23.10"]
    >>> # Build applicative data
    >>> appPseudos = [ApplicativeData("Pseudo", ASCII(pseudo)) for pseudo in pseudos]
    >>> appCities = [ApplicativeData("City", ASCII(city)) for city in cities]
    >>> appIps = [ApplicativeData("IPs", IPv4(ip)) for ip in ips]
    >>> appDatas = appPseudos + appCities + appIps
    >>> # Creating messages using application data
    >>> msgsType1 = [ RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in pseudos for city in cities]
    >>> msgsType2 = [ RawMessage("My ip address is {0}".format(TypeConverter.convert(ip, IPv4, Raw))) for ip in ips]
    >>> messages = msgsType1+msgsType2
    >>> appCluster = ClusterByApplicativeData()
    >>> symbols = appCluster.cluster(messages, appDatas)
    >>> len(symbols)
    2
    >>> len(symbols[0].messages) == 3 or len(symbols[0].messages) == 16
    True
    >>> len(symbols[1].messages) == 3 or len(symbols[1].messages) == 16
    True

    """

    def __init__(self):
        pass

    @typeCheck(list, list)
    def cluster(self, messages, appDatas):
        if messages is None:
            raise TypeError("Messages cannot be None")
        if appDatas is None:
            raise TypeError("AppDatas cannot be None")
        if len(messages) == 0:
            raise TypeError("There should be at least one message.")
        if len(appDatas) == 0:
            raise TypeError("There should be at least one applicative data.")

        for m in messages:
            if not isinstance(m, AbstractMessage):
                raise TypeError("At least one message ({0}) is not an AbstractMessage.".format(str(m)))
        for appData in appDatas:
            if not isinstance(appData, ApplicativeData):
                raise TypeError("At least one applicative data ({0}) is not an instance of ApplicativeData.".format(str(appData)))

        labels = dict()
        for appData in appDatas:
            labels[appData.value] = appData.name

        idMessages = dict()
        for message in messages:
            idMessages[message.id] = message

        messagesPerAppData = dict()
        for message in messages:
            messagesPerAppData[message] = set()

        searchEngine = SearchEngine()

        searchResults = searchEngine.searchDataInMessages([appData.value for appData in appDatas], messages, inParallel=True, dataLabels=labels)
        for result in searchResults:
            searchTask = result.searchTask
            message = searchTask.properties['message']
            label = searchTask.properties['label']
            if label not in list(labels.values()):
                raise ValueError("Found label ({0}) in a result cannot be identified in the original list of searched labels.".format(label))
            if message.id not in list(idMessages.keys()):
                raise ValueError("Found message ({0}) cannot be identified in the original list of searched messages.".format(message.id))
            messagesPerAppData[idMessages[message.id]].add(label)

        # Build clusters
        clusters = dict()
        for message, labelsInMessage in list(messagesPerAppData.items()):
            strAppDatas = ';'.join(sorted(labelsInMessage))
            if len(strAppDatas) == 0:
                strAppDatas = None
            if strAppDatas in list(clusters.keys()):
                clusters[strAppDatas].append(message)
            else:
                clusters[strAppDatas] = [message]

        # Build Symbols
        symbols = [Symbol(name=strAppDatas, messages=msgs) for strAppDatas, msgs in list(clusters.items())]

        return symbols
