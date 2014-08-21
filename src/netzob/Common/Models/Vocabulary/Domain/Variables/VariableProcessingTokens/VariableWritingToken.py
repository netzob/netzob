# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray


class VariableWritingToken(AbstractVariableProcessingToken):
    """A communication token used by variables when they are written.
    """

    def __init__(self, memory=None, value=None, generationStrategy=None):
        """Constructor of VariableWritingToken:

        :type value: bitarray
        :param value: the current written value in binary format.
        :param generationStrategy: the strategy that all generation of value for this variable will follow.
        :type generationStrategy: :class:

        """
        super(VariableWritingToken, self).__init__(memory, value)
        self.__generationStrategy = generationStrategy
        if value is not None:
            self.index = len(value)

    def __str__(self):
        """Used for debug purpose.
        """
        return "WritingToken: isOk: {0}, value: {1}".format(self.Ok, TypeConverter.convert(self.value, BitArray, Raw))

    @property
    def generationStrategy(self):
        """The generation strategy that will be used to generate the value."""
        return self.__generationStrategy

    @generationStrategy.setter
    def generationStrategy(self, generationStrategy):
        self.__generationStrategy = generationStrategy
