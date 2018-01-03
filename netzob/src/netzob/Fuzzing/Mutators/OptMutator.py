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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Opt import Opt


class OptMutator(DomainMutator):
    r"""The mutator for an optional variable.

    The OptMutator constructor expects some parameters:

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
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, optional
    :raises: :class:`Exception` if domain is not valid


    >>> from netzob.all import *
    >>> child = Data(dataType=String("abc"))
    >>> fieldOpt = Field(Opt(child))
    >>> mutator = OptMutator(fieldOpt.domain)
    >>> mutator.generate()
    0
    >>> mutator.generate()
    0
    >>> mutator.generate()
    0
    >>> mutator.generate()
    0
    >>> mutator.generate()
    1
    >>> mutator.generate()
    1
    >>> mutator.generate()
    0
    >>> mutator.generate()
    1

    **Constant definitions**:
    """

    # Constants
    DOMAIN_TYPE = Opt

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 mutateChild=True,
                 mappingTypesMutators={}):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=None)

        # Variables from parameters
        self.mutateChild = mutateChild
        self.mappingTypesMutators = mappingTypesMutators

        # Initialize data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=255)  # Arbitrarily maxValue

    def count(self, fuzz=None):
        r"""

        >>> from netzob.all import *
        >>> d = Opt(uint8())
        >>> OptMutator(d).count()
        256

        """

        # Handle count() of children
        count = self.domain.children[0].count(fuzz=fuzz)
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

        # Randomely decide if we create a transition
        if next(self.generator) % 2 == 0:
            return 0
        else:
            return 1
