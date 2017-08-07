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
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
from netzob.Fuzzing.Generators.PseudoRandomGenerator import PseudoRandomGenerator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.AbstractType import Sign, UnitSize


class BitArrayMutator(DomainMutator):
    """The binary sequence mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The BitArrayMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`,
        :meth:`generate` will be used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param length: The scope of sequence length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional

    The following example shows how to generate a binary sequence with a length
    in [0, 30] interval:

    >>> from netzob.all import *
    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain, length=(0,30), seed=19)
    >>> mutator.generate()
    bitarray('00011000111101111111011001001101110001100110010101001000000000001')

    Constant definitions:
    """

    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 100
    DATA_TYPE = BitArray

    def __init__(self,
                 domain,
                 length=(None, None),  # type: Tuple[int, int]
                 lengthBitSize=None,
                 **kwargs):
        # Call parent init
        super().__init__(domain, **kwargs)

        if (isinstance(length, tuple) and len(length) == 2 and
                all(isinstance(_, int) for _ in length)):
            self._minLength, self._maxLength = length
        size = domain.dataType.size
        if (isinstance(size, tuple) and len(size) == 2 and
                all(isinstance(_, int) for _ in size)):
            # Handle desired interval according to the storage space of the
            # domain dataType
            self._minLength = max(self._minLength, domain.dataType.size[0])
            self._maxLength = min(self._maxLength, domain.dataType.size[1])
        if self._minLength is None or self._maxLength is None:
            self._minLength = self.DEFAULT_MIN_LENGTH
            self._maxLength = self.DEFAULT_MAX_LENGTH

        self._sequenceLength = Field(uint16le())
        self._lengthMutator = IntegerMutator(
            domain=self._sequenceLength.domain,
            interval=(self._minLength, self._maxLength),
            generator='determinist',
            bitsize=lengthBitSize,
            **kwargs)
        self._prng = PseudoRandomGenerator(self._seed)
        self._prng.setInterval((0, (2**64)-1))
        self.updateSeed(self._seed)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._lengthMutator.seed = self._seed
        self._prng.seed = self._seed

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
        # Call parent generate() method
        super().generate()

        lm = self._lengthMutator
        lm_dom = lm.getDomain()
        length = int.from_bytes(lm.generate(),
                                lm_dom.dataType.endianness.value)

        valueBits = bitarray()
        if length == 0:
            return valueBits
        while True:
            valueInt = self._prng.getNewValue()
            bits = TypeConverter.convert(valueInt,
                                         Integer,
                                         BitArray,
                                         src_unitSize=UnitSize.SIZE_64,
                                         src_sign=Sign.UNSIGNED,
                                         dst_sign=Sign.UNSIGNED)
            valueBits += bits
            if len(valueBits) >= length:
                break
        return valueBits[:length]
