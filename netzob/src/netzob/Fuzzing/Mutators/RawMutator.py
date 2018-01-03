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
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class RawMutator(DomainMutator):
    r"""The raw mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The RawMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`,
        :meth:`generate` will be used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
        Default value is UnitSize.SIZE_8.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type lengthBitSize: :class:`int`, optional


    The following example shows how to generate a fuzzed raw bytes:

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.RawMutator import RawMutator
    >>> fieldRaw = Field(Raw(nbBytes=2))
    >>> mutator = RawMutator(fieldRaw.domain)
    >>> len(mutator.generate())
    16
    >>> len(mutator.generate())
    15
    >>> len(mutator.generate())
    14

    """

    DATA_TYPE = Raw

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 interval=MutatorInterval.FULL_INTERVAL,
                 lengthBitSize=None):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        # Initialize data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=255)  # 255 in order to cover all values of a byte

        # Initialize length generator
        model_min = int(self.domain.dataType.size[0] / 8)
        model_max = int(self.domain.dataType.size[1] / 8)
        model_unitSize = self.domain.dataType.unitSize
        self._initializeLengthGenerator(generator, interval, (model_min, model_max), model_unitSize)

    def count(self):
        r"""

        >>> from netzob.all import *
        >>> f = Field(Raw())
        >>> RawMutator(f.domain).count()
        86400000000

        >>> f = Field(Raw(nbBytes=4))
        >>> RawMutator(f.domain).count()
        4294967296

        >>> f = Field(Raw(nbBytes=1))
        >>> RawMutator(f.domain).count()
        256

        >>> f = Field(Raw(nbBytes=(1, 3)))
        >>> RawMutator(f.domain).count()
        16843008

        >>> f = Field(Raw(b"abcd"))
        >>> RawMutator(f.domain).count()
        4294967296

        """

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
        super().generate()

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
        return valueBytes[:length]
