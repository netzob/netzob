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
        return []


    #+----------------------------------------------
    #| getSearchedDataForHexadecimal:
    #|   Generates data which can represent the specified Hexa
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForHexadecimal(self, value):
        return []

    #+----------------------------------------------
    #| getSearchedDataForString:
    #|   Generates data which can represent the specified string
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForString(self, value):
        data = TypeConvertor.stringToNetzobRaw(value)
        # Creation of a SearchTask
        task = SearchTask(value, Format.STRING)
        task.registerVariation(data, "String representation of the value")
        return [task]

    #+----------------------------------------------
    #| getSearchedDataForIP:
    #|   Generates data which can represent the specified IP
    #| @param value the value to search for
    #+----------------------------------------------
    def getSearchedDataForIP(self, value):
        return []


    #+----------------------------------------------
    #| search:
    #|   Search a set of specified data in the messages
    #| @param tasks the set of "search" task
    #+----------------------------------------------
    def search(self, tasks):
        results = []
        for task in tasks:
            for symbols in self.project.getVocabulary().getSymbols():
                for message in symbols.getMessages():
                    for variation in task.getVariations():
                        task.registerResults(self.extendedSearch(variation, message))

        return tasks

    #+----------------------------------------------
    #| extendedSearch:
    #|   Search for a data in a specified message
    #+----------------------------------------------
    def extendedSearch(self, data, message):
        results = []
        results.extend(self.naturalSearch(data, message))
        return results


    def naturalSearch(self, data, message):
        results = []

        print "Search " + data
        print "in " + message.getStringData()

        # Search naturally all the possible places of data in message
        indice = 0
        while indice + len(data) <= len(message.getStringData()):
            self.log.info("indice = " + str(indice))
            self.log.info(message.getStringData()[indice:len(data) + indice] + "== " + data)
            if message.getStringData()[indice:len(data) + indice] == data:
                # We have a match
                searchResult = SearchResult(message)
                searchResult.addSegment(indice, len(data))
                results.append(searchResult)
            indice = indice + 1

        return results
