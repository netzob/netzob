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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
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
        Default value is UnitSize.SIZE_8.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional

    The following example shows how to generate a binary sequence with a length
    in [0, 30] interval:

    >>> from netzob.all import *
    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain)
    >>> mutator.generate()
    bitarray('110001010111010000000101010011111010001000110110101111111011000001111111100111010011100110001100001100101011010011000010101100010010101101001010000101101001110110101111011100111111010000010000000000010000001010000011000111101101000000000111100111001100110')

    >>> from netzob.all import *
    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain, interval=(0,30), seed=19)
    >>> mutator.generate()
    bitarray('000110001111011111000010111000000011111100110111001000110101110001010100110110010001010100111111101011000000011011001110011111001111101110010011101000101011101000110111010001101000110010001100100010111010100100111011111011000001110100011101011111111110100')

    """

    DEFAULT_MIN_LENGTH = 4
    DEFAULT_MAX_LENGTH = 80
    DATA_TYPE = BitArray

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 interval=MutatorInterval.DEFAULT_INTERVAL,
                 lengthBitSize=UnitSize.SIZE_8):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Initialize generator
        self.initializeGenerator(interval, lengthBitSize)

    def initializeGenerator(self, interval, lengthBitSize):

        minLength = None
        maxLength = None

        # Check min, max interval
        if (isinstance(interval, tuple) and len(interval) == 2 and
                all(isinstance(_, int) for _ in interval)):
            minLength, maxLength = interval
        size = self.domain.dataType.size
        if (isinstance(size, tuple) and len(size) == 2 and
                all(isinstance(_, int) for _ in size)):
            # Handle desired interval according to the storage space of the
            # domain dataType
            minLength = max(minLength, self.domain.dataType.size[0])
            maxLength = min(maxLength, self.domain.dataType.size[1])
        if minLength is None or maxLength is None:
            minLength = self.DEFAULT_MIN_LENGTH
            maxLength = self.DEFAULT_MAX_LENGTH

        # Check lengthBitSize
        if isinstance(lengthBitSize, UnitSize):
            lengthBitSize = lengthBitSize.value

        # Build the length generator
        self.lengthGenerator = GeneratorFactory.buildGenerator(DeterministGenerator.NG_determinist,
                                                               seed = self.seed,
                                                               minValue = minLength,
                                                               maxValue = maxLength,
                                                               bitsize = lengthBitSize,
                                                               signed = False)

        # Build the data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed)

    def generate(self):
        """This is the fuzz generation method of the binary sequence field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: a generated content represented with a bit array
        :rtype: :class:`bitarray`
        """
        # Call parent generate() method
        super().generate()

        length = next(self.lengthGenerator)

        valueBits = bitarray()
        if length == 0:
            return valueBits
        while True:
            valueInt = int(next(self.generator) * 65535)
            valueBits += Integer(valueInt, unitSize=UnitSize.SIZE_16, sign=Sign.UNSIGNED).value
            if len(valueBits) >= length:
                break
        return valueBits[:length]
