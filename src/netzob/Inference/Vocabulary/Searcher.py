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
from netzob.Common.TypeConvertor import TypeConvertor
from netzob.Inference.Vocabulary.SearchResult import SearchResult


#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Searcher :
#|     Provides multiple algorithms for a searching after a pattern in a 
#|     set of computed messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Searcher(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param messages the list of messages it will search in
    #+----------------------------------------------   
    def __init__(self, messages):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Searcher.py')
        self.messages = messages
    
    
    #+---------------------------------------------- 
    #| getSearchedDataForBinary :
    #|   Generates data which can represent the specified Binary
    #| @param value the value to search for
    #+---------------------------------------------- 
    def getSearchedDataForBinary(self, value):
        return []
    
    
    #+---------------------------------------------- 
    #| getSearchedDataForOctal :
    #|   Generates data which can represent the specified Octal
    #| @param value the value to search for
    #+---------------------------------------------- 
    def getSearchedDataForOctal(self, value):
        return []
    
    
    #+---------------------------------------------- 
    #| getSearchedDataForHexadecimal :
    #|   Generates data which can represent the specified Hexa
    #| @param value the value to search for
    #+---------------------------------------------- 
    def getSearchedDataForHexadecimal(self, value):
        return []
    
    #+---------------------------------------------- 
    #| getSearchedDataForASCII :
    #|   Generates data which can represent the specified ASCII
    #| @param value the value to search for
    #+---------------------------------------------- 
    def getSearchedDataForASCII(self, value):
        data = TypeConvertor.ASCIIToNetzobRaw(value)
        return [data]
    
    #+---------------------------------------------- 
    #| getSearchedDataForIP :
    #|   Generates data which can represent the specified IP
    #| @param value the value to search for
    #+---------------------------------------------- 
    def getSearchedDataForIP(self, value):
        return []
        
    
    #+---------------------------------------------- 
    #| search :
    #|   Search a set of specified data in the messages
    #| @param datas set of data to search for
    #+----------------------------------------------
    def search(self, datas):
        results = []
        for data in datas :
            for message in self.messages :
                results.extend(self.extendedSearch(data, message))
        return results
    
    #+---------------------------------------------- 
    #| extendedSearch :
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
        while indice + len(data) <= len(message.getStringData()) :
            self.log.info("indice = " + str(indice))
            self.log.info(message.getStringData()[indice:len(data) + indice] + "== " + data)
            if message.getStringData()[indice:len(data) + indice] == data :
                # We have a match
                searchResult = SearchResult()
                searchResult.addSegment(indice, len(data))
                results.append(searchResult)
            indice = indice + 1
        
        return results
