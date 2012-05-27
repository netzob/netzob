# -*- coding: utf-8 -*-

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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import logging
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.Format import Format
from netzob.Inference.Vocabulary.SearchResult import SearchResult
from netzob.Inference.Vocabulary.SearchTask import SearchTask

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#+----------------------------------------------
#| Searcher:
#|     Provides multiple algorithms for a searching after a pattern in a
#|     set of computed messages
#+----------------------------------------------
class Searcher(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param project : the project where the search will be executed
    #+----------------------------------------------
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.Searcher.py')
        self.project = project

    #+----------------------------------------------
    #| getSearchedDataForBinary:
    #|   Generates data which can represent the specified Binary
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForBinary(self, value):
        return []

    #+----------------------------------------------
    #| getSearchedDataForOctal:
    #|   Generates data which can represent the specified Octal
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForOctal(self, value):
        return []

    #+----------------------------------------------
    #| getSearchedDataForDecimal:
    #|   Generates data which can represent the specified Decimal
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForDecimal(self, value):
        # Creation of a SearchTask
        task = SearchTask(value, value, Format.DECIMAL)
        task.registerVariation(TypeConvertor.decimalToNetzobRaw(value), "Decimal representation of '{0}'".format(TypeConvertor.decimalToNetzobRaw(value)))
        task.registerVariation(TypeConvertor.decimalToNetzobRaw(value[::-1]), "Inverted decimal representation of '{0}'".format(TypeConvertor.decimalToNetzobRaw(value[::-1])))
        return [task]

    #+----------------------------------------------
    #| getSearchedDataForHexadecimal:
    #|   Generates data which can represent the specified Hexa
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForHexadecimal(self, value):
        # Creation of a SearchTask
        task = SearchTask(value, value, Format.HEX)
        task.registerVariation(value, "Hexadecimal representation of '{0}'".format(value))
        task.registerVariation(value[::-1], "Inverted representation of '{0}'".format(value[::-1]))
        return [task]

    #+----------------------------------------------
    #| getSearchedDataForString:
    #|   Generates data which can represent the specified string
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForString(self, value):
        # Creation of a SearchTask
        task = SearchTask(value, value, Format.STRING)
        task.registerVariation(TypeConvertor.stringToNetzobRaw(value), "String representation of '%s'" % value)
        task.registerVariation(TypeConvertor.stringToNetzobRaw(value[::-1]), "Inverted string representation of '%s'" % value[::-1])
        return [task]

    #+----------------------------------------------
    #| getSearchedDataForIP:
    #|   Generates data which can represent the specified IP
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForIP(self, value):
        tasks = []
        # parse the value to get a, b, c and d
        ipTab = value.split('.')
        a = ipTab[0]
        b = ipTab[1]
        c = ipTab[2]
        d = ipTab[3]

        a2 = a
        if a2 < 100:
            a2 = "0" + a2
        if a2 < 10:
            a2 = "0" + a2
        b2 = b
        if b2 < 100:
            b2 = "0" + b2
        if b2 < 10:
            b2 = "0" + b2
        c2 = c
        if c2 < 100:
            c2 = "0" + c2
        if c2 < 10:
            c2 = "0" + c2
        d2 = d
        if d2 < 100:
            d2 = "0" + d2
        if d2 < 10:
            d2 = "0" + d2

        # in String :
        # - 192.168.0.10
        val = "%s.%s.%s.%s" % (a, b, c, d)
        tasks.extend(self.getSearchedDataForString(val))

        # - 192.168.000.010
        val = "%s.%s.%s.%s" % (a2, b2, c2, d2)
        tasks.extend(self.getSearchedDataForString(val))

        # - 192168000010
        val = "%s%s%s%s" % (a2, b2, c2, d2)
        tasks.extend(self.getSearchedDataForString(val))

        # - 10.0.168.192
        val = "%s.%s.%s.%s" % (d, c, b, a)
        tasks.extend(self.getSearchedDataForString(val))

        # - 000.010.192.168
        val = "%s.%s.%s.%s" % (d2, c2, b2, a2)
        tasks.extend(self.getSearchedDataForString(val))

        # - 0.10.192.168
        val = "%s.%s.%s.%s" % (c, d, a, b)
        tasks.extend(self.getSearchedDataForString(val))

        # - 000.010.192.168
        val = "%s.%s.%s.%s" % (c2, d2, a2, b2)
        tasks.extend(self.getSearchedDataForString(val))

        # - 000010192168
        val = "%s%s%s%s" % (c2, d2, a2, b2)
        tasks.extend(self.getSearchedDataForString(val))

        return tasks

    #+----------------------------------------------
    #| search:
    #|   Search a set of specified data in all the project
    #| @param tasks the set of "search" task
    #+----------------------------------------------
    def search(self, tasks):
        for task in tasks:
            for symbols in self.project.getVocabulary().getSymbols():
                for message in symbols.getMessages():
                    variations = task.getVariations()
                    for variation_value in variations.keys():
                        task.registerResults(self.extendedSearch(variation_value, message), variations[variation_value])
        return tasks

    #+----------------------------------------------
    #| searchInSymbol:
    #|   Search a set of specified data in a the specified symbol
    #| @param tasks the set of "search" task
    #| @param symbol the symbol to search in
    #+----------------------------------------------
    def searchInSymbol(self, tasks, symbol):
        for task in tasks:
            for message in symbol.getMessages():
                variations = task.getVariations()
                for variation_value in variations.keys():
                    task.registerResults(self.extendedSearch(variation_value, message), variations[variation_value])
        return tasks

    #+----------------------------------------------
    #| searchInMessage:
    #|   Search a set of specified data in a the specified message
    #| @param tasks the set of "search" task
    #| @param message the message to search in
    #+----------------------------------------------
    def searchInMessage(self, tasks, message):
        for task in tasks:
            variations = task.getVariations()
            for variation_value in variations.keys():
                task.registerResults(self.extendedSearch(variation_value, message), variations[variation_value])
        return tasks

    #+----------------------------------------------
    #| extendedSearch:
    #|   Search for a data in a specified message
    #+----------------------------------------------
    def extendedSearch(self, data, message):
        results = []
        results.extend(self.naturalSearch(data, message))
        results.extend(self.inversedSearch(data, message))
        results.extend(self.semiInvertedOnNaturalSearch(data, message))
        results.extend(self.semiInvertedOnInvertedSearch(data, message))
        return results

    def naturalSearch(self, data, message):
        results = []

        # Search naturally all the possible places of data in message
        indice = 0
        while indice + len(data) <= len(message.getStringData()):
            if message.getStringData()[indice:len(data) + indice] == data:
                # We have a match
                searchResult = SearchResult(message, "Natural search")
                searchResult.addSegment(indice, len(data))
                results.append(searchResult)
            indice = indice + 1

        return results

    def inversedSearch(self, data, message):
        results = []
        invData = data[::-1]

        # Search naturally all the possible places of data in message
        indice = 0
        while indice + len(invData) <= len(message.getStringData()):
            if message.getStringData()[indice:len(invData) + indice] == invData:
                # We have a match
                searchResult = SearchResult(message, "Inverted search")
                searchResult.addSegment(indice, len(invData))
                results.append(searchResult)
            indice = indice + 1

        return results

    def semiInvertedOnNaturalSearch(self, data, message):
        logging.debug("semi inverted = " + str(data))
        results = []
        invData = ""
        for i in range(0, len(data), 2):
            if len(data) > i + 1:
                invData = invData + data[i + 1]
            invData = invData + data[i]

        if len(data) % 2 == 1:
            invData = invData + data[-1]

        # Search naturally all the possible places of data in message
        indice = 0
        while indice + len(invData) <= len(message.getStringData()):
            if message.getStringData()[indice:len(invData) + indice] == invData:
                # We have a match
                searchResult = SearchResult(message, "4bytes inverted on natural search")
                searchResult.addSegment(indice, len(invData))
                results.append(searchResult)
            indice = indice + 1

        return results

    def semiInvertedOnInvertedSearch(self, data, message):

        results = []
        tmpData = data[::-1]
        invData = ""
        for i in range(0, len(tmpData), 2):
            if len(data) > i + 1:
                invData = invData + tmpData[i + 1]
            invData = invData + tmpData[i]

        if len(tmpData) % 2 == 1:
            invData = invData + tmpData[-1]

        # Search naturally all the possible places of data in message
        indice = 0
        while indice + len(invData) <= len(message.getStringData()):
            if message.getStringData()[indice:len(invData) + indice] == invData:
                # We have a match
                searchResult = SearchResult(message, "4bytes inverted on inverted search")
                searchResult.addSegment(indice, len(invData))
                results.append(searchResult)
            indice = indice + 1

        return results
