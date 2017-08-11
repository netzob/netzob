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
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Fuzzing.Generators.PseudoRandomGenerator import PseudoRandomGenerator
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Model.Vocabulary.Types.AbstractType import Sign


class IntegerMutator(DomainMutator):
    r"""The integer mutator, using pseudo-random or determinist generator

    The IntegerMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param interval: The scope of values to generate.
        If set to :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`, the values will be generated
        between the min and max values of the domain.
        If set to :attr:`MutatorInterval.FULL_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.FULL_INTERVAL>`, the values will be generated in
        [0, 2^N-1], where N is the bitsize (storage) of the field.
        If it is a tuple of integers (min, max), the values will be generate
        between min and max.
        Default value is :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`.
    :param bitsize: The size in bits of the memory on which the generated
        values have to be encoded. Only used with a determinist generator.
        Default value is `None`, which indicates to use the unit size set in the field domain.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use. Set 'determinist' for the determinist generator, else among those
        available in :mod:`randomstate.prng` for a pseudo-random generator.
        Default value is :attr:`PRNG_mt19937`.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type interval: :class:`int` or :class:`tuple`, optional
    :type mode: :class:`int`, optional
    :type bitsize: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional

    **Internal generator functions**

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 4321 and by using the default
    pseudo-random generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8be())
    >>> mutator = IntegerMutator(fieldInt.domain, interval=(10, 20), seed=4321)
    >>> mutator.generate()
    b'\n'

    The following example shows how to generate an 8 bits integer in [-128, +127]
    interval, with an arbitrary seed of 52 and by using the determinist
    generator:

    >>> fieldInt1 = Field(Integer())
    >>> mutator1 = IntegerMutator(fieldInt1.domain, generator='determinist', seed=52)
    >>> mutator1.generate()
    b'\x03'

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> fieldInt1 = Field(uint8be())
    >>> mutator1 = IntegerMutator(fieldInt1.domain, interval=(10, 20), generator='determinist', seed=1234)
    >>> mutator1.generate()
    b'\x11'

    The following example shows how to generate an 8 bits integer in [-10, +5]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> fieldInt1 = Field(Integer(interval=(-10, 5)))
    >>> mutator1 = IntegerMutator(fieldInt1.domain, generator='determinist', seed=42)
    >>> mutator1.generate()
    b'\xfd'

    The following example shows how to generate an 16 bits integer in
    [-32768, +32767] interval, with an arbitrary seed of 1234 and by using the
    determinist generator:

    >>> fieldInt1 = Field(Integer(unitSize=UnitSize.SIZE_16))
    >>> mutator1 = IntegerMutator(fieldInt1.domain, generator='determinist', seed=430)
    >>> mutator1.generate()
    b'\xff\xc1'


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

    >>> import random
    >>> random.seed(4321)
    >>> mutator2 = IntegerMutator(fieldInt.domain, generator=repeatfunc(random.random))
    >>> mutator2.generate()
    b'@'

    This example uses an iterator object with a finite number of values (3),
    resulting in an error as soon as the limit is reached:

    >>> mutator3 = IntegerMutator(fieldInt.domain, generator=(0., 0.5, 1.))
    >>> mutator3.generate()
    b'\x00'
    >>> mutator3.generate()
    b'\x7f'
    >>> mutator3.generate()
    b'\xff'
    >>> mutator3.generate()
    Traceback (most recent call last):
    StopIteration

    Note that, it is simple to make an infinite number generator from a finite
    number of values by using the function :func:`itertools.cycle` of Python:

    >>> from itertools import cycle
    >>> mutator4 = IntegerMutator(fieldInt.domain, generator=cycle(range(2)))
    >>> mutator4.generate()
    b'\x00'
    >>> mutator4.generate()
    b'\xff'
    >>> mutator4.generate()
    b'\x00'

    Constant definitions:
    """

    DATA_TYPE = Integer

    def __init__(self,
                 domain,
                 interval=MutatorInterval.DEFAULT_INTERVAL,
                 bitsize=None,
                 generator=PseudoRandomGenerator.NG_mt19937,
                 **kwargs):
        # Call parent init
        super().__init__(domain, **kwargs)

        # Find min and max potential values for interval
        minValue = 0
        maxValue = 0
        if isinstance(interval, tuple) and len(interval) == 2 and all(isinstance(_, int) for _ in interval):
            # Handle desired interval according to the storage space of the domain dataType
            minValue = max(interval[0], domain.dataType.getMinStorageValue())
            maxValue = min(interval[1], domain.dataType.getMaxStorageValue())
        elif interval == MutatorInterval.DEFAULT_INTERVAL:
            minValue = domain.dataType.getMinValue()
            maxValue = domain.dataType.getMaxValue()
        elif interval == MutatorInterval.FULL_INTERVAL:
            minValue = domain.dataType.getMinStorageValue()
            maxValue = domain.dataType.getMaxStorageValue()
        else:
            raise Exception("Not enough information to generate the mutated data")
        self._minValue = minValue
        self._maxValue = maxValue

        # Initialize the number generator
        if generator == DeterministGenerator.NG_determinist:
            self._ng = DeterministGenerator(seed=self._seed)

            if bitsize is not None:
                if not isinstance(bitsize, int) or bitsize <= 0:
                    raise ValueError("{} is not a valid bitsize value".format(bitsize))
            self._bitsize = bitsize
            if self._bitsize is None:
                self._bitsize = domain.dataType.unitSize.value
            if self._minValue >= 0:
                if self._maxValue > 2**self._bitsize - 1:
                    raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxValue, self._bitsize))
            else:
                if self._maxValue > 2**(self._bitsize - 1) - 1:
                    raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxValue, self._bitsize))
                if self._minValue < -2**(self._bitsize - 1):
                    raise ValueError("The lower bound {} is too small and cannot be encoded on {} bits".format(self._minValue, self._bitsize))

            # Initialize values to generate
            self._ng.createValues(self._minValue,
                                  self._maxValue,
                                  self._bitsize,
                                  domain.dataType.sign == Sign.SIGNED)
        else:
            self._ng = PseudoRandomGenerator(seed=self._seed,
                                                    generator=generator)
            self._ng.setInterval((self._minValue, self._maxValue))

        # forward seed to ng
        self.updateSeed(self._seed)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._ng.updateSeed(seedValue)

    def reset(self):
        self._ng.reset()
        self.resetCurrentCounter()

    def getNbValues(self):
        """Returns the number of values available for the field domain.

        :return: the number of available values
        :rtype: :class:`int`
        """
        if isinstance(self._ng, DeterministGenerator):
            return len(self._ng.values)
        else:
            return 1 + self._maxValue - self._minValue

    def generate(self):
        """This is the mutation method of the integer type.
        It uses a PRNG to produce the value between minValue and maxValue.

        :return: the generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent :meth:`generate` method
        super().generate()

        # Generate and return a random value in the interval
        dom_type = self.getDomain().dataType
        return Integer.decode(self.generateInt(),
                              unitSize=dom_type.unitSize,
                              endianness=dom_type.endianness,
                              sign=dom_type.sign)

    def generateInt(self):
        """This is the mutation method of the integer type.
        It uses a random generator to produce the value in interval.

        :return: the generated int value
        :rtype: :class:`int`
        """
        return self._ng.getNewValue()
