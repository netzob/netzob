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
from netzob.Fuzzing.Generators.PseudoRandomIntegerGenerator import PseudoRandomIntegerGenerator


class PseudoRandomIntegerMutator(DomainMutator):
    r"""The integer mutator, using pseudo-random generator.

    The PseudoRandomIntegerMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param interval: The scope of values to generate.
        If set to :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`, the values will be generated
        between the min and max values of the domain.
        If set to :attr:`MutatorInterval.FULL_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.FULL_INTERVAL>`, the values will be generated in
        [0, 2^N-1], where N is the bitsize (storage) of the field.
        If it is a tuple of integers (min, max), the values will be generate
        between min and max.
        Default value is :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is :attr:`PRNG_mt19937`.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type interval: :class:`int` or :class:`tuple`, optional
    :type mode: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional

    **Internal generator functions**

    The following example shows how to generate an 8bits integer in [10, 20]
    interval, with an arbitrary seed of 4321:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8be())
    >>> mutator = PseudoRandomIntegerMutator(fieldInt.domain, interval=(10, 20), seed=4321)
    >>> mutator.generate()
    b'\n'

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
    >>> mutator2 = PseudoRandomIntegerMutator(fieldInt.domain, generator=repeatfunc(random.random))
    >>> mutator2.generate()
    b'@'

    This example uses an iterator object with a finite number of values (3),
    resulting in an error as soon as the limit is reached:

    >>> mutator3 = PseudoRandomIntegerMutator(fieldInt.domain, generator=(0., 0.5, 1.))
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
    >>> mutator4 = PseudoRandomIntegerMutator(fieldInt.domain, generator=cycle(range(2)))
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
                 generator=PseudoRandomIntegerGenerator.PRNG_mt19937,
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

        # Initialize RNG
        self._prng = PseudoRandomIntegerGenerator(seed=self._seed,
                                                  generator=generator)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._prng.updateSeed(seedValue)

    def reset(self):
        self._prng.reset()
        self.resetCurrentCounter()

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

    def generateInt(self, interval=None):
        """This is the mutation method of the integer type.
        It uses a PRNG to produce the value in interval.

        :return: the generated int value
        :rtype: :class:`int`
        :raise: ValueError when the interval format is invalid
        """

        # Generate and return a random value in the interval
        if interval is None:
            return self._generateInt()
        elif (isinstance(interval, tuple) and
              len(interval) == 2 and
              all(isinstance(_, int) for _ in interval)):
            return self._generateIntWithInterval(interval)
        else:
            raise ValueError("Cannot handle interval: {}".format(interval))

    def _generateInt(self):
        return self._prng.getNewValue((self._minValue, self._maxValue))

    def _generateIntWithInterval(self, interval):
        return self._prng.getNewValue(interval)



