# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Fuzzing.PseudoRandomIntegerMutator import (
    PseudoRandomIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint32le


class StringMutator(Mutator):
    """The string mutator, using a pseudo-random generator to get a string length.
    The generated string shall not be longer than 2^32.

    >>> from netzob.all import *
    >>> mutator = StringMutator()
    >>> mutator.seed = 10
    >>> asciiString = ASCII()
    >>> mutator.field = asciiString
    >>> dataHex = mutator.mutate()

    """

    DEFAULT_END_CHAR = '\0'
    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 10

    def __init__(self):
        super().__init__()
        self._endChar = StringMutator.DEFAULT_END_CHAR
        self._minLength = StringMutator.DEFAULT_MIN_LENGTH
        self._maxLength = StringMutator.DEFAULT_MAX_LENGTH
        self._stringLength = uint32le()
        self._lengthMutator = PseudoRandomIntegerMutator(
            minValue=self._minLength,
            maxValue=self.maxLength)
        self._lengthMutator.field = self._stringLength

    @property
    def lengthMutator(self):
        """The mutator used to generate the string length, between
        minLength and maxLength.

        :type: :class:`PseudoRandomIntegerMutator <netzob.Fuzzing.PseudoRandomIntegerMutator>`
        """
        return self._lengthMutator

    @property
    def minLength(self):
        """The min length of the string. Default value is DEFAULT_MIN_LENGTH.

        :type: :class:`int`
        """
        return self._minLength

    @minLength.setter
    @typeCheck(int)
    def minLength(self, length_min):
        self._minLength = length_min

    @property
    def maxLength(self):
        """The max length of the string. Default value is DEFAULT_MAX_LENGTH.

        :type: :class:`int`
        """
        return self._maxLength

    @maxLength.setter
    @typeCheck(int)
    def maxLength(self, length_max):
        self._maxLength = length_max

    @property
    def endChar(self):
        """The character defining the end of the string. Default value is
        DEFAULT_END_CHAR.

        :type: :class:`str`
        """
        return self._field

    @endChar.setter
    @typeCheck(str)
    def endChar(self, char):
        self._endChar = char

    def getLength(self):
        """The length of the last generated string.

        :rtype: :class:`int`
        """
        return self._stringLength.value

    def mutate(self):
        """This is the mutation method of the string field.
        It uses lengthMutator, then a random generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """

        self._lengthMutator.minValue = self.minLength
        self._lengthMutator.maxValue = self.maxLength
        generatedLength = int(self._lengthMutator.mutate(), 16)
        # TODO : implement the string generator, which uses generatedLength
        return super().mutate()
