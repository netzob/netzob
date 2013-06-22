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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.AbstractType import AbstractType


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
        self.__logger = logging.getLogger(__name__)
        self.__generationStrategy = generationStrategy
        if value is not None:
            self.index = len(value)

    def toString(self):
        """Used for debug purpose.
        """
        return "WritingToken: isOk: {0}, value: {1}".format(self.isOk, TypeConverter.convert(self.value, bitarray, Raw))

    def updateValue(self):
        """Re-make the value of the token by concatenating each segment of the chopped value.
        """
        self.value = bitarray(endian=AbstractType.defaultEndianness())
        self.index = 0

        for linkedValue in self.linkedValues:
            self.__appendValue(linkedValue[1])

    @typeCheck(AbstractVariable, bitarray)
    def setValueForVariable(self, variable, value):
        """Edit the previously inserted value for specified variable
        and replace with the provided value.

        :param variable: the variable for which we modify its value
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :raises :class:`TypeError ` if parameters are not valid.

        """
        if variable is None:
            raise TypeError("a variable must be specified")

        # we are interesting in the last value.
        if self.linkedValues is not None:
            for linkedValue in reversed(self.linkedValues):  # We iterate the list in reverse order.
                if linkedValue[0] == variable.id:
                    linkedValue[1] = value
                    break
        # refresh the computed value
        self.updateValue()

    @typeCheck(AbstractVariable, bitarray)
    def write(self, variable, value):
        """A variable writes a value in the token.

        :param variable: the variable for which the value must be modified.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariables.AbstractVariable
        :raises: :class:`TypeError ` if parameters are not valid.
        """
        if variable is None:
            raise TypeError("a variable must be specified.")
        if value is None:
            raise TypeError("value cannot be None")

        self.linkedValues.append((variable.id, value))
        self.updateValue()

    @typeCheck(bitarray)
    def __appendValue(self, value):
        """Append in the current value the specified value.

        :param value: the value to append
        :type value: :class:`bitarray`.
        :raises: :class:`TypeError` if parameter is not valid
        """
        if value is not None:
            self.index += len(value)
            self.value += value

    @property
    def generationStrategy(self):
        """The generation strategy that will be used to generate the value."""
        return self.__generationStrategy

    @generationStrategy.setter
    def generationStrategy(self, generationStrategy):
        self.__generationStrategy = generationStrategy
