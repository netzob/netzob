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
#| SearchResult:
#|     Definition of the result of a search operation
#+----------------------------------------------
class SearchResult(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, message, description):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.SearchResult.py')
        self.segments = []
        self.message = message
        self.description = description
        self.variationDescription = ""

    def getMessage(self):
        return self.message

    def getVariationDescription(self):
        return self.variationDescription

    def getDescription(self):
        return self.description

    def addSegment(self, i_start, i_end):
        self.segments.append([i_start, i_end])

    def getSegments(self):
        return self.segments

    def setVariationDescription(self, variationDescription):
        self.variationDescription = variationDescription
