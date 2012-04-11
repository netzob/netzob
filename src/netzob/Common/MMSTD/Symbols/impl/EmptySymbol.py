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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol


#+---------------------------------------------------------------------------+
#| EmptySymbol:
#|     Definition of an empty symbol
#+---------------------------------------------------------------------------+
class EmptySymbol(AbstractSymbol):

    # Name of the "type" of the symbol
    TYPE = "EmptySymbol"

    def __init__(self):
        AbstractSymbol.__init__(self, EmptySymbol.TYPE)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Symbols.impl.EmptySymbol.py')

    def isEquivalent(self, symbol):

        if symbol.__class__.__name__ == EmptySymbol.__name__:
            self.log.debug("The symbols are equivalents")
            return True
        else:
            self.log.debug("The symbols are not equivalents")
            return False

    def getValueToSend(self, inverse, vocabulary, memory):
        return (bitarray(endian='big'), "")

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return "EmptySymbol"

    def getEntry(self):
        return None

    def getName(self):
        return "EmptySymbol"

    def __str__(self):
        return "EmptySymbol"

#    def setID(self, id):
#        self.id = id
#    def setEntry(self, entry):
#        self.entry = entry
