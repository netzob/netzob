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
from netzob.Fuzzing.all import (DeterministIntegerMutator,
                                StringPaddedGenerator)
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.String import String
from netzob.all import Field


class StringMutator(Mutator):
    """The string mutator, using a determinist generator to get a string length.
    The generated string shall not be longer than 2^16 bytes.

    >>> from netzob.all import *
    >>> mutator = StringMutator()
    >>> asciiString = String()
    >>> mutator.field = asciiString
    >>> dataHex = mutator.mutate()

    """

    DEFAULT_END_CHAR = '\0'
    DEFAULT_MIN_LENGTH = 2
    DEFAULT_MAX_LENGTH = 10
    DEFAULT_NAUGHTY_STRINGS = ["System(\"ls -al /\")",
                               "`ls -al /`",
                               "Kernel.exec(\"ls -al /\")",
                               "Kernel.exit(1)",
                               "%x('ls -al /')",
                               "<img \\x00src=x onerror=\"alert(1)\">",
                               "$ENV{'HOME'}",
                               "%d",
                               "%s"]
    PADDING_CHAR = ' '
    METHOD_PADDING_TRUNCATE = 0
    METHOD_CONCATENATE = 1

    def __init__(self,
                 endChar=None,
                 minLength=None,
                 maxLength=None,
                 naughtyStrings=None,
                 method=None):
        super().__init__()

        if endChar is None:
            self._endChar = StringMutator.DEFAULT_END_CHAR
        else:
            self._endChar = endChar
        if minLength is None:
            self._minLength = StringMutator.DEFAULT_MIN_LENGTH
        else:
            self._minLength = minLength
        if maxLength is None:
            self._maxLength = StringMutator.DEFAULT_MAX_LENGTH
        else:
            self._maxLength = maxLength
        if naughtyStrings is None or not isinstance(naughtyStrings, list):
            self._naughtyStrings = StringMutator.DEFAULT_NAUGHTY_STRINGS
        else:
            self._naughtyStrings = naughtyStrings
        if method is None or (method != StringMutator.METHOD_PADDING_TRUNCATE
                              and method != StringMutator.METHOD_CONCATENATE):
            self._method = StringMutator.METHOD_PADDING_TRUNCATE
        else:
            self._method = method

        self._stringLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            minValue=self._minLength,
            maxValue=self.maxLength)
        self._lengthMutator.field = self._stringLength

        self._sg = StringPaddedGenerator(self._lengthMutator,
                                         self._naughtyStrings)

    @property
    def lengthMutator(self):
        """The mutator used to generate the string length, between
        minLength and maxLength.

        :type: :class:`DeterministIntegerMutator <netzob.Fuzzing.DeterministIntegerMutator>`
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
        return self._endChar

    @endChar.setter
    @typeCheck(str)
    def endChar(self, char):
        self._endChar = char

    def getLength(self):
        """The length of the last generated string.

        :rtype: :class:`int`
        """
        return self._stringLength.value

    @property
    def naughtyStrings(self):
        """The string list to use for the mutation.

        :type: :class:`list`
        """
        return self._naughtyStrings

    @naughtyStrings.setter
    @typeCheck(int)
    def naughtyStrings(self, testStrings):
        self._naughtyStrings = testStrings

    def mutate(self):
        """This is the mutation method of the string field.
        It uses lengthMutator, then a random generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        if self.field is not None:
            if self._currentCounter < self.counterMax:
                self._currentCounter += 1
                value = self._sg.getNewValue(self.endChar)
                return String.decode(value,
                                     unitSize=self.field.domain.dataType.unitSize,
                                     endianness=self.field.domain.dataType.endianness,
                                     sign=self.field.domain.dataType.sign)
            else:
                raise Exception("Max mutation counter reached")
        else:
            raise Exception("Field to mutate not set")
