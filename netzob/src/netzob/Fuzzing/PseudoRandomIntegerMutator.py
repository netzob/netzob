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
from netzob.Fuzzing.DomainMutator import DomainMutator, MutatorInterval
from netzob.Common.Utils.Decorators import typeCheck
# from netzob.Fuzzing.Xorshift128plus import Xorshift128plus
from netzob.Model.Vocabulary.Types.Integer import Integer
from randomstate.prng import (mt19937, mlfg_1279_861, mrg32k3a, pcg32, pcg64,
                              xorshift128, xoroshiro128plus, xorshift1024,
                              dsfmt)


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
    :param generator_type: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is :attr:`PRNG_mt19937`.
    :param seed: The seed used in pseudo-random generator
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type interval: :class:`int` or :class:`tuple`, optional
    :type mode: :class:`int`, optional
    :type generator_type: :class:`str`, optional
    :type seed: :class:`int`, optional

    The following example shows how to generate an 8bits integer in [10, 20]
    interval, with an arbitrary seed of 4321:

    >>> from netzob.all import *
    >>> fieldInt = Field(Integer())
    >>> mutator = PseudoRandomIntegerMutator(domain=fieldInt.domain, interval=(10, 20), seed=4321)
    >>> mutator.generate()
    b'\n'

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
                 generator_type='mt19937',
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
        self.__initializeGenerator(generator_type, self._seed)
        # self._prng = Xorshift128plus(self.seed)

    def __initializeGenerator(self, generator_type, seed):
        self._seed = seed
        if generator_type == 'mt19937':
            self._prng = mt19937.RandomState(seed=self._seed)
        elif generator_type == 'mlfg_1279_861':
            self._prng = mlfg_1279_861.RandomState(seed=self._seed)
        elif generator_type == 'mrg32k3a':
            self._prng = mrg32k3a.RandomState(seed=self._seed)
        elif generator_type == 'pcg32':
            self._prng = pcg32.RandomState(seed=self._seed)
        elif generator_type == 'pcg64':
            self._prng = pcg64.RandomState(seed=self._seed)
        elif generator_type == 'xorshift128':
            self._prng = xorshift128.RandomState(seed=self._seed)
        elif generator_type == 'xoroshiro128plus':
            self._prng = xoroshiro128plus.RandomState(seed=self._seed)
        elif generator_type == 'xorshift1024':
            self._prng = xorshift1024.RandomState(seed=self._seed)
        elif generator_type == 'dsfmt':
            self._prng = dsfmt.RandomState(seed=self._seed)
        else:
            raise ValueError(str(generator_type) +
                             ' is not a valid PRNG module.')
        self._generatorType = generator_type

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self.__initializeGenerator(self._generatorType, seedValue)

    def reset(self):
        self.__initializeGenerator(self._generatorType, self._seed)
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
        """

        # Generate and return a random value in the interval
        if interval is None:
            return int(self._prng.random_sample() *
                       (self._maxValue - self._minValue) +
                       self._minValue)
        elif (isinstance(interval, tuple) and
              len(interval) == 2 and
              all(isinstance(_, int) for _ in interval)):
            minValue, maxValue = interval
            return int(self._prng.random_sample() *
                       (maxValue - minValue) +
                       minValue)
