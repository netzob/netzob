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


#+----------------------------------------------
#| Local Imports
#+----------------------------------------------

#+----------------------------------------------
#| SearchTask:
#|     Describes a search operation
#+----------------------------------------------
class SearchTask(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param data: the searched data
    #| @param type: the type of the searched data
    #+----------------------------------------------
    def __init__(self, description, data, type):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.SearchTask.py')
        self.description = description
        self.data = data
        self.type = type
        self.searchedDatas = dict()
        self.results = []

    def registerResults(self, r, v):
        for result in r:
            result.setVariationDescription(v)
            self.results.append(result)

    def getResults(self):
        return self.results

    def registerVariation(self, data, description):
        self.searchedDatas[data] = description

    def getVariations(self):
        return self.searchedDatas

    def getDescription(self):
        return self.description
