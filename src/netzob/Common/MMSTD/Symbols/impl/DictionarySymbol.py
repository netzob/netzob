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

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol


#+---------------------------------------------------------------------------+
#| DictionarySymbol:
#|     Definition of a symbol based on a dictionary
#+---------------------------------------------------------------------------+
class DictionarySymbol(AbstractSymbol):

    def __init__(self, dictionaryEntry):
        AbstractSymbol.__init__(self, "DictionarySymbol")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Symbols.impl.DictionarySymbol.py')
        self.entry = dictionaryEntry

    def isEquivalent(self, symbol):
        if self.entry.getID() == symbol.getID():
            self.log.debug("The symbols are equivalents")
            return True
        else:
            self.log.debug("The symbols are not equivalents")
            return False

    def getValueToSend(self, inverse, vocabulary, memory):
        result = self.entry.getValueToSend(inverse, vocabulary, memory)
        return result

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.entry.getID()

    def getEntry(self):
        return self.entry

    def getName(self):
        return self.entry.getName()

    def setID(self, id):
        self.id = id

    def setEntry(self, entry):
        self.entry = entry

    def __str__(self):
        return str(self.entry)

    def __repr__(self):
        return str(self.entry)

    def __cmp__(self, other):
        if other == None:
            return 0
        try:
            if self.getID() == other.getID() and self.getEntry() == other.getEntry():
                return 0
            else:
                return 1
        except:
            self.log.warn("Tried to compare a DictionarySymbol with " + str(other))
            return 1
