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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import Sign


class TimestampMutator(DomainMutator):
    r"""The Timestamp mutator, using pseudo-random generator.

    The TimestampMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is ``'xorshift'``.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional

    **Internal generator functions**

    The following example shows how to generate a Timestamp value,
    with an arbitrary seed of 4321:

    >>> from netzob.all import *
    >>> fieldTimestamp = Field(Timestamp())
    >>> mutator = TimestampMutator(fieldTimestamp.domain, seed=4321)
    >>> d = mutator.generate()
    >>> d
    b'\x12 #$'
    >>> len(d)
    4

    """

    DATA_TYPE = Timestamp

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Initialize data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed)

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

        # Generate a random integer between 0 and 2**unitsize-1
        timeValue = next(self.generator) * (2**self.domain.dataType.unitSize.value - 1)

        return Integer.decode(timeValue,
                              unitSize=self.domain.dataType.unitSize,
                              endianness=self.domain.dataType.endianness,
                              sign=Sign.UNSIGNED)
