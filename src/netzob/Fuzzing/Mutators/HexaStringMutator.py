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
from netzob.Fuzzing.Mutator import Mutator, FuzzingMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, FuzzingInterval
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class HexaStringMutator(DomainMutator):
    r"""The HexaString mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The HexaStringMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`,
        :meth:`generate` will be used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
        Default value is UnitSize.SIZE_8.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type lengthBitSize: :class:`int`, optional


    The following example shows how to generate a fuzzed hexastring:

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.HexaStringMutator import HexaStringMutator
    >>> fieldHexa = Field(HexaString(nbBytes=2))
    >>> mutator = HexaStringMutator(fieldHexa.domain)
    >>> len(mutator.generate())
    16
    >>> len(mutator.generate())
    15
    >>> len(mutator.generate())
    14

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.HexaStringMutator import HexaStringMutator
    >>> fieldHexa = Field(HexaString(nbBytes=2))
    >>> mutator = HexaStringMutator(fieldHexa.domain, lengthBitSize=UnitSize.SIZE_8)
    >>> len(mutator.generate())
    256
    >>> len(mutator.generate())
    255

    """

    DATA_TYPE = HexaString

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
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=255)  # 255 in order to cover all values of a byte

            # Initialize length generator
            model_min = int(self.domain.dataType.size[0] / 8)
            model_max = int(self.domain.dataType.size[1] / 8)
            model_unitSize = self.domain.dataType.unitSize
            self._initializeLengthGenerator(generator, interval, (model_min, model_max), model_unitSize)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> f = Field(HexaString())
        >>> m = HexaStringMutator(f.domain).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        m = HexaStringMutator(self.domain,
                              mode=self.mode,
                              generator=self.generator,
                              seed=self.seed,
                              counterMax=self.counterMax,
                              lengthBitSize=self.lengthBitSize)
        return m

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(HexaString())
        >>> HexaStringMutator(f.domain).count()
        86400000000

        >>> f = Field(HexaString(nbBytes=4))
        >>> HexaStringMutator(f.domain).count()
        4294967296

        >>> f = Field(HexaString(nbBytes=1))
        >>> HexaStringMutator(f.domain).count()
        256

        >>> f = Field(HexaString(nbBytes=(1, 3)))
        >>> HexaStringMutator(f.domain).count()
        16843008

        >>> f = Field(HexaString(b"abcd"))
        >>> HexaStringMutator(f.domain).count()
        65536

        """

        if self.mode == FuzzingMode.FIXED:
            count = 1
        else:
            range_min = int(self.domain.dataType.size[0] / 8)
            range_max = int(self.domain.dataType.size[1] / 8)
            permitted_values = 256
            count = 0
            for i in range(range_min, range_max + 1):
                count += permitted_values ** i
                if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                    return AbstractType.MAXIMUM_POSSIBLE_VALUES
        return count

    def generate(self):
        """This is the fuzz generation method of the raw field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: A generated content represented with bytes.
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            valueBytes = next(self.generator)
        else:

            # Generate length of random data
            length = next(self._lengthGenerator)

            valueBytes = bytes()
            if length == 0:
                return valueBytes
            while True:
                valueInt = next(self.generator)
                valueBytes += valueInt.to_bytes(1, byteorder='big')
                if len(valueBytes) >= length:
                    break
            valueBytes = valueBytes[:length]

        return valueBytes


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a field**

    >>> from netzob.all import *
    >>> f1 = Field(HexaString(nbBytes=1))
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
    >>> f1 = Field(HexaString(nbBytes=1))
    >>> f2_1 = Field(HexaString(nbBytes=1))
    >>> f2_2 = Field(HexaString(nbBytes=1))
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
    >>> f1 = Field(HexaString(nbBytes=1))
    >>> f2_1 = Field(HexaString(nbBytes=1))
    >>> f2_2 = Field(HexaString(nbBytes=1))
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2] = b'\x41'
    Traceback (most recent call last):
    ...
    Exception: Cannot set a fixed value on a field that contains sub-fields


    **Fixing the value of a leaf variable**

    >>> from netzob.all import *
    >>> v1 = Data(HexaString(nbBytes=1))
    >>> v2 = Data(HexaString(nbBytes=1))
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
    >>> v1 = Data(HexaString(nbBytes=1))
    >>> v2 = Data(HexaString(nbBytes=1))
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
    >>> f1 = Field(HexaString(nbBytes=1))
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
    StopIteration


    **Fixing the value of a field, by relying on a provided iterator**

    >>> from netzob.all import *
    >>> f1 = Field(HexaString(nbBytes=1))
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
    StopIteration


    **Fixing the value of a field, by relying on a provided function**

    >>> from netzob.all import *
    >>> f1 = Field(HexaString(nbBytes=1))
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
    >>> f1 = Field(HexaString(nbBytes=1), name='f1')
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
    >>> v1 = Data(HexaString(nbBytes=1), name='v1')
    >>> v2 = Data(HexaString(nbBytes=1), name='v2')
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
    >>> v1 = Data(HexaString(nbBytes=1), name='v1')
    >>> v2 = Data(HexaString(nbBytes=1), name='v2')
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
