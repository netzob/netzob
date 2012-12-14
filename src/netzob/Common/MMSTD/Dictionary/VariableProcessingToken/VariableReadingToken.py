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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken import \
    AbstractVariableProcessingToken
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class VariableReadingToken(AbstractVariableProcessingToken):
    """VariableReadingToken:
            A communication token used by variable when they are read.
    """

    def __init__(self, negative, vocabulary, memory, value, index):
        """Constructor of VariableReadingToken:

                @type index: integer
                @param index: the current reading index in the read value.
        """
        AbstractVariableProcessingToken.__init__(self, negative, vocabulary, memory, value)
        self.index = index

    def toString(self):
        """toString:
                Used for debug purpose.
        """
        return "ReadingToken: isOk: {0}, value left: {1}".format(str(self.isOk()), TypeConvertor.bin2strhex(self.value[self.index:]))

    def read(self, variable, increment):
        """read:
                A variable reads a piece of the token value.
        """
        self.appendLinkedValue([variable.getID(), self.getValue()[self.index:self.index + increment]])
        self.incrementIndex(increment)

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def incrementIndex(self, increment):
        self.index += increment

    def setIndex(self, index):
        self.index = index
