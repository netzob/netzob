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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode, center
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize


class RepeatMutator(DomainMutator):
    r"""The sequence mutator, using a determinist generator to get a sequence
    length.

    The RepeatMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param mutateChild: If true, sub-field has to be mutated.
        Default value is :const:`False`.
    :param mappingTypesMutators: Override the global default mapping of types with their default
        mutators.
    :param length: The scope of sequence length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, optional
    :raises: :class:`Exception` if domain is not valid


    >>> from netzob.all import *
    >>> child = Data(dataType=String("abc"))
    >>> fieldRepeat = Field(Repeat(child, nbRepeat=3))
    >>> mutator = RepeatMutator(fieldRepeat.domain, interval=MutatorInterval.FULL_INTERVAL)
    >>> mutator.generate()
    256
    >>> mutator.generate()
    255
    >>> mutator.generate()
    254


    **Fuzzing example of a field that contains a fixed number of repeat of a variable**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=2))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep)
    >>> len(symbol.specialize(fuzz=fuzz))
    512


    **Fuzzing example of a field that contains a variable number of repeat of a variable**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep)
    >>> len(symbol.specialize(fuzz=fuzz))
    512
    >>> len(symbol.specialize(fuzz=fuzz))
    510


    **Fuzzing of an alternate of variables with non-default fuzzing strategy (MutatorMode.MUTATE)**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep, mode=MutatorMode.MUTATE)
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res != b'\x00\x01' and res != b'\x00\x02'
    True


    **Fuzzing of a repeat of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> fuzz = Fuzz()
    >>> f_repeat = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> fuzz.set(f_repeat, mappingTypesMutators=mapping)
    >>> len(symbol.specialize(fuzz=fuzz))
    512


    **Fuzzing of a repeat of variables without fuzzing the children**

    >>> fuzz = Fuzz()
    >>> f_repeat = Field(name="rep", domain=Repeat(int8(interval=(5, 8)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> fuzz.set(f_repeat, mutateChild=False)
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> for i in range(int(len(res))):
    ...     assert 5 <= ord(res[i:i+1]) <= 8

    **Constant definitions**:
    """

    # Constants
    DOMAIN_TYPE = Repeat

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 mutateChild=True,
                 mappingTypesMutators={},
                 interval=MutatorInterval.FULL_INTERVAL,
                 lengthBitSize=None):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        # Variables from parameters
        self.mutateChild = mutateChild
        self.mappingTypesMutators = mappingTypesMutators

        # Initialize the length generator
        model_min = self.domain.nbRepeat[0]
        model_max = self.domain.nbRepeat[1]
        model_unitSize = self.domain.UNIT_SIZE
        self._initializeLengthGenerator(interval, (model_min, model_max), model_unitSize)

    @property
    def mutateChild(self):
        """
        Property (getter).
        If true, the sub-field has to be mutated.
        Default value is False.

        :type: :class:`bool`
        """
        return self._mutateChild

    @mutateChild.setter  # type: ignore
    @typeCheck(bool)
    def mutateChild(self, mutateChild):
        self._mutateChild = mutateChild

    @property
    def mappingTypesMutators(self):
        """Return the mapping that set the default mutator for each type.

        :type: :class:`dict`
        """
        return self._mappingTypesMutators

    @mappingTypesMutators.setter  # type: ignore
    @typeCheck(dict)
    def mappingTypesMutators(self, mappingTypesMutators):
        """Override the global default mapping of types with their default
        mutators.
        """
        from netzob.Fuzzing.Fuzz import Fuzz
        self._mappingTypesMutators = Fuzz.mappingTypesMutators.copy()
        for k, v in self._mappingTypesMutators.items():
            if k in mappingTypesMutators.keys():
                mutator, mutator_default_parameters = v
                mutator_default_parameters.update(mappingTypesMutators[k])
                self._mappingTypesMutators[k] = mutator, mutator_default_parameters

    def generate(self):
        """This is the fuzz generation method of the sequence field.

        :return: None
        :rtype: :class:`None`
        """
        # Call parent generate() method
        super().generate()

        # Generate length
        if self._lengthGenerator is not None:
            length = next(self._lengthGenerator)
        else:
            raise Exception("Length generator not initialized")

        return length
