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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Values.AbstractValue import AbstractValue
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| TextValue:
#|     Represents a text value
#+---------------------------------------------------------------------------+
class TextValue(AbstractValue):

    def __init__(self, text):
        AbstractValue.__init__(self, "TextValue")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.TextValue.py')

        self.strtext = text
        self.bintext = TypeConvertor.string2bin(self.strtext, 'big')

    def send(self, negative, dictionary):
        return (self.bintext, self.strtext)

    def compare(self, val, indice, negative, dictionary):
        self.log.debug("Compare received: '{0}' with '{1}'".format(str(val[indice:]), str(self.bintext)))

        tmp = val[indice:]
        if len(tmp) >= len(self.bintext):
            if tmp[:len(self.bintext)] == self.bintext:
                self.log.debug("Compare successful")
                return indice + len(self.bintext)
        else:
            self.log.debug("Compare fail")
            return -1

    def restore(self):
        return

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
