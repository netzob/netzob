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


class RecursionException(Exception):
    pass


class AltMutator(DomainMutator):
    r"""The alternative mutator.

    The AltMutator constructor expects some parameters:

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
    :param maxDepth: This makes it possible to limit the recursive calls to the mutator.
    :type domain: :class:`Variable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type mutateChild: :class:`bool`, optional
    :type mappingTypesMutators: :class:`dict` where keys are :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` and values are tuples (:class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`, mutator parameters, ...), optional
    :type maxDepth: :class:`int`.
    :raises: :class:`Exception` if domain is not valid


    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
    >>> data_subAlt = Alt([Integer(12), String("abc")])
    >>> data_alt = Alt([Integer(34), data_subAlt])
    >>> mutator = AltMutator(data_alt, seed=10)
    >>> mutator.generate()
    0
    >>> mutator.currentDepth
    1
    >>> mutator.generate()
    1
    >>> mutator.currentDepth
    2
    >>> mutator.generate()
    0
    >>> mutator.currentDepth
    3


    **Fuzzing of a field that contains an alternate of variables with default fuzzing strategy (FuzzingMode.GENERATE)**

    >>> f_alt = Field(name="alt", domain=Alt([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_alt)
    >>> next(symbol.specialize(preset))
    b'\x00\x00'


    **Fuzzing of an alternate of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> f_alt = Field(name="alt", domain=Alt([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> mapping = {}
    >>> mapping[Integer] = {'generator':'determinist'}
    >>> preset.fuzz(f_alt, mappingTypesMutators=mapping)
    >>> res = next(symbol.specialize(preset))
    >>> res
    b' \x01'


    **Fuzzing of an alternate of variables without fuzzing the children**

    >>> f_alt = Field(name="alt", domain=Alt([int8(interval=(1, 4)),
    ...                                       int8(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_alt, mutateChild=False)
    >>> res = next(symbol.specialize(preset))
    >>> 1 <= ord(res) <= 4
    True


    **Fuzzing of an alternate of variables with a limitation in term of recursivity**

    >>> inner_domain = Alt([int8(interval=(1, 4)), int8(interval=(5, 8))])
    >>> outer_domain = Alt([int8(interval=(9, 12)), inner_domain])
    >>> f_alt = Field(name="alt", domain=outer_domain)
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_alt, maxDepth=2)
    >>> next(symbol.specialize(preset))
    b'\x00'
    >>> next(symbol.specialize(preset))
    Traceback (most recent call last):
    ...
    netzob.Fuzzing.Mutators.AltMutator.RecursionException: Max depth reached (2)


    **Constant definitions:**
    """

    DEFAULT_MAX_DEPTH = 20

    def __init__(self,
                 domain,
                 mode=FuzzingMode.GENERATE,
                 generator='xorshift',
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=DomainMutator.COUNTER_MAX_DEFAULT,
                 mutateChild=True,
                 mappingTypesMutators={},
                 maxDepth=DEFAULT_MAX_DEPTH):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Variables from parameters
        self.mutateChild = mutateChild
        self.mappingTypesMutators = mappingTypesMutators
        self.maxDepth = maxDepth

        # Internal structure used to determine the position to select at each call to generate()
        self._currentDepth = 0

        if self.mode == FuzzingMode.FIXED:
            self.generator = generator
        else:
            # Configure generator
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed, minValue=0, maxValue=len(self.domain.children) - 1)

    def copy(self):
        r"""Return a copy of the current mutator.

        >>> from netzob.all import *
        >>> d = Alt([uint8(), uint8()])
        >>> m = AltMutator(d).copy()
        >>> m.mode
        FuzzingMode.GENERATE

        """
        copy_mappingTypesMutators = {}
        for k, v in self._mappingTypesMutators.items():
            mutator, mutator_default_parameters = v
            copy_mappingTypesMutators[k] = mutator_default_parameters

        m = AltMutator(self.domain,
                       mode=self.mode,
                       generator=self.generator,
                       seed=self.seed,
                       counterMax=self.counterMax,
                       mutateChild=self.mutateChild,
                       mappingTypesMutators=copy_mappingTypesMutators,
                       maxDepth=self.maxDepth)
        return m

    def count(self, preset=None):
        r"""

        >>> from netzob.all import *
        >>> d = Alt([uint8(), uint8()])
        >>> AltMutator(d).count()
        65536

        """
        if self.mode == FuzzingMode.FIXED:
            count = AbstractType.MAXIMUM_POSSIBLE_VALUES
        else:
            count = 1
            for t in self.domain.children:
                count *= t.count(preset=preset)
        return count

    @property
    def maxDepth(self):
        """
        Property (getter.setter  # type: ignore).
        Recursivity limit in mutating an :class:`Alt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt>` type.
        When this limit is reached in :meth:`generate` method, an exception is
        raised.

        :rtype: :class:`int`
        """
        return self._maxDepth

    @maxDepth.setter  # type: ignore
    @typeCheck(int)
    def maxDepth(self, maxDepthValue):
        self._maxDepth = maxDepthValue

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

    @property
    def currentDepth(self):
        """
        Property (getter).
        Return the current depth in searching a type different of
        :class:`Alt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt>` in :meth:`generate`.

        :type: :class:`int`
        :raises: :class:`RecursionError` if _currentDepth is None
        """
        if self._currentDepth is None:
            raise ValueError("Current depth is None : generate() has to be \
called, first")
        return self._currentDepth

    def generate(self):
        """This is the fuzz generation method of the alternative field.

        It randomly selects the child among the alternative list by using
        :attr:`positionGenerator`.

        If the mutation encounters recursivity (:class:`Alt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt>`
        containing :class:`Alt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt>`),
        infinite loop is avoided by controlling the number of iterations
        **currentDepth** with **maxDepth**.

        If **currentDepth** exceeds **maxDepth**, a RecursionError is raised.

        :return: None
        :rtype: :class:`None`
        :raises: :class:`RecursionError`
        """
        # Call parent generate() method
        if self.mode != FuzzingMode.FIXED:
            super().generate()

        self._currentDepth += 1
        if self._currentDepth >= self.maxDepth:
            raise RecursionException("Max depth reached ({})".format(self.maxDepth))

        return next(self.generator)


def _test_alt_mutator():
    r"""
    # Test if AltMutator generate a pseudo-random type between those defined

    >>> from netzob.all import *

    >>> f_alt = Field(name="alt", domain=Alt([Raw(), int8(), int16()]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_alt)
    >>> have_int8 = False
    >>> have_int16 = False
    >>> have_raw = False
    >>> for _ in range(10):
    ...     tmp = len(next(symbol.specialize(preset)))
    ...     if tmp == 1:
    ...         have_int8 = True
    ...     elif tmp == 2:
    ...         have_int16 = True
    ...     elif tmp > 2:
    ...         have_raw = True
    >>> have_int8
    True
    >>> have_int16
    True
    >>> have_raw
    True

    """


def _test_alt_use_mutator():
    r"""
    # AltMutator can be set to use another mutator's option for mutation

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> mapping = {}
    >>> f_alt = Field(name="alt", domain=Alt([Integer(), Raw()]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> mapping[Integer] = {'lengthBitSize' : UnitSize.SIZE_64}
    >>> preset.fuzz(f_alt, mappingTypesMutators=mapping)
    >>> res = []
    >>> res.append(len(next(symbol.specialize(preset))))
    >>> res.append(len(next(symbol.specialize(preset))))
    >>> 8 in res
    True

    """


def _test_alt_max_depth():
    r"""
    # AltMutator can be set to limit the number of mutations

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> f_alt = Field(name="alt", domain=Alt([Integer(42)]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> preset = Preset(symbol)
    >>> preset.fuzz(f_alt, maxDepth=3, generator='xorshift')
    >>> tmp = next(symbol.specialize(preset))
    >>> tmp = next(symbol.specialize(preset))
    >>> tmp = next(symbol.specialize(preset))
    Traceback (most recent call last):
    ...
    netzob.Fuzzing.Mutators.AltMutator.RecursionException: Max depth reached (3)

    """


def _test_fixed():
    r"""

    Reset the underlying random generator

    >>> from netzob.all import *
    >>> Conf.apply()


    **Fixing the value of a node variable**

    >>> from netzob.all import *
    >>> v1 = Data(Raw(nbBytes=1))
    >>> v2 = Data(Raw(nbBytes=1))
    >>> v_alt = Alt([v1, v2])
    >>> f1 = Field(v_alt)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset[v_alt] = b'\x41\x42\x43'
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
    >>> v_alt = Alt([v1, v2], name='v_alt')
    >>> f1 = Field(v_alt)
    >>> symbol = Symbol([f1], name="sym")
    >>> preset = Preset(symbol)
    >>> preset['v_alt'] = b'\x41\x42\x43'
    >>> messages_gen = symbol.specialize(preset)
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'
    >>> next(messages_gen)
    b'ABC'

    """
