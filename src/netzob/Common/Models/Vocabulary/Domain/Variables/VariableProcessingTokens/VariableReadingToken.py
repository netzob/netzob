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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Types.Raw import Raw


class VariableReadingToken(AbstractVariableProcessingToken):
    """A communication token used by variable when they are read."""

    def __init__(self, memory=None, value=None, index=0):
        """Constructor of VariableReadingToken:

        :param index: the current reading index in the read value.
        :type index: :class:`int`
        :raise: :class:`ValueError` or :class:`TypeError` if parameters are not valid
        """
        super(VariableReadingToken, self).__init__(memory, value)
        self.index = index

    def toString(self):
        """Used for debug purpose."""
        return "ReadingToken: isOk: {0}, value left: {1}".format(self.isOk, TypeConverter.convert(self.value[self.index:], bitarray, Raw))

    @typeCheck(AbstractVariable, int)
    def read(self, variable, increment):
        """A variable reads a piece of the token value.

        :param variable: store the index+increment section to the variable
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :param increment: the size of the section for which the variable matches >=0
        :type increment: :class:`int`
        :raise: :class:`ValueError` or :class:`TypeError` if parameters are not valid

        """
        if increment < 0:
            raise ValueError("Increment must be >=0")

        self.linkedValues.append((variable.id, self.value[self.index:self.index + increment]))
        self.incrementIndex(increment)

    @typeCheck(int)
    def incrementIndex(self, increment):
        """Increment the current index by the value of provided increment parameter

        >>> rToken = VariableReadingToken()
        >>> print rToken.index
        0
        >>> rToken.incrementIndex(10)
        >>> print rToken.index
        10

        :param increment: the index will be incremented by its valu
        :type increment: :class:`int`
        :raises: TypeError and ValueError if the parameter is not Valid
        """
        if increment is None:
            raise TypeError("The increment cannot be None")

        if increment < 0:
            raise ValueError("The increment must be positive")

        self.index = self.index + increment
