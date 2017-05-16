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
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint32le


class SequenceMutator(Mutator):
    """The sequence mutator, using a determinist generator to get a sequence
    length.

    >>> from netzob.all import *
    >>> sequenceField = Field(Repeat(String("this is a string"), nbRepeat=2))
    >>> mutator = SequenceMutator()
    >>> mutator.seed = 10
    >>> mutator.field = sequenceField
    >>> dataHex = mutator.mutate()

    """

    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 1

    def __init__(self):
        self._elementMutator = None
        self._minLength = SequenceMutator.DEFAULT_MIN_LENGTH
        self._maxLength = SequenceMutator.DEFAULT_MAX_LENGTH
        self._elementLength = uint32le()
        self._lengthMutator = DeterministIntegerMutator(
            minValue=self._minLength,
            maxValue=self.maxLength)
        self._lengthMutator.field = self._elementLength

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

    @elementMutator.setter
    @typeCheck(Mutator)
    def elementMutator(self, mutator):
        self._elementMutator = mutator

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
        """The length of the last generated elements of the sequence.

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
        generatedLength = int(self._lengthMutator.mutate(), 16)
        # TODO : implement the sequence generator, which uses generatedLength
        return super().generate()
