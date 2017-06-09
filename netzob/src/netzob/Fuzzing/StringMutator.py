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
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
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
from netzob.Fuzzing.DeterministIntegerMutator import DeterministIntegerMutator
from netzob.Fuzzing.StringPaddedGenerator import StringPaddedGenerator
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


class StringMutator(Mutator):
    """The string mutator, using a determinist generator to get a string length.
    The generated string shall not be longer than 2^16 bytes.

    The StringMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to **Mutator.GENERATE**, the generate() method will be
        used to produce the value.
        If set to **Mutator.MUTATE**, the mutate() method will be used to
        produce the value (not implemented).
        Default value is **Mutator.GENERATE**.
    :param endChar: The character(s) ending the string.
        Default value is **DEFAULT_END_CHAR**.
    :param length: The scope of string length to generate. If set to
        (min, max), the values will be generate between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :param naughtyStrings: The list of potentially dangerous strings.
        Default value is **DEFAULT_NAUGHTY_STRINGS**.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type endChar: :class:`str`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional
    :type naughtyStrings: :class:`list` of :class:`str`, optional

    The following example shows how to generate a string with a length in
    [35, 60] interval, the smaller one between the field domain and the length
    given to the constructor of StringMutator:

    >>> from netzob.all import *
    >>> fieldString = Field(String(nbChars=(35, 60)))
    >>> mutator = StringMutator(fieldString.domain, length=(10,600))
    >>> mutator.seed = 10
    >>> mutator.generate()
    b'`ls -al /`\x00     '

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

    def __init__(self,
                 domain,
                 mode=None,
                 endChar=DEFAULT_END_CHAR,
                 length=(None, None),
                 lengthBitSize=None,
                 naughtyStrings=None):
        # Sanity checks
        if domain is None:
            raise Exception("Domain should be known to initialize a mutator")
        if not isinstance(domain, AbstractVariable):
            raise Exception("Mutator domain should be of type AbstractVariable. Received object: '{}'".format(domain))
        if not hasattr(domain, 'dataType'):
            raise Exception("Mutator domain should have a dataType")
        if not isinstance(domain.dataType, String):
            raise Exception("Mutator domain dataType should be an Integer, not '{}'".format(type(domain.dataType)))

        # Call parent init
        super().__init__(domain=domain, mode=mode)

        self._endChar = endChar

        if isinstance(length, tuple) and \
           len(length) == 2 and \
           isinstance(length[0], int) and \
           isinstance(length[1], int):
            self._minLength = length[0]
            self._maxLength = length[1]
        if isinstance(domain.dataType.size, tuple) and \
           len(domain.dataType.size) == 2 and \
           isinstance(domain.dataType.size[0], int) \
           and isinstance(domain.dataType.size[1], int):
            # Handle desired interval according to the storage space of the domain dataType
            self._minLength = max(self._minLength, int(domain.dataType.size[0]/8))
            self._maxLength = min(self._maxLength, int(domain.dataType.size[1]/8))
        if self._minLength is None or self._maxLength is None:
            self._minLength = StringMutator.DEFAULT_MIN_LENGTH
            self._maxLength = StringMutator.DEFAULT_MAX_LENGTH

        if not isinstance(naughtyStrings, list):
            self._naughtyStrings = StringMutator.DEFAULT_NAUGHTY_STRINGS
        else:
            self._naughtyStrings = naughtyStrings
        self._method = method

        self._stringLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._stringLength.domain,
            mode=mode,
            interval=(self._minLength, self.maxLength),
            bitsize=lengthBitSize)

        self._sg = StringPaddedGenerator(self._lengthMutator,
                                         self._naughtyStrings)
        self._seed = 0

    @property
    def seed(self):
        """The seed used in generator
        Default value is 0.

        :type: :class:`int`
        """
        return self._seed

    @seed.setter
    @typeCheck(int)
    def seed(self, seedValue):
        self._seed = seedValue
        self._lengthMutator.seed = self._seed
        self._sg.seed = self._seed

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

    @property
    def maxLength(self):
        """The max length of the string. Default value is DEFAULT_MAX_LENGTH.

        :type: :class:`int`
        """
        return self._maxLength

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

    def generate(self):
        """This is the fuzz generation method of the string field.
        It uses lengthMutator, then a random generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        if self.domain is not None:
            if self._currentCounter < self.counterMax:
                self._currentCounter += 1
                value = self._sg.getNewValue(self.endChar)
                return String.decode(value,
                                     unitSize=self.domain.dataType.unitSize,
                                     endianness=self.domain.dataType.endianness,
                                     sign=self.domain.dataType.sign)
            else:
                raise Exception("Max mutation counter reached")
        else:
            raise Exception("Field to mutate not set")
