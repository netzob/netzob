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
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator, FuzzingMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, FuzzingInterval
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Common.Utils.Decorators import NetzobLogger


@NetzobLogger
class BitArrayMutator(DomainMutator):
    """The binary sequence mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The BitArrayMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`,
        :meth:`generate` will be used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
    :param interval: The scope of sequence length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
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
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 interval=FuzzingInterval.FULL_INTERVAL,
                 lengthBitSize=None):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:

            # Initialize data generator
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=(1 << 32) - 1)  # in order to generate 4 bytes of random data at each call

            # Initialize length generator
            model_min = self.domain.dataType.size[0]
            model_max = self.domain.dataType.size[1]
            model_unitSize = self.domain.dataType.unitSize
            self._initializeLengthGenerator(generator, interval, (model_min, model_max), model_unitSize)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> f = Field(BitArray())
        >>> m = BitArrayMutator(f.domain).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        m = BitArrayMutator(self.domain,
                            mode=self.mode,
                            generator=self.generator,
                            seed=self.seed,
                            counterMax=self.counterMax,
                            lengthBitSize=self.lengthBitSize)
        return m

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(BitArray())
        >>> BitArrayMutator(f.domain).count()
        86400000000

        >>> f = Field(BitArray(nbBits=4))
        >>> BitArrayMutator(f.domain).count()
        16

        >>> f = Field(BitArray(nbBits=1))
        >>> BitArrayMutator(f.domain).count()
        2

        >>> f = Field(BitArray(nbBits=(1, 3)))
        >>> BitArrayMutator(f.domain).count()
        14

        >>> f = Field(BitArray("0101"))
        >>> BitArrayMutator(f.domain).count()
        16

        """

        if self.mode == FuzzingMode.FIXED:
            count = 1
        else:
            range_min = self.domain.dataType.size[0]
            range_max = self.domain.dataType.size[1]
            permitted_values = 2
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
        return count

    def generate(self):
        """This is the fuzz generation method of the binary sequence field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: a generated content represented with a bit array
        :rtype: :class:`bitarray`
        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            valueBytes = next(self.generator)
        else:

            # Generate length of random data
            length = next(self._lengthGenerator)

            # Generate random data
            value_bits = bitarray('')
            if length == 0:
                return value_bits.tobytes()
            while True:
                # Generate random sequence of bits, octet per octet
                data_int = next(self.generator)
                data_bytes = data_int.to_bytes(4, byteorder='big')
                data_bits = bitarray()
                data_bits.frombytes(data_bytes)

                # Concatenate the generated data
                value_bits += data_bits
                if len(value_bits) >= length:
                    break
            valueBytes = value_bits[:length].tobytes()

        return valueBytes


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
    2


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
    2


    # Default BitArray type and fuzzing with full storage size

    >>> f = Field(BitArray())
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.FULL_INTERVAL)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.FULL_INTERVAL, lengthBitSize=UnitSize.SIZE_4)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.DEFAULT_INTERVAL)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.DEFAULT_INTERVAL, lengthBitSize=UnitSize.SIZE_8)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.DEFAULT_INTERVAL)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.FULL_INTERVAL)
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
    >>> mutator = BitArrayMutator(f.domain, interval=FuzzingInterval.FULL_INTERVAL, lengthBitSize=UnitSize.SIZE_8)
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
    >>> different_count = 0
    >>> for _ in range(20):
    ...     curr_len = len(mutator.generate())
    ...     if curr_len not in len_list:
    ...         different_count += 1
    ...     len_list.append(curr_len)

    >>> different_count < 10
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
    >>> len(mutator.generate()) * 8
    65536
    >>> mutator = BitArrayMutator(fieldBits.domain, lengthBitSize=UnitSize.SIZE_8)
    >>> len(mutator.generate()) * 8
    256
    >>> mutator = BitArrayMutator(fieldBits.domain, lengthBitSize=UnitSize.SIZE_4)
    >>> len(mutator.generate()) * 8
    16

    """


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a field**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a sub-field**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> f2_1 = Field(BitArray(nbBits=8))
    >>> f2_2 = Field(BitArray(nbBits=8))
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2_1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'\xceA\xca'
    >>> next(messages_gen)
    b'\xceA\xfb'
    >>> next(messages_gen)
    b'\xceA\xb0'


    **Fixing the value of a field that contains sub-fields**

    This should trigger an exception as it is only possible to fix a value to leaf fields.

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> f2_1 = Field(BitArray(nbBits=8))
    >>> f2_2 = Field(BitArray(nbBits=8))
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2] = b'\x41'
    Traceback (most recent call last):
    ...
    Exception: Cannot set a fixed value on a field that contains sub-fields


    **Fixing the value of a leaf variable**

    >>> from netzob.all import *
    >>> v1 = Data(BitArray(nbBits=8))
    >>> v2 = Data(BitArray(nbBits=8))
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A\xde'
    >>> next(messages_gen)
    b'A#'
    >>> next(messages_gen)
    b'A1'


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(BitArray(nbBits=8))
    >>> v2 = Data(BitArray(nbBits=8))
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v_agg] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'


    **Fixing the value of a field, by relying on a provided generator**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> my_generator = (x for x in [b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_generator
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    Traceback (most recent call last):
    ...
    RuntimeError: generator raised StopIteration


    **Fixing the value of a field, by relying on a provided iterator**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> my_iter = iter([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_iter
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    Traceback (most recent call last):
    ...
    RuntimeError: generator raised StopIteration


    **Fixing the value of a field, by relying on a provided function**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8))
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> def my_callable():
    ...     return random.choice([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_callable
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'


    **Fixing the value of a field through its name**

    >>> from netzob.all import *
    >>> f1 = Field(BitArray(nbBits=8), name='f1')
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['f1'] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a variable leaf through its name**

    >>> from netzob.all import *
    >>> v1 = Data(BitArray(nbBits=8), name='v1')
    >>> v2 = Data(BitArray(nbBits=8), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v1'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC\xd1'
    >>> next(messages_gen)
    b'ABC\x8f'
    >>> next(messages_gen)
    b'ABC3'


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(BitArray(nbBits=8), name='v1')
    >>> v2 = Data(BitArray(nbBits=8), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v_agg'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'

    """
