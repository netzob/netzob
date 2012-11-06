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
from bitarray import bitarray
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken import \
    AbstractVariableProcessingToken
from netzob.Common.Type.TypeConvertor import TypeConvertor


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
        AbstractVariableProcessingToken.__init__(self, negative, vocabulary, memory, value)
        self.generationStrategy = generationStrategy
        self.index = len(value)

    def toString(self):
        """toString:
                Used for debug purpose.
        """
        return "WritingToken: isOk: {0}, value: {1}".format(str(self.isOk()), TypeConvertor.bin2strhex(self.value))

    def updateValue(self):
        """updateValue:
                Re-make the value of the token by concatenating each segment of the chopped value.
        """
        self.value = bitarray()
        self.index = 0
        for linkedValue in self.getLinkedValue():
            self.appendValue(linkedValue[1])

    def setValueForVariable(self, variable, value):
        """setValueForVariable:
                Edit the previously inserted value for specified variable and replace it
                with the provided value
        """
        for linkedValue in self.getLinkedValue():
            if linkedValue[0] == variable.getID():
                linkedValue[1] = value
                break

        # refresh the computed value
        self.updateValue()

    def write(self, variable, value):
        """write:
                A variable writes a value in the token.
        """
        self.appendLinkedValue([variable.getID(), value])
        self.updateValue()

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getGenerationStrategy(self):
        return self.generationStrategy

    def appendValue(self, value):
        if value is not None:
            self.index += len(value)
            self.value += value
