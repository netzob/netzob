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

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class ObservationTable(object):
    """Implementation of an Observation Table (OT) as described by Angluin in "Learning Regular Sets from Queries and Counterexamples"""

    def __init__(self, alphabet):
        self.alphabet = alphabet

        self.__shortPrefixRows = list()
        self.__longPrefixRows = list()
        self.__allRows = list()
        self.__allRowContents = list()
        self.__canonicalRows = list()
        self.__rowContentIds = dict()
        self.__rowMapp = dict()

        self.__numRows = 0
        self.__suffixes = list()
        
    def initialize(self, initialSuffixes, mqOracle):
        if len(self.__allRows) > 0:
            raise Exception("Called initialize, but there are already rows present")

        numSuffixes = len(initialSuffixes)
        self.__suffixes.extend(initialSuffixes)

        numLps = len(self.alphabet)
        numPrefixes = 1 + numLps

        queries = list()
        
        
        

    @property
    def alphabet(self):
        return self.__alphabet

    @alphabet.setter
    def alphabet(self, alphabet):
        self.__alphabet = alphabet
        
