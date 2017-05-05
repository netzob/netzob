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
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint32le
from netzob.Common.Utils.Decorators import typeCheck


class BinarySequenceMutator(Mutator):
    """The binary sequence mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    >>> from netzob.all import *
    >>> mutator = BinarySequenceMutator()
    >>> mutator.seed = 10
    >>> binaryField = Field(domain=BitArray())
    >>> mutator.field = binaryField
    >>> dataHex = mutator.mutate()

    """

    MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 100

    def __init__(self):
        super().__init__()
        self._maxLength = BinarySequenceMutator.DEFAULT_MAX_LENGTH
        self._sequenceLength = uint32le()
        self._lengthMutator = DeterministIntegerMutator(
            minValue=BinarySequenceMutator.MIN_LENGTH,
            maxValue=self.maxLength)
        self._lengthMutator.field = self._sequenceLength

    @property
    def lengthMutator(self):
        """The mutator used to generate the sequence length, between
        MIN_LENGTH and maxLength.

        :type: :class:`DeterministIntegerMutator <netzob.Fuzzing.DeterministIntegerMutator>`
        """
        return self._lengthMutator

    @property
    def maxLength(self):
        """The max length of the binary sequence. Default value is DEFAULT_MAX_LENGTH.

        :type: :class:`int`
        """
        return self._maxLength

    @maxLength.setter
    @typeCheck(int)
    def maxLength(self, length_max):
        self._maxLength = length_max

    def getLength(self):
        """The length of the last generated sequence.

        :rtype: :class:`int`
        """
        return self._sequenceLength.value

    def mutate(self):
        """This is the mutation method of the binary sequence field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        self._lengthMutator.maxValue = self.maxLength
        generatedLength = int(self._lengthMutator.mutate(), 16)
        # TODO : implement the sequence generator, which uses generatedLength
        return super().mutate()
