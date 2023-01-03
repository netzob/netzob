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
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import Sign


class TimestampMutator(DomainMutator):
    r"""The Timestamp mutator, using pseudo-random generator.

    The TimestampMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
    :param generator: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is ``'xorshift'``.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional

    **Internal generator functions**

    The following example shows how to generate a Timestamp value,
    with an arbitrary seed of 4321:

    >>> from netzob.all import *
    >>> fieldTimestamp = Field(Timestamp())
    >>> mutator = TimestampMutator(fieldTimestamp.domain, seed=4321)
    >>> mutator.generate()
    b'\x00\x00\x00\x00'
    >>> d = mutator.generate()
    >>> d
    b'A\x9a\x0c\x0f'
    >>> len(d)
    4

    """

    DATA_TYPE = Timestamp

    def __init__(self,
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:

            # Initialize data generator
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=(1 << 32) - 1, signed=False)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> f = Field(Timestamp())
        >>> m = TimestampMutator(f.domain).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        m = TimestampMutator(self.domain,
                             mode=self.mode,
                             generator=self.generator,
                             seed=self.seed,
                             counterMax=self.counterMax)
        return m

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(Timestamp())
        >>> TimestampMutator(f.domain).count()
        4294967296

        >>> f = Field(Timestamp(1444494130))
        >>> TimestampMutator(f.domain).count()
        4294967296

        """

        return (1 << self.domain.dataType.unitSize.value)

    def generate(self):
        """This is the mutation method of the Timestamp type.
        It uses a PRNG to produce the value corresponding to the domain.

        :return: the generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            valueBytes = next(self.generator)
        else:

            # Generate a random integer between 0 and 2**unitsize-1
            timeValue = next(self.generator)

            valueBytes = Integer.decode(timeValue,
                                        unitSize=self.domain.dataType.unitSize,
                                        endianness=self.domain.dataType.endianness,
                                        sign=Sign.UNSIGNED)

        return valueBytes


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a field**

    >>> from netzob.all import *
    >>> f1 = Field(Timestamp())
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
    >>> f1 = Field(Timestamp())
    >>> f2_1 = Field(Timestamp())
    >>> f2_2 = Field(Timestamp())
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2_1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> len(next(messages_gen))
    9
    >>> len(next(messages_gen))
    9
    >>> len(next(messages_gen))
    9


    **Fixing the value of a field that contains sub-fields**

    This should trigger an exception as it is only possible to fix a value to leaf fields.

    >>> from netzob.all import *
    >>> f1 = Field(Timestamp())
    >>> f2_1 = Field(Timestamp())
    >>> f2_2 = Field(Timestamp())
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2] = b'\x41'
    Traceback (most recent call last):
    ...
    Exception: Cannot set a fixed value on a field that contains sub-fields


    **Fixing the value of a leaf variable**

    >>> from netzob.all import *
    >>> v1 = Data(Timestamp())
    >>> v2 = Data(Timestamp())
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> len(next(messages_gen))
    5
    >>> len(next(messages_gen))
    5
    >>> len(next(messages_gen))
    5


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(Timestamp())
    >>> v2 = Data(Timestamp())
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
    >>> f1 = Field(Timestamp())
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
    >>> f1 = Field(Timestamp())
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
    >>> f1 = Field(Timestamp())
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> def my_callable():
    ...     return random.choice([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_callable
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    b'A'
    >>> next(messages_gen)
    b'B'


    **Fixing the value of a field through its name**

    >>> from netzob.all import *
    >>> f1 = Field(Timestamp(), name='f1')
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
    >>> v1 = Data(Timestamp(), name='v1')
    >>> v2 = Data(Timestamp(), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v1'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> len(next(messages_gen))
    7
    >>> len(next(messages_gen))
    7
    >>> len(next(messages_gen))
    7


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(Timestamp(), name='v1')
    >>> v2 = Data(Timestamp(), name='v2')
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
