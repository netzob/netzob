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


#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken import AbstractVariableProcessingToken


class VariableWritingToken(AbstractVariableProcessingToken):
    """VariableWritingToken:
            A communication token used by variable when they are written.
    """

    def __init__(self, negative, vocabulary, memory, value, generationStrategy):
        """Constructor of VariableWritingToken:

                @type value: bitarray
                @param value: the current written value in binary format.
                @type generationStrategy: string
                @param generationStrategy: the strategy that all generation of value for this variable will follow.
        """
        AbstractVariableProcessingToken.__init__(self, negative, vocabulary, memory)
        self.value = value
        self.generationStrategy = generationStrategy
        self.index = len(value)

    def toString(self):
        """toString:
                Used for debug purpose.
        """
        return _("isOk: {0}, value: {1}").format(str(self.isOk()), str(self.value))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getValue(self):
        return self.value

    def getGenerationStrategy(self):
        return self.generationStrategy

    def getIndex(self):
        return self.index

    def setValue(self, value):
        self.index = len(value)
        self.value = value

    def appendValue(self, value):
        self.index += len(value)
        self.value += value
