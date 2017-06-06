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
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat


class SequenceMutator(Mutator):
    """The sequence mutator, using a determinist generator to get a sequence
    length.

    >>> from netzob.all import *
    >>> sequenceField = Field(Repeat(String("this is a string"), nbRepeat=2))
    >>> mutator = SequenceMutator()
    >>> mutator.seed = 10
    >>> mutator.field = sequenceField
    >>> dataHex = mutator.generate()

    """

    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 10

    def __init__(self,
                 domain,
                 elementMutator=None,
                 mode=None,
                 length=(None, None),
                 lengthBitSize=None):
        # Sanity checks
        if domain is None:
            raise Exception("Domain should be known to initialize a mutator")
        if not isinstance(domain, Repeat):
            raise Exception("Mutator domain should be of type Repeat. Received object: '{}'".format(domain))

        # Call parent init
        super().__init__(domain=domain, mode=mode)

        if isinstance(length, tuple) and \
           len(length) == 2 and \
           isinstance(length[0], int) and \
           isinstance(length[1], int):
            self._minLength = length[0]
            self._maxLength = length[1]
        if isinstance(domain.nbRepeat, tuple):
            # Handle desired length according to the domain information
            self._minLength = max(self._minLength, int(domain.nbRepeat[0]))
            self._maxLength = min(self._maxLength, int(domain.nbRepeat[1]))
        if self._minLength is None or self._maxLength is None:
            self._minLength = SequenceMutator.DEFAULT_MIN_LENGTH
            self._maxLength = SequenceMutator.DEFAULT_MAX_LENGTH

        if elementMutator is not None and not isinstance(elementMutator, Mutator):
            raise ValueError("{} is not a valid Mutator".format(type(elementMutator)))
        self._elementMutator = elementMutator

        self._sequenceLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._sequenceLength.domain,
            mode=mode,
            interval=(self._minLength, self.maxLength),
            bitsize=lengthBitSize)

    @property
    def lengthMutator(self):
        """The mutator used to generate the sequence length, between
        minLength and maxLength.

        :type: :class:`DeterministIntegerMutator <netzob.Fuzzing.DeterministIntegerMutator>`
        """
        return self._lengthMutator

    @property
    def elementMutator(self):
        """Used to mutate each element of the sequence.
        This mutator depends on the type of the field.

        :type: :class:`Mutator <netzob.Fuzzing.Mutator>`
        """
        return self._elementMutator

    @property
    def minLength(self):
        """The min length of an element of the sequence.
        Default value is DEFAULT_MIN_LENGTH.

        :type: :class:`int`
        """
        return self._minLength

    @minLength.setter
    @typeCheck(int)
    def minLength(self, length_min):
        self._minLength = length_min

    @property
    def maxLength(self):
        """The max length of an element of the sequence.
        Default value is DEFAULT_MAX_LENGTH.

        :type: :class:`int`
        """
        return self._maxLength

    @maxLength.setter
    @typeCheck(int)
    def maxLength(self, length_max):
        self._maxLength = length_max

    def getLength(self):
        """The last generated length of the sequence.

        :rtype: int
        """
        return self._elementLength.value

    def generate(self):
        """This is the fuzz generation method of the sequence field.
        It uses lengthMutator and elementMutator.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        self._lengthMutator.minValue = self.minLength
        self._lengthMutator.maxValue = self.maxLength
        length = int.from_bytes(self._lengthMutator.generate(),
                                self._lengthMutator.domain.dataType.endianness)
        self.domain.nbRepeat = length

        elementValue = self.domain.children[0].dataType.value.tobytes()
        if self._elementMutator is not None:
            elementValue = self._elementMutator.generate()

        value = b''
        if elementValue is not None:
            for _ in range(0, length):
                value = value + elementValue
        return value
