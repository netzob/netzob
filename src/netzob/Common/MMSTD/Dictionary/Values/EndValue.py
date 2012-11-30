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
from gettext import gettext as _
import logging
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Values.AbstractValue import AbstractValue


#+---------------------------------------------------------------------------+
#| EndValue:
#|     Represents the end of a symbol
#+---------------------------------------------------------------------------+
class EndValue(AbstractValue):

    def __init__(self):
        AbstractValue.__init__(self, "EndValue")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.EndValue.py')

    def send(self, negative, dictionary):
        return (bitarray(endian='big'), "")

    def compare(self, val, indice, negative, dictionary):
        self.log.debug("Endvalue ? indice = " + str(indice))
        if len(val[indice:]) == 0:
            self.log.debug("Compare successful (" + str(indice) + " != " + str(len(val)) + ")")
            return indice
        else:
            cr = bitarray('00001010', endian='big')

            if val[indice:] == cr:
                self.log.debug("Compare successfull we consider \\n as the end")
                return indice + len(cr)

            self.log.debug("Compare Fail, received '" + str(val[indice:]) + "'")
            return -1

    def restore(self):
        return

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
