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
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Types.Integer import uint16le
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data


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
    >>> from netzob.Fuzzing.Mutators.DomainMutator import MutatorMode
    >>> child = Data(dataType=String("abc"), svas=SVAS.PERSISTENT)
    >>> fieldRepeat = Field(Repeat(child, nbRepeat=3))
    >>> mutator = RepeatMutator(fieldRepeat.domain, length=(0, 30), seed=10)
    >>> mutator.generate()
    16
    >>> mutator.generate()
    17
    >>> mutator.generate()
    31


    **Fuzzing example of a field that contains a fixed number of repeat of a variable**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=2))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep, RepeatMutator)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x03\x00\x01\x00\x02\x00\x03\x00\x02\x00\x01\x00\x01\x00\x03\x00\x01\x00\x01\x00\x03\x00\x03\x00\x01\x00\x02\x00\x03'


    **Fuzzing example of a field that contains a variable number of repeat of a variable**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep, RepeatMutator)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x03\x00\x01\x00\x02\x00\x03\x00\x02\x00\x01\x00\x01\x00\x03\x00\x01\x00\x01\x00\x03\x00\x03\x00\x01\x00\x02\x00\x03'
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x02\x00\x03\x00\x01\x00\x03\x00\x03\x00\x02\x00\x01\x00\x02\x00\x03\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x03'


    **Fuzzing of an alternate of variables with non-default fuzzing strategy (MutatorMode.MUTATE)**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep, RepeatMutator, mode=MutatorMode.MUTATE)
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res != b'\x00\x01' and res != b'\x00\x02'
    True


    **Fuzzing of a repeat of variables with non-default types/mutators mapping (determinist IntegerMutator instead of pseudo-random IntegerMutator for Integer)**

    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
    >>> fuzz = Fuzz()
    >>> f_repeat = Field(name="rep", domain=Repeat(int16(interval=(1, 4)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> mapping = {}
    >>> mapping[Integer] = IntegerMutator, generator='determinist'
    >>> fuzz.set(f_repeat, RepeatMutator, mappingTypesMutators=mapping)
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res
    b'\xfc\x00\xfc\x01\xfd\xff\xfe\x00\xfe\x01\xfe\xff\xff\x00\xff\x01\xff\x7f\xff\x80\xff\x81\xff\xbf\xff\xc0\xff\xc1\xff\xdf'


    **Fuzzing of a repeat of variables without fuzzing the children**

    >>> fuzz = Fuzz()
    >>> f_repeat = Field(name="rep", domain=Repeat(int8(interval=(5, 8)), nbRepeat=(2, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_repeat])
    >>> fuzz.set(f_repeat, RepeatMutator, mutateChild=False)
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> for i in range(int(len(res))):
    ...     assert 5 <= ord(res[i:i+1]) <= 8

    **Constant definitions**:
    """

    # Constants
    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 10
    DOMAIN_TYPE = Repeat

    def __init__(self,
                 domain,
                 mutateChild=True,
                 mappingTypesMutators={},
                 length=(None, None),
                 lengthBitSize=None,
                 **kwargs):
        # Call parent init
        super().__init__(domain, **kwargs)

        if isinstance(length, tuple) and len(length) == 2:
            if all(isinstance(_, int) for _ in length):
                self._minLength, self._maxLength = length
            else:
                self._minLength, self._maxLength = (0, 0)
        if isinstance(domain.nbRepeat, tuple):
            # Handle desired length according to the domain information
            self._minLength = max(self._minLength, int(domain.nbRepeat[0]))
            self._maxLength = min(self._maxLength, int(domain.nbRepeat[1]))
        if self._minLength is None or self._maxLength is None:
            self._minLength = self.DEFAULT_MIN_LENGTH
            self._maxLength = self.DEFAULT_MAX_LENGTH

        self._mutateChild = mutateChild
        self.mappingTypesMutators = mappingTypesMutators

        domain_length_repeat = Data(uint16le())
        self._lengthMutator = IntegerMutator(
            domain=domain_length_repeat,
            interval=(self._minLength, self._maxLength),
            generator='determinist',
            bitsize=lengthBitSize,
            **kwargs)

    @typeCheck(int)
    def updateSeed(self, seedValue):
        super().updateSeed(seedValue)
        self._lengthMutator.updateSeed(seedValue)

    @property
    def mutateChild(self):
        """
        Property (getter).
        If true, the sub-field has to be mutated.
        Default value is False.

        :type: :class:`bool`
        """
        return self._mutateChild

    @mutateChild.setter
    @typeCheck(bool)
    def mutateChild(self, mutateChild):
        self._mutateChild = mutateChild

    @property
    def mappingTypesMutators(self):
        """Return the mapping that set the default mutator for each type.

        :type: :class:`dict`
        """
        return self._mappingTypesMutators

    @mappingTypesMutators.setter
    @typeCheck(dict)
    def mappingTypesMutators(self, mappingTypesMutators):
        """Override the global default mapping of types with their default
        mutators.
        """
        from netzob.Fuzzing.Fuzz import Fuzz
        self._mappingTypesMutators = Fuzz.mappingTypesMutators.copy()
        self._mappingTypesMutators.update(mappingTypesMutators)

    def generate(self):
        """This is the fuzz generation method of the sequence field.
        It generates a sequence length by using lengthMutator.

        :return: None
        :rtype: :class:`None`
        """
        # Call parent generate() method
        super().generate()

        return self._lengthMutator.generateInt()

    def mutate(self, data):
        """Not implemented yet."""
        raise NotImplementedError
