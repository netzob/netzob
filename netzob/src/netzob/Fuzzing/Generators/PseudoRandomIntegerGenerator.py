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
import typing
import inspect
from itertools import repeat, starmap

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from randomstate import RandomState
from randomstate.prng import (mt19937, mlfg_1279_861, mrg32k3a, pcg32, pcg64,
                              xorshift128, xoroshiro128plus, xorshift1024,
                              dsfmt)

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Generator import Generator
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class PRNGFactory(object):
    """
    the :class:`PRNGFactory` is a factory that creates specific instances of
    :class:`PseudoRandomIntegerGenerator`.
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
        (compatible with :class:`randomstate.Randomstate`), an :class:`Iterable
        <typing.Iterable>` object or a :class:`Generator <typing.Generator>`
        function with no argument.

        :param generator: the generator key
        :type generator: str, callable or generator function
        """
        if isinstance(generator, str):
            if generator == PseudoRandomIntegerGenerator.PRNG_mt19937:
                PRNG = mt19937.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_mlfg_1279_861:
                PRNG = mlfg_1279_861.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_mrg32k3a:
                PRNG = mrg32k3a.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_pcg32:
                PRNG = pcg32.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_pcg64:
                PRNG = pcg64.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_xorshift128:
                PRNG = xorshift128.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_xoroshiro128plus:
                PRNG = xoroshiro128plus.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_xoroshiro128plus:
                PRNG = xorshift1024.RandomState
            elif generator == PseudoRandomIntegerGenerator.PRNG_dsfmt:
                PRNG = dsfmt.RandomState
            assert issubclass(PRNG, RandomState)
            return repeatfunc(PRNG(seed=seed).random_sample)
        if seed is not None:
            cls._logger.warning("the seed must be configured manually, in "
                                "compliance with the custom generator."
                                .format(cls.__name__))
        return cls._handleCustomGenerator(generator)


class PseudoRandomIntegerGenerator(Generator):
    """Generates integer values pseudo-randomly.

    >>> from netzob.all import *
    >>> prng = PseudoRandomIntegerGenerator(seed=1342)
    >>> prng.getNewValue(interval=(-3, 4))
    1
    >>> prng.getNewValue(interval=(-3, 4))
    -2
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
                 seed,
                 generator=PRNG_mt19937):
        super().__init__()
        self._generatorType = generator
        self.updateSeed(seed)
        # Initialize RNG
        self._prng = PRNGFactory.buildPRNG(generator, self._seed)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._prng = PRNGFactory.buildPRNG(self._generatorType, seedValue)

    def reset(self):
        self._prng = PRNGFactory.buildPRNG(self._generatorType, self._seed)

    @typeCheck(tuple)
    def getNewValue(self, interval):
        """This is the method to get a new integer value.

        :return: a generated integer value
        :rtype: :class:`integer`
        """
        if len(interval) == 2:
            minValue, maxValue = interval
            return center(next(self._prng), minValue, maxValue)
        raise ValueError("interval does not contain 2 elements")


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
