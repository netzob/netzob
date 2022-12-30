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
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, FuzzingInterval
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat


class RepeatMutator(DomainMutator):
    r"""The sequence mutator, using a determinist generator to get a sequence
    length.

    The RepeatMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`FuzzingMode.GENERATE <netzob.Fuzzing.DomainMutator.FuzzingMode.GENERATE>`.
    :param mutateChild: If true, sub-field has to be mutated.
        Default value is :const:`True`.
    :param mappingTypesMutators: Override the global default mapping of types with their default
        mutators.
    :param length: The scope of sequence length to generate. If set to
        (min, max), the values will be generated between min and max.
        Default value is **(None, None)**.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type length: :class:`tuple`, optional
    :type lengthBitSize: :class:`int`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, optional
    :raises: :class:`Exception` if domain is not valid


    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.RepeatMutator import RepeatMutator
    >>> child = Data(dataType=String("abc"))
    >>> fieldRepeat = Field(Repeat(child, nbRepeat=3))
    >>> mutator = RepeatMutator(fieldRepeat.domain, interval=FuzzingInterval.FULL_INTERVAL)
    >>> mutator.generate()
    256
    >>> mutator.generate()
    255
    >>> mutator.generate()
    254


    **Fuzzing example of a field that contains a fixed number of repeat of a variable**

    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=2))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_rep)
    >>> gen = symbol.specialize(preset)
    >>> len(next(gen))
    512


    **Fuzzing example of a field that contains a variable number of repeat of a variable**

    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_rep)
    >>> len(next(symbol.specialize(preset)))
    512


    **Fuzzing of an alternate of variables with non-default fuzzing strategy (FuzzingMode.MUTATE)**

    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_rep, mode=FuzzingMode.MUTATE)
    >>> res = next(symbol.specialize(preset))
    >>> res != b'\x00\x01' and res != b'\x00\x02'
    True


    **Fuzzing of a repeat of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> f_repeat = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> preset = Preset(symbol)
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> preset.fuzz(f_repeat, mappingTypesMutators=mapping)
    >>> len(next(symbol.specialize(preset)))
    512


    **Fuzzing of a repeat of variables without fuzzing the children**

    >>> f_repeat = Field(name="rep", domain=Repeat(int8(interval=(5, 8)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_repeat, mutateChild=False)
    >>> res = next(symbol.specialize(preset))
    >>> for i in range(int(len(res))):
    ...     assert 5 <= ord(res[i:i+1]) <= 8

    **Constant definitions**:
    """

    # Constants
    DOMAIN_TYPE = Repeat

    def __init__(self,
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 mutateChild=True,
                 mappingTypesMutators={},
                 interval=FuzzingInterval.FULL_INTERVAL,
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

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:

            # Initialize the length generator
            if isinstance(self.domain.nbRepeat, tuple):
                model_min = self.domain.nbRepeat[0]
                model_max = self.domain.nbRepeat[1]
            elif isinstance(self.domain.nbRepeat, int):
                model_min = self.domain.nbRepeat
                model_max = self.domain.nbRepeat
            else:
                model_min = 0
                model_max = Repeat.MAX_REPEAT

            model_unitSize = self.domain.UNIT_SIZE
            self._initializeLengthGenerator(generator, interval, (model_min, model_max), model_unitSize)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> d = Repeat(uint8(), nbRepeat=3)
        >>> m = RepeatMutator(d).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        copy_mappingTypesMutators = {}
        for k, v in self._mappingTypesMutators.items():
            mutator, mutator_default_parameters = v
            copy_mappingTypesMutators[k] = mutator_default_parameters

        m = RepeatMutator(self.domain,
                          mode=self.mode,
                          generator=self.generator,
                          seed=self.seed,
                          counterMax=self.counterMax,
                          mutateChild=self.mutateChild,
                          mappingTypesMutators=copy_mappingTypesMutators,
                          lengthBitSize=self.lengthBitSize)
        return m

    def count(self, preset=None):
        r"""

        >>> from netzob.all import *
        >>> d = Repeat(uint8(), nbRepeat=3)
        >>> RepeatMutator(d).count()
        16777216

        >>> d = Repeat(uint8(), nbRepeat=(1, 2))
        >>> RepeatMutator(d).count()
        65536

        >>> def cbk(nb_repeat, data, path, child, remaining=None):
        ...     return RepeatResult.STOP_AFTER
        >>> d = Repeat(uint8(), nbRepeat=cbk)
        >>> RepeatMutator(d).count()
        86400000000

        """

        if self.mode == FuzzingMode.FIXED:
            return AbstractType.MAXIMUM_POSSIBLE_VALUES
        else:

            # Handle max repeat
            if isinstance(self.domain.nbRepeat, tuple):
                max_repeat = self.domain.nbRepeat[1]
            elif isinstance(self.domain.nbRepeat, int):
                max_repeat = self.domain.nbRepeat
            else:
                max_repeat = Repeat.MAX_REPEAT

            # Handle count() of children
            count = self.domain.children[0].count(preset=preset)

            # Result
            count = count ** max_repeat
            if count > AbstractType.MAXIMUM_POSSIBLE_VALUES:
                return AbstractType.MAXIMUM_POSSIBLE_VALUES
            else:
                return count

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
        from netzob.Model.Vocabulary.Preset import Preset
        self._mappingTypesMutators = Preset.mappingTypesMutators.copy()
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
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            value = next(self.generator)
        else:

            # Generate length
            if self._lengthGenerator is not None:
                value = next(self._lengthGenerator)
            else:
                raise Exception("Length generator not initialized")

        return value


def _test_fuzz_children_with_specific_mutator():
    r"""

    **Fuzzing of a repeat of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> f_repeat = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> preset = Preset(symbol)
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> preset.fuzz(f_repeat, mappingTypesMutators=mapping)
    >>> len(next(symbol.specialize(preset)))
    512

    """


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(Raw(nbBytes=1))
    >>> v_repeat = Repeat(v1, nbRepeat=3)
    >>> f1 = Field(v_repeat)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v_repeat] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(Raw(nbBytes=1), name='v1')
    >>> v_repeat = Repeat(v1, nbRepeat=3, name='v_repeat')
    >>> f1 = Field(v_repeat)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v_repeat'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'

    """
