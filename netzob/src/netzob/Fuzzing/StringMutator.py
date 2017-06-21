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
from typing import Tuple  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.DomainMutator import DomainMutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Fuzzing.DeterministIntegerMutator import DeterministIntegerMutator
from netzob.Fuzzing.StringPaddedGenerator import StringPaddedGenerator
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Field import Field


class StringMutator(DomainMutator):
    """The string mutator, using a determinist generator to get a string length.
    The generated string shall not be longer than 2^16 bytes.

    The StringMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to **MutatorMode.GENERATE**, the generate() method will be
        used to produce the value.
        If set to **MutatorMode.MUTATE**, the mutate() method will be used to
        produce the value (not implemented).
        Default value is **MutatorMode.GENERATE**.
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
    >>> mutator = StringMutator(fieldString.domain, length=(10,600), seed=10)
    >>> mutator.generate()  # doctest: +SKIP
    b'`ls -al /`\x00     '

    Constant definitions:
    """

    DEFAULT_END_CHAR = '\0'
    DEFAULT_MIN_LENGTH = 2
    DEFAULT_MAX_LENGTH = 10
    DEFAULT_NAUGHTY_STRINGS = """
    System("ls -al /"),
    `ls -al /`,
    Kernel.exec("ls -al /"),
    Kernel.exit(1),
    %x('ls -al /'),
    <img \\x00src=x onerror="alert(1)">,
    $ENV{'HOME'},
    %d,
    %s
    """.split()
    PADDING_CHAR = ' '

    def __init__(self,
                 domain,
                 endChar=DEFAULT_END_CHAR,  # type: str
                 length=(None, None),       # type: Tuple[int, int]
                 lengthBitSize=None,
                 naughtyStrings=None,
                 **kwargs):
        # Sanity checks
        if not isinstance(domain.dataType, String):
            raise Exception("Mutator domain dataType should be an Integer, not '{}'"
                            .format(type(domain.dataType)))

        # Call parent init
        super().__init__(domain, **kwargs)

        self._endChar = endChar

        if isinstance(length, tuple) and len(length) == 2 and all(isinstance(_, int) for _ in length):
            self._minLength, self._maxLength = length
        dom_size = domain.dataType.size
        if isinstance(dom_size, tuple) and len(dom_size) == 2 and all(isinstance(_, int) for _ in dom_size):
            # Handle desired interval according to the storage space of the domain dataType
            self._minLength = max(self._minLength, int(dom_size[0] / 8))
            self._maxLength = min(self._maxLength, int(dom_size[1] / 8))
        if self._minLength is None or self._maxLength is None:
            self._minLength = self.DEFAULT_MIN_LENGTH
            self._maxLength = self.DEFAULT_MAX_LENGTH

        if not isinstance(naughtyStrings, list):
            self._naughtyStrings = self.DEFAULT_NAUGHTY_STRINGS
        else:
            self._naughtyStrings = naughtyStrings

        self._stringLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._stringLength.domain,
            interval=(self._minLength, self._maxLength),
            bitsize=lengthBitSize,
            **kwargs)

        self._sg = StringPaddedGenerator(self._lengthMutator,
                                         self._naughtyStrings)
        self._seed = 0

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._lengthMutator.updateSeed(seedValue)
        self._sg.updateSeed(seedValue)

    def getLength(self):
        """The length of the last generated string.

        :rtype: :class:`int`
        """
        return self._stringLength.value

    @property
    def naughtyStrings(self):
        """
        Property (getter).
        The string list to use for the mutation.

        :type: :class:`list`
        """
        return self._naughtyStrings

    def generate(self):
        """This is the fuzz generation method of the string field.
        It uses lengthMutator, then a random generator to produce the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        super().generate()

        value = self._sg.getNewValue(self._endChar)
        value = self._sg.getNewValue(self._endChar)
        dom_type = self.getDomain().dataType
        return String.decode(value,
                             unitSize=dom_type.unitSize,
                             endianness=dom_type.endianness,
                             sign=dom_type.sign)

    def mutate(self, data):
        raise NotImplementedError
