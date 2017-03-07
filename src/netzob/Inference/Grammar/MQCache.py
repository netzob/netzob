# -*- coding: utf-8 -*-

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

#+----------------------------------------------
#| Standard library imports
#+----------------------------------------------
import logging

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
import time
from netzob.Inference.Grammar.Queries.MembershipQuery import MembershipQuery


#+----------------------------------------------
#| MQCache:
#|    A cache for MQs and their results
#+----------------------------------------------
class MQCache():

    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.MQCache.py')
        self.cache = dict()

    def getCachedResult(self, mq):
        for cachedMQ in list(self.cache.keys()):
            if cachedMQ == mq:
                return self.cache.get(cachedMQ)

        return None

    def cacheResult(self, mq, result):
        self.log.debug("Cache the following : " + str(mq) + " == " + str(result))
        self.cache[mq] = result

    def dumpCache(self):
        for mq in list(self.cache.keys()):
            result = self.cache[mq]
            self.log.debug(str(mq) + ">" + str(result))

    def preloadCache(self, datas, vocabulary):
        for data in datas:
            self.preloadCacheEntry(data, vocabulary)

    def preloadCacheEntry(self, data, vocabulary):
        tab = data.split(" > ")
        msgSymbols = tab[0]
        mqSymbols = msgSymbols.split(",")
        symbols = []
        for mqSymbol in mqSymbols:
            symbol = vocabulary.getSymbolByName(mqSymbol)
            if symbol is not None:
                symbols.append(symbol)
        mq = MembershipQuery(symbols)

        msgResult = tab[1]
        tmp = msgResult.split(",")
        symbolsResult = []
        for t in tmp:
            symbol = vocabulary.getSymbolByName(t)
            if symbol is not None:
                symbolsResult.append(symbol)
        self.cacheResult(mq, symbolsResult)

#
#        (DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO, LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (STATUS, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (STATUS, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (LOGOUT, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (STATUS, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (UnknownSymbol, LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (LOGOUT, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, EXECUTE,) > [UnknownSymbol, PASSWORD_ACCEPTED, CANTEXECUTE]
#        (EXECUTE, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, UnknownSymbol,) > [UnknownSymbol, PASSWORD_ACCEPTED, EmptySymbol]
#        (SYSINFO, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, LOGOUT,) > [UnknownSymbol, PASSWORD_ACCEPTED, EmptySymbol]
#        (SYSINFO, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (DOWNLOAD, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, DOWNLOAD,) > [UnknownSymbol, PASSWORD_ACCEPTED, DOWNLOADING]
#        (DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (STATUS, SYSINFO,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, LOGIN,) > [UnknownSymbol, PASSWORD_ACCEPTED, EmptySymbol]
#        (EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (EXECUTE, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, SYSINFO,) > [UnknownSymbol, PASSWORD_ACCEPTED, CPU]
#        (STATUS, LOGIN,) > [UnknownSymbol, EmptySymbol, PASSWORD_ACCEPTED]
#        (STATUS, LOGOUT,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGOUT, LOGIN,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, STATUS,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO, EXECUTE,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (UnknownSymbol, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (SYSINFO, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (STATUS, DOWNLOAD,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#        (LOGIN, STATUS,) > [UnknownSymbol, PASSWORD_ACCEPTED, SDBOT]
#        (DOWNLOAD, UnknownSymbol,) > [UnknownSymbol, EmptySymbol, EmptySymbol]
#
#
#
#
#
