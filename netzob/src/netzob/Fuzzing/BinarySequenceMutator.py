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
from netzob.Fuzzing.DeterministIntegerMutator import (
    DeterministIntegerMutator)
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Field import Field
from netzob.Fuzzing.Xorshift128plus import Xorshift128plus
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from bitarray import bitarray


class BinarySequenceMutator(Mutator):
    """The binary sequence mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    >>> from netzob.all import *
    >>> mutator = BinarySequenceMutator()
    >>> binaryField = Field(domain=BitArray())
    >>> mutator.field = binaryField
    >>> dataHex = mutator.mutate()

    """

    MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 100

    def __init__(self,
                 maxLength=None):
        super().__init__()
        if maxLength is None:
            self._maxLength = BinarySequenceMutator.DEFAULT_MAX_LENGTH
        else:
            self._maxLength = maxLength
        self._sequenceLength = Field(uint16le())
        self._lengthMutator = DeterministIntegerMutator(
            domain=self._sequenceLength.domain,
            interval=(BinarySequenceMutator.MIN_LENGTH, self.maxLength))
        self._lengthMutator.field = self._sequenceLength
        self._prng = Xorshift128plus(self.seed)

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

    def getLength(self):
        """The length of the last generated sequence.

        :rtype: :class:`int`
        """
        return self._sequenceLength.value

    def generate(self):
        """This is the fuzz generation method of the binary sequence field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: a generated content represented with bytes
        :rtype: :class:`bytes`
        """
        self._lengthMutator.maxValue = self.maxLength

        length = int.from_bytes(self._lengthMutator.generate(),
                                self._lengthMutator.field.domain.dataType.endianness)

        valueBits = bitarray()
        if length == 0:
            return valueBits
        while True:
            valueInt = self._prng.getNew64bitsValue()
            bits = TypeConverter.convert(data=valueInt,
                                         sourceType=Integer,
                                         destinationType=BitArray,
                                         src_unitSize=AbstractType.UNITSIZE_64,
                                         src_sign=AbstractType.SIGN_UNSIGNED,
                                         dst_sign=AbstractType.SIGN_UNSIGNED)
            valueBits += bits
            if len(valueBits) >= length:
                break
        return valueBits[:length]
