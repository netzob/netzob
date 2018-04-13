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
        Default value is :const:`False`.
    :param mappingTypesMutators: Override the global default mapping of types with their default
        mutators.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, optional
    :raises: :class:`Exception` if domain is not valid


    **Fuzzing of a field that contains an aggregate of variables with default fuzzing strategy (FuzzingMode.GENERATE)**

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> fuzz.set(f_agg)
    >>> next(symbol.specialize(fuzz=fuzz))
    b'\x00\x00\x00\x00'


    **Fuzzing of an aggregate of variables with non-default fuzzing strategy (FuzzingMode.MUTATE)**

    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([int16(1),
    ...                                       int16(2)]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> fuzz.set(f_agg, mode=FuzzingMode.MUTATE)
    >>> res = next(symbol.specialize(fuzz=fuzz))
    >>> res != b'\x00\x01' and res != b'\x00\x02'
    True


    **Fuzzing of an aggregate of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> fuzz.set(f_agg, mappingTypesMutators=mapping)
    >>> res = next(symbol.specialize(fuzz=fuzz))
    >>> res
    b' \x01 \x01'


    **Fuzzing of an aggregate of variables without fuzzing the children**

    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([int8(interval=(1, 4)),
    ...                                       int8(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> fuzz.set(f_agg, mutateChild=False)
    >>> res = next(symbol.specialize(fuzz=fuzz))
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

        # Initialize data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=1)

    def count(self, fuzz=None):
        r"""

        >>> from netzob.all import *
        >>> d = Agg([uint8(), uint8()])
        >>> AggMutator(d).count()
        65536

        """
        count = 1
        for t in self.domain.children:
            count *= t.count(fuzz=fuzz)
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
        from netzob.Fuzzing.Fuzz import Fuzz
        self._mappingTypesMutators = Fuzz.mappingTypesMutators.copy()
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
        super().generate()
