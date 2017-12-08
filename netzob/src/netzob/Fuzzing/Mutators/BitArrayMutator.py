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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode, center
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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Sign, UnitSize
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
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
    :param interval: The scope of sequence length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type interval: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional


    The following example shows how to generate a fuzzed binary sequence:

    >>> from netzob.all import *
    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain)
    >>> data = mutator.generate()
    >>> len(data)
    8192

    """

    DATA_TYPE = BitArray

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 interval=MutatorInterval.FULL_INTERVAL,
                 lengthBitSize=None):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        # Initialize length generator
        model_min = self.domain.dataType.size[0]
        model_max = self.domain.dataType.size[1]
        model_unitSize = self.domain.dataType.unitSize
        self._initializeLengthGenerator(interval, (model_min, model_max), model_unitSize)

        # Initialize data generator
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

        # Generate length of random data
        if self._lengthGenerator is not None:
            length = next(self._lengthGenerator)
        else:
            raise Exception("Length generator not initialized")

        length = center(length, self._minLength, self._maxLength)

        # Generate random data
        value_bits = bitarray('')
        if length == 0:
            return value_bits.tobytes()
        while True:
            # Generate random sequence of bits, octet per octet
            data_int = int(next(self.generator) * 255)
            data_bytes = data_int.to_bytes(length=1, byteorder='big')
            data_bits = bitarray()
            data_bits.frombytes(data_bytes)

            # Concatenate the generated data
            value_bits += data_bits
            if len(value_bits) >= length:
                break
        return value_bits[:length].tobytes()


def _test():
    r"""

    # Default BitArray type with default fuzzing

    >>> from netzob.all import *
    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain)
    >>> mutator._minLength
    0
    >>> mutator._maxLength
    65536
    >>> mutator.lengthBitSize
    UnitSize.SIZE_16
    >>> len(mutator.generate())
    8192


    # Default BitArray type and fuzzing with specific interval

    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain, interval=(10,30))
    >>> mutator._minLength
    10
    >>> mutator._maxLength
    30
    >>> mutator.lengthBitSize
    UnitSize.SIZE_16
    >>> len(mutator.generate())
    4


    # Default BitArray type and fuzzing with specific interval, and specific length bit size

    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain, interval=(10,30), lengthBitSize=UnitSize.SIZE_8)
    >>> mutator._minLength
    10
    >>> mutator._maxLength
    30
    >>> mutator.lengthBitSize
    UnitSize.SIZE_8
    >>> len(mutator.generate())
    4


    # Default BitArray type and fuzzing with full storage size

    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.FULL_INTERVAL)
    >>> mutator._minLength
    0
    >>> mutator._maxLength
    65536
    >>> mutator.lengthBitSize
    UnitSize.SIZE_16
    >>> len(mutator.generate())
    8192


    # Default BitArray type and fuzzing with full storage size, and specific length bit size

    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.FULL_INTERVAL, lengthBitSize=UnitSize.SIZE_4)
    >>> mutator._minLength
    0
    >>> mutator._maxLength
    16
    >>> mutator.lengthBitSize
    UnitSize.SIZE_4
    >>> len(mutator.generate())
    2


    # BitArray of specific size and fuzzing with default interval

    >>> f = Field(domain=BitArray(nbBits=16), name="data")
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.DEFAULT_INTERVAL)
    >>> mutator._minLength
    16
    >>> mutator._maxLength
    16
    >>> mutator.lengthBitSize
    UnitSize.SIZE_4
    >>> len(mutator.generate())
    2


    # BitArray of specific size and fuzzing with default interval, and specific datatype storage size

    >>> f = Field(domain=BitArray(nbBits=16), name="data")
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.DEFAULT_INTERVAL, lengthBitSize=UnitSize.SIZE_8)
    >>> mutator._minLength
    16
    >>> mutator._maxLength
    16
    >>> mutator.lengthBitSize
    UnitSize.SIZE_8
    >>> len(mutator.generate())
    2


    # BitArray of specific variable size and fuzzing with default interval

    >>> f = Field(domain=BitArray(nbBits=(8, 12)), name="data")
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.DEFAULT_INTERVAL)
    >>> mutator._minLength
    8
    >>> mutator._maxLength
    12
    >>> mutator.lengthBitSize
    UnitSize.SIZE_4
    >>> len(mutator.generate())
    2


    # BitArray of specific variable size and fuzzing with full datatype storage size

    >>> f = Field(domain=BitArray(nbBits=(4, 6)), name="data")
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.FULL_INTERVAL)
    >>> mutator._minLength
    0
    >>> mutator._maxLength
    16
    >>> mutator.lengthBitSize
    UnitSize.SIZE_4
    >>> len(mutator.generate())
    2


    # BitArray of specific variable size and fuzzing with full datatype storage size, and specific length bit size

    >>> f = Field(domain=BitArray(nbBits=(4, 6)), name="data")
    >>> mutator = BitArrayMutator(f.domain, interval=MutatorInterval.FULL_INTERVAL, lengthBitSize=UnitSize.SIZE_8)
    >>> mutator._minLength
    0
    >>> mutator._maxLength
    256
    >>> mutator.lengthBitSize
    UnitSize.SIZE_8
    >>> len(mutator.generate())
    32

    """


def _test_bitarray_length():
    r"""
    # Fuzzing of bitarray generate bitarray with different length

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.BitArrayMutator import BitArrayMutator

    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain)
    
    >>> len_list = []
    >>> duplicata_count = 0
    >>> for _ in range(20):
    ...     curr_len = len(mutator.generate())
    ...     if curr_len in len_list:
    ...         duplicata_count += 1
    ...     len_list.append(curr_len)

    >>> duplicata_count < 5
    True

    """

def _test_bitarray_length_2():
    r"""
    # Fuzzing of bitarray generate positiv value by a determinist generator with lengthBitSize that define the maximum length

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
    >>> from netzob.Fuzzing.Mutators.BitArrayMutator import BitArrayMutator

    >>> fieldBits = Field(BitArray())
    >>> mutator = BitArrayMutator(fieldBits.domain, lengthBitSize=UnitSize.SIZE_16)
    >>> len(mutator.generate())
    65536
    >>> mutator = BitArrayMutator(fieldBits.domain, lengthBitSize=UnitSize.SIZE_8)
    >>> len(mutator.generate())
    256
    >>> mutator = BitArrayMutator(fieldBits.domain, lengthBitSize=UnitSize.SIZE_4)
    >>> len(mutator.generate())
    16

    """
