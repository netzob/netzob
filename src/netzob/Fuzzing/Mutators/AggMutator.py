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
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Fuzzing.Mutator import Mutator, FuzzingMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Common.Utils.Decorators import typeCheck

class AggMutator(DomainMutator):
    r"""The aggregate mutator.

    The AggMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`FuzzingMode.GENERATE`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`FuzzingMode.MUTATE <netzob.Fuzzing.DomainMutator.FuzzingMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value.
        Default value is :attr:`FuzzingMode.GENERATE`.
    :param mutateChild: If :const:`True`, the subfield has to be mutated.
        Default value is :const:`True`.
    :param mappingTypesMutators: Override the global default mapping of types with their default
        mutators.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, optional
    :raises: :class:`Exception` if domain is not valid


    **Fuzzing of a field that contains an aggregate of variables with default fuzzing strategy (FuzzingMode.GENERATE)**

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
    >>> f_agg = Field(name="agg", domain=Agg([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_agg)
    >>> next(symbol.specialize(preset))
    b'\x00\x00\x00\x00'


    **Fuzzing of an aggregate of variables with non-default fuzzing strategy (FuzzingMode.MUTATE)**

    >>> f_agg = Field(name="agg", domain=Agg([int16(1),
    ...                                       int16(2)]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_agg, mode=FuzzingMode.MUTATE)
    >>> res = next(symbol.specialize(preset))
    >>> res != b'\x00\x01' and res != b'\x00\x02'
    True


    **Fuzzing of an aggregate of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> f_agg = Field(name="agg", domain=Agg([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> preset = Preset(symbol)
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> preset.fuzz(f_agg, mappingTypesMutators=mapping)
    >>> res = next(symbol.specialize(preset))
    >>> res
    b' \x01 \x01'


    **Fuzzing of an aggregate of variables without fuzzing the children**

    >>> f_agg = Field(name="agg", domain=Agg([int8(interval=(1, 4)),
    ...                                       int8(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_agg, mutateChild=False)
    >>> res = next(symbol.specialize(preset))
    >>> 1 <= res[0] <= 4
    True
    >>> 5 <= res[1] <= 8
    True

    """

    def __init__(self,
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 mutateChild=True,
                 mappingTypesMutators={}):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Variables from parameters
        self.mutateChild = mutateChild
        self.mappingTypesMutators = mappingTypesMutators

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:
            # Configure generator
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=1)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> d = Agg([uint8(), uint8()])
        >>> m = AggMutator(d).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        copy_mappingTypesMutators = {}
        for k, v in self._mappingTypesMutators.items():
            mutator, mutator_default_parameters = v
            copy_mappingTypesMutators[k] = mutator_default_parameters

        m = AggMutator(self.domain,
                       mode=self.mode,
                       generator=self.generator,
                       seed=self.seed,
                       counterMax=self.counterMax,
                       mutateChild=self.mutateChild,
                       mappingTypesMutators=copy_mappingTypesMutators)
        return m

    def count(self, preset=None):
        r"""

        >>> from netzob.all import *
        >>> d = Agg([uint8(), uint8()])
        >>> AggMutator(d).count()
        65536

        """
        if self.mode == FuzzingMode.FIXED:
            count = AbstractType.MAXIMUM_POSSIBLE_VALUES
        else:
            count = 1
            for t in self.domain.children:
                count *= t.count(preset=preset)

        if isinstance(self._effectiveCounterMax, float):
            count = count * self._effectiveCounterMax
        else:
            count = min(count, self._effectiveCounterMax)
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
        """This is the fuzz generation method of the aggregate field.

        :return: None
        :rtype: :class:`None`

        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        if self.mode == FuzzingMode.FIXED:
            value = next(self.generator)
            return value


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(Raw(nbBytes=1))
    >>> v2 = Data(Raw(nbBytes=1))
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


    **Fixing the value of a variable node through its name**

    >>> from netzob.all import *
    >>> v1 = Data(Raw(nbBytes=1), name='v1')
    >>> v2 = Data(Raw(nbBytes=1), name='v2')
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
