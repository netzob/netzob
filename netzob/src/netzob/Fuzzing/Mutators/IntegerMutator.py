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
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import Sign, UnitSize, AbstractType
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Fuzzing.Mutator import Mutator, FuzzingMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, FuzzingInterval
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator


@NetzobLogger
class IntegerMutator(DomainMutator):
    r"""The integer mutator, using pseudo-random or determinist generator

    The IntegerMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param interval: The scope of values to generate.
        If set to :attr:`FuzzingInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.FuzzingInterval.DEFAULT_INTERVAL>`, the values will be generated
        between the min and max values of the domain.
        If set to :attr:`FuzzingInterval.FULL_INTERVAL <netzob.Fuzzing.DomainMutator.FuzzingInterval.FULL_INTERVAL>`, the values will be generated in
        [0, 2^N-1], where N is the bitsize (storage) of the field.
        If it is a tuple of integers (min, max), the values will be generate
        between min and max.
        Default value is :attr:`FuzzingInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.FuzzingInterval.DEFAULT_INTERVAL>`.
    :param lengthBitSize: The storage size in bits of the integer.
        Default value is `None`, which indicates to use the unit size set in the field domain.
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
    :param generator: The name of the generator to use. Set 'determinist' for the determinist generator, else among those
        available in :mod:`randomstate.prng` for a pseudo-random generator.
        Default value is ``'xorshift'``.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type interval: :class:`int` or :class:`tuple`, optional
    :type mode: :class:`int`, optional
    :type lengthBitSize: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional


    **Internal generator functions**

    The following example shows how to generate an 8 bits unsigned
    integer with a default seed and by using the default pseudo-random
    generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big') <= 255
    True

    The following example shows how to generate an 8 bits unsigned
    integer in [10, 20] interval with a default seed and by using the
    default pseudo-random generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain, interval=(10, 20))
    >>> d = mutator.generate()
    >>> 10 <= int.from_bytes(d, byteorder='big') <= 20
    True

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 4321 and by using the default
    pseudo-random generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain, interval=(10, 20))
    >>> d = mutator.generate()
    >>> 10 <= int.from_bytes(d, byteorder='big') <= 20
    True

    The following example shows how to generate an 8 bits integer in [-128, +127]
    interval, with an arbitrary seed of 52 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer())
    >>> mutator = IntegerMutator(fieldInt1.domain, generator='determinist', seed=52)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    32767

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt1.domain, generator='determinist', seed=1234, interval=(10, 20))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    255

    The following example shows how to generate an 8 bits integer in [-10, +5]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer(interval=(-10, 5)))
    >>> mutator = IntegerMutator(fieldInt1.domain, generator='determinist', seed=1234)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    8193

    The following example shows how to generate an 16 bits integer in
    [-32768, +32767] interval, with an arbitrary seed of 1234 and by using the
    determinist generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer(unitSize=UnitSize.SIZE_16))
    >>> mutator = IntegerMutator(fieldInt1.domain, generator='determinist', seed=430)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    32767


    **Custom generators**

    It is also possible to provide a custom :attr:`generator`.

    .. warning::
       Make sure that each value of the generator is a float between 0.0 and 1.0
       (like :func:`random.random`).

    .. note::
       The value returned by the :meth:`generate` method is *not* the float value
       extracted from the internal state, but a 8-bit binary view in :class:`bytes`.

    This example wraps the :func:`random.random` Python generator (providing
    values in the expected set) into a valid generator mechanism:

    >>> from netzob.all import *
    >>> import random
    >>> from itertools import repeat, starmap
    >>> def repeatfunc(func, times=None, *args):
    ...     if times is None:
    ...         return starmap(func, repeat(args))
    ...     return starmap(func, repeat(args, times))
    >>> random.seed(4321)
    >>> mutator = IntegerMutator(fieldInt.domain, generator=repeatfunc(random.random))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    65

    This example uses an iterator object with a finite number of values (3),
    resulting in an error as soon as the limit is reached:

    >>> from netzob.all import *
    >>> mutator = IntegerMutator(fieldInt.domain, generator=(0., 0.5, 1.))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    128
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    255
    >>> d = mutator.generate()
    Traceback (most recent call last):
    ...
    RuntimeError: generator raised StopIteration

    Note that it is simple to make an infinite number generator from a finite
    number of values by using the function :func:`itertools.cycle` of Python:

    >>> from netzob.all import *
    >>> from itertools import cycle
    >>> mutator = IntegerMutator(fieldInt.domain, generator=cycle(range(2)))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    1
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0

    Constant definitions:
    """

    DATA_TYPE = Integer

    def __init__(self,
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 interval=None,
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
            # Configure generator

            # Handle default interval depending on type of generator
            if generator == DeterministGenerator.name or isinstance(generator, DeterministGenerator):
                if interval is None:
                    interval = FuzzingInterval.DEFAULT_INTERVAL
            else:
                if interval is None:
                    interval = FuzzingInterval.FULL_INTERVAL

            # Initialize generator
            self._initializeGenerator(interval)

    def _initializeGenerator(self, interval):

        # Find min and max potential values for the datatype interval
        self._minLength = 0
        self._maxLength = 0
        if isinstance(interval, tuple) and len(interval) == 2 and all(isinstance(_, int) for _ in interval):
            # Handle desired interval according to the storage space of the domain dataType
            self._minLength = max(interval[0], self.domain.dataType.getMinStorageValue())
            self._maxLength = min(interval[1], self.domain.dataType.getMaxStorageValue())
        elif interval == FuzzingInterval.DEFAULT_INTERVAL:
            self._minLength = self.domain.dataType.getMinValue()
            self._maxLength = self.domain.dataType.getMaxValue()
        elif interval == FuzzingInterval.FULL_INTERVAL:
            self._minLength = self.domain.dataType.getMinStorageValue()
            self._maxLength = self.domain.dataType.getMaxStorageValue()
        else:
            raise Exception("Not enough information to generate the mutated data.")

        # Check bitsize
        if self.lengthBitSize is not None:
            if not isinstance(self.lengthBitSize, UnitSize):
                raise ValueError("{} is not a valid bitsize value".format(self.lengthBitSize))
        if self.lengthBitSize is None:
            self.lengthBitSize = self.domain.dataType.unitSize

        # Check minValue and maxValue consistency according to the bitsize value
        if self._minLength >= 0:
            if self._maxLength > (1 << self.lengthBitSize.value) - 1:
                raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxLength, self.lengthBitSize))
        else:
            if self._maxLength > (1 << (self.lengthBitSize.value - 1)) - 1:
                raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxLength, self.lengthBitSize))
            if self._minLength < -(1 << (self.lengthBitSize.value - 1)):
                raise ValueError("The lower bound {} is too small and cannot be encoded on {} bits".format(self._minLength, self.lengthBitSize.value))

        # Build the generator
        self.generator = GeneratorFactory.buildGenerator(self.generator,
                                                         seed=self.seed,
                                                         minValue=self._minLength,
                                                         maxValue=self._maxLength,
                                                         bitsize=self.lengthBitSize.value,
                                                         signed=self.domain.dataType.sign == Sign.SIGNED)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> f = Field(Integer())
        >>> m = IntegerMutator(f.domain).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        m = IntegerMutator(self.domain,
                           mode=self.mode,
                           generator=self.generator,
                           seed=self.seed,
                           counterMax=self.counterMax,
                           lengthBitSize=self.lengthBitSize)
        return m

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(Integer())
        >>> IntegerMutator(f.domain).count()
        65536

        >>> f = Field(Integer(4))
        >>> IntegerMutator(f.domain).count()
        65536

        >>> f = Field(Integer(interval=(1, 10)))
        >>> IntegerMutator(f.domain).count()
        65536

        >>> f = Field(uint8(interval=(1, 10)))
        >>> IntegerMutator(f.domain).count()
        256

        """

        if self.mode == FuzzingMode.FIXED:
            count = 1
        elif isinstance(self.generator, DeterministGenerator):
            count = len(self.generator._values)
        else:
            count = self._maxLength - self._minLength + 1

        if isinstance(self._effectiveCounterMax, float):
            count = count * self._effectiveCounterMax
        else:
            count = min(count, self._effectiveCounterMax)

        return count

    def generate(self):
        """This is the mutation method of the integer type.
        It uses a PRNG to produce the value between minValue and maxValue.

        :return: the generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent :meth:`generate` method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        # Generate and return a random value in the interval
        value = next(self.generator)

        if self.mode != FuzzingMode.FIXED:

            # Handle redefined bitsize
            dom_type = self.domain.dataType
            if self.lengthBitSize is not None:
                dst_bitsize = self.lengthBitSize
            else:
                dst_bitsize = dom_type.unitSize

            value = Integer.decode(value,
                                   unitSize=dst_bitsize,
                                   endianness=dom_type.endianness,
                                   sign=dom_type.sign)
        return value


def _test_endianness():
    r"""

    # Fuzzing of integer takes into account the endianness

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> fieldInt = Field(uint8le())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='little')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='little')
    90
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='little')
    152

    >>> fieldInt = Field(uint8be())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    90

    """


def _test_pseudo_rand_interval():
    r"""

    # Fuzzing of integer follow the interval [0, 2^N - 1]
    # N is the number of bit of the integer

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generator import Generator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator='xorshift')
    >>> generated_values = set()
    >>> generated_values_signed = set()
    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=False))

    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values_signed.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> result = True
    >>> for x in generated_values:
    ...     if x < 0 or x > pow(2, v.getFixedBitSize()) - 1:
    ...         result = False

    >>> result
    True

    >>> result = True
    >>> atleast_one_neg = False
    >>> for x in generated_values_signed:
    ...     if abs(x) < 0 or abs(x) > pow(2, v.getFixedBitSize() - 1):        # for signed interval is [-128, 127] for 8 bit
    ...         result = False
    ...     if x < 0:
    ...         atleast_one_neg = True

    >>> result
    True
    >>> atleast_one_neg
    True

    """


def _test_determinist_generator_1():
    r"""

    # Fuzzing of integer with deterministic generator: ensure that the expected values are generated (P, Q, P-1, Q-1, P+1, Q+1, 0, -1, 1)
    # P is the min value and Q the max value

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8(interval=(10, 20))
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator='determinist')
    >>> generated_values = set()
    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> min_value = v.getMinValue()
    >>> max_value = v.getMaxValue()

    >>> expected_values = set()
    >>> expected_values.add(min_value)
    >>> expected_values.add(max_value)
    >>> expected_values.add(min_value - 1)
    >>> expected_values.add(max_value - 1)
    >>> expected_values.add(min_value + 1)
    >>> expected_values.add(max_value + 1)
    >>> expected_values.add(0)
    >>> expected_values.add(-1)
    >>> expected_values.add(1)
    >>> expected_values
    {0, 1, 9, 10, 11, 19, 20, 21, -1}

    >>> all(x in generated_values for x in expected_values)
    True

    """


def _test_determinist_generator_2():
    r"""

    # Fuzzing of integer with deterministic generator: ensure that the expected values are generated (-2^k, -2^k - 1, -2^k + 1, 2^k, 2^k - 1, 2^k + 1)
    # k belongs to [0, 1, ..., N-2] ; N is the number of bit of the integer

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator='determinist')
    >>> generated_values = set()
    >>> for _ in range(50):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator='determinist')
    >>> generated_values = set()
    >>> for _ in range(50):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> expected_values = set()
    >>> for k in range(v.getFixedBitSize() - 2):
    ...     expected_values.add(pow(-2, k))
    ...     expected_values.add(pow(-2, k) - 1)
    ...     expected_values.add(pow(-2, k) + 1)
    ...     expected_values.add(pow(2, k))
    ...     expected_values.add(pow(2, k) - 1)
    ...     expected_values.add(pow(2, k) + 1)

    >>> all(x in generated_values for x in expected_values)
    True

    """


def _test_coverage():
    r"""

    # Test to verify that the RNG covers all 8 bits values without duplicate values

    >>> from netzob.all import *
    >>> f_data = Field(uint8())
    >>> symbol = Symbol([f_data])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_data, generator='xorshift')
    >>> datas = set()
    >>> for _ in range(symbol.count()):
    ...     datas.add(next(symbol.specialize(preset)))
    >>> len(datas)
    256

    Test to verify that the RNG covers all 16 bits values

    >>> from netzob.all import *
    >>> f_data = Field(uint16())
    >>> symbol = Symbol([f_data])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_data, generator='xorshift')
    >>> datas = set()
    >>> for _ in range(symbol.count()):
    ...     datas.add(next(symbol.specialize(preset)))
    >>> len(datas)
    65536


    # Test to verify that the RNG covers all values in a specific interval

    >>> from netzob.all import *
    >>> f_data = Field(uint8(interval=(10, 20)))
    >>> symbol = Symbol([f_data])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_data, interval=FuzzingInterval.DEFAULT_INTERVAL, generator='xorshift')
    >>> datas = set()
    >>> symbol.count()
    11
    >>> for _ in range(symbol.count()):
    ...     datas.add(next(symbol.specialize(preset)))
    >>> len(datas)
    11

    """


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()

    **Fixing the value of a field**

    >>> from netzob.all import *
    >>> f1 = Field(uint8())
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
    >>> f1 = Field(uint8())
    >>> f2_1 = Field(uint8())
    >>> f2_2 = Field(uint8())
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2_1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'\x10A\xdb'
    >>> next(messages_gen)
    b'\x10A\xf7'
    >>> next(messages_gen)
    b'\x10A\x07'


    **Fixing the value of a field that contains sub-fields**

    This should trigger an exception as it is only possible to fix a value to leaf fields.

    >>> from netzob.all import *
    >>> f1 = Field(uint8())
    >>> f2_1 = Field(uint8())
    >>> f2_2 = Field(uint8())
    >>> f2 = Field([f2_1, f2_2])
    >>> symbol = Symbol([f1, f2], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[f2] = b'\x41'
    Traceback (most recent call last):
    ...
    Exception: Cannot set a fixed value on a field that contains sub-fields


    **Fixing the value of a leaf variable**

    >>> from netzob.all import *
    >>> v1 = Data(uint8())
    >>> v2 = Data(uint8())
    >>> v_agg = Agg([v1, v2])
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v1] = b'\x41'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'Ai'
    >>> next(messages_gen)
    b'A\xec'
    >>> next(messages_gen)
    b'A\xfb'


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(uint8())
    >>> v2 = Data(uint8())
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
    >>> f1 = Field(uint8())
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
    >>> f1 = Field(uint8())
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
    >>> f1 = Field(uint8())
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> def my_callable():
    ...     return random.choice([b'\x41', b'\x42', b'\x43'])
    >>> preset[f1] = my_callable
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'B'
    >>> next(messages_gen)
    b'C'
    >>> next(messages_gen)
    b'A'


    **Fixing the value of a field through its name**

    >>> from netzob.all import *
    >>> f1 = Field(uint8(), name='f1')
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
    >>> v1 = Data(uint8(), name='v1')
    >>> v2 = Data(uint8(), name='v2')
    >>> v_agg = Agg([v1, v2], name='v_agg')
    >>> f1 = Field(v_agg)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v1'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC\x11'
    >>> next(messages_gen)
    b'ABC\xfa'
    >>> next(messages_gen)
    b'ABC\xa7'


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(uint8(), name='v1')
    >>> v2 = Data(uint8(), name='v2')
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
