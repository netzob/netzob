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
import inspect
import typing
from itertools import repeat, starmap

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.DomainMutator import DomainMutator, MutatorInterval
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
# from netzob.Fuzzing.Xorshift128plus import Xorshift128plus
from netzob.Model.Vocabulary.Types.Integer import Integer
from randomstate import RandomState
from randomstate.prng import (mt19937, mlfg_1279_861, mrg32k3a, pcg32, pcg64,
                              xorshift128, xoroshiro128plus, xorshift1024,
                              dsfmt)


@NetzobLogger
class PRNGFactory(object):
    """
    the :class:`PRNGFactory` is a factory that creates specific instances of
    :class:`PseudoRandomIntegerMutator`.
    """

    @staticmethod
    def _handleCustomGenerator(generator):
        if isinstance(generator, typing.Iterable):
            return iter(generator)
        elif callable(generator):
            if inspect.isgeneratorfunction(generator):
                return generator()
            else:
                return repeatfunc(generator)
        raise ValueError('{} is not a valid PRNG module.'.format(generator))

    @classmethod
    def buildPRNG(cls, generator, seed):
        """
        Provide a generator using either a name
        (compatible with :class:`randomstate.Randomstate`), an :doc:`iterable`
        object or a :doc:`generator` function with no argument.

        :param generator: the generator key
        :type generator: str, callable or generator function
        """
        if isinstance(generator, str):
            if generator == 'mt19937':
                PRNG = mt19937.RandomState
            elif generator == 'mlfg_1279_861':
                PRNG = mlfg_1279_861.RandomState
            elif generator == 'mrg32k3a':
                PRNG = mrg32k3a.RandomState
            elif generator == 'pcg32':
                PRNG = pcg32.RandomState
            elif generator == 'pcg64':
                PRNG = pcg64.RandomState
            elif generator == 'xorshift128':
                PRNG = xorshift128.RandomState
            elif generator == 'xoroshiro128plus':
                PRNG = xoroshiro128plus.RandomState
            elif generator == 'xorshift1024':
                PRNG = xorshift1024.RandomState
            elif generator == 'dsfmt':
                PRNG = dsfmt.RandomState
            assert issubclass(PRNG, RandomState)
            return repeatfunc(PRNG(seed=seed).random_sample)
        if seed is not None:
            cls._logger.warning("the seed must be configured manually, in "
                                "compliance with the custom generator."
                                .format(cls.__name__))
        return cls._handleCustomGenerator(generator)


class PseudoRandomIntegerMutator(DomainMutator):
    r"""The integer mutator, using pseudo-random generator.

    The PseudoRandomIntegerMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param interval: The scope of values to generate.
        If set to :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`, the values will be generate
        between the min and max values of the domain.
        If set to :attr:`MutatorInterval.FULL_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.FULL_INTERVAL>`, the values will be generate in
        [0, 2^N-1], where N is the bitsize (storage) of the field.
        If it is an tuple of integers (min, max), the values will be generate
        between min and max.
        Default value is :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not implemented).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is :attr:`PRNG_mt19937`.
    :param seed: The seed used in pseudo-random generator
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
    >>> fieldInt = Field(Integer())
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
    b'\xc1'

    This example uses an iterator object with a finite number of values (3),
    resulting in an error as soon as the limit is reached:

    >>> mutator3 = PseudoRandomIntegerMutator(fieldInt.domain, generator=(0., 0.5, 1))
    >>> mutator3.generate()
    b'\x80'
    >>> mutator3.generate()
    b'\x00'
    >>> mutator3.generate()
    b'\x7f'
    >>> mutator3.generate()
    Traceback (most recent call last):
    StopIteration

    Note that, it is simple to make an infinite number generator from a finite
    number of values by using the function :func:`itertools.cycle` of Python:

    >>> from itertools import cycle
    >>> mutator4 = PseudoRandomIntegerMutator(fieldInt.domain, generator=cycle(range(2)))
    >>> mutator4.generate()
    b'\x80'
    >>> mutator4.generate()
    b'\x7f'
    >>> mutator4.generate()
    b'\x80'

    Constant definitions :
    """

    # Types of PRNG in RandomState module
    PRNG_mt19937 = 'mt19937'
    PRNG_mlfg_1279_861 = 'mlfg_1279_861'
    PRNG_mrg32k3a = 'mrg32k3a'
    PRNG_pcg32 = 'pcg32'
    PRNG_pcg64 = 'pcg64'
    PRNG_xorshift128 = 'xorshift128'
    PRNG_xoroshiro128plus = 'xoroshiro128plus'
    PRNG_xorshift1024 = 'xorshift1024'
    PRNG_dsfmt = 'dsfmt'

    def __init__(self,
                 domain,
                 interval=MutatorInterval.DEFAULT_INTERVAL,
                 generator='mt19937',
                 **kwargs):
        # Call parent init
        super().__init__(domain, **kwargs)

        # Sanity checks
        if not isinstance(domain.dataType, Integer):
            raise Exception("Mutator domain dataType should be an Integer, not '{}'".format(type(domain.dataType)))

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
        self._prng = PRNGFactory.buildPRNG(generator, self._seed)
        # self._prng = Xorshift128plus(self.seed)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._prng = PRNGFactory.buildPRNG(self._generatorType, seedValue)

    def reset(self):
        self._prng = PRNGFactory.buildPRNG(self._generatorType, self._seed)
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
        if self.currentCounter < self.counterMax:
            self._currentCounter += 1
            dom_type = self.getDomain().dataType
            return Integer.decode(self.generateInt(),
                                  unitSize=dom_type.unitSize,
                                  endianness=dom_type.endianness,
                                  sign=dom_type.sign)
        else:
            raise Exception("Max mutation counter reached")

    def generateInt(self, interval=None):
        """This is the mutation method of the integer type.
        It uses a PRNG to produce the value between minValue and maxValue.

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
        return center(next(self._prng), self._minValue, self._maxValue)

    def _generateIntWithInterval(self, interval):
        minValue, maxValue = interval
        return center(next(self._prng), minValue, maxValue)


def center(val, lower, upper):
    """
    Center :attr:`val` between :attr:`lower` and :attr:`upper`.
    """
    return int(val * (upper - lower) + lower)


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  ``repeatfunc(random.random)``
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))
