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
import inspect
from typing import Dict, Union  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType  # noqa: F401
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
from netzob.Fuzzing.AlternativeMutator import AlternativeMutator  # noqa: F401
from netzob.Fuzzing.DomainMutator import DomainMutator, MutatorMode  # noqa: F401
from netzob.Fuzzing.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator
from netzob.Fuzzing.StringMutator import StringMutator


class Fuzz(object):
    r"""The Fuzz class is the entry point for the fuzzing component.

    We can apply fuzzing on symbols, fields, variables and types
    through the :meth:`set <.Fuzz.set>` method.

    By default, types have an associated mutator (e.g. :class:`String
    <netzob.Model.Vocabulary.Types.String.String>` type is associated
    by default to the :class:`StringMutator
    <netzob.Model.Fuzzing.StringMutator.StringMutator>`).
    The :meth:`set <.Fuzz.set>` method changes the default behavior.

    The following examples show the different usages of the fuzzing
    component.

    **Fuzzing example of a field that contains an integer**

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=Integer(interval=(1, 4), unitSize=UnitSize.SIZE_16))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'\x00\x02'


    **Fuzzing example of a field that contains an aggregate of variables**

    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([Integer(interval=(1, 4), unitSize=UnitSize.SIZE_16),
    ...                                       Integer(interval=(5, 8), unitSize=UnitSize.SIZE_16)]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> fuzz.set(f_agg, PseudoRandomIntegerMutator, interval=(20, 32000)) # doctest: +SKIP
    >>> symbol.specialize(fuzz=fuzz) # doctest: +SKIP
    b'\x02\x84\x04\xf5'


    **Fuzzing example of a field that contains an alternate of variables**

    >>> fuzz = Fuzz()
    >>> f_alt = Field(name="alt", domain=Alt([Integer(interval=(1, 4), unitSize=UnitSize.SIZE_16),
    ...                                           Integer(interval=(5, 8), unitSize=UnitSize.SIZE_16)]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> fuzz.set(f_alt, PseudoRandomIntegerMutator, interval=(20, 32000)) # doctest: +SKIP
    >>> res = symbol.specialize(fuzz=fuzz) # doctest: +SKIP
    >>> res == b'\x02\x84' or res == b'\x04\xf5' # doctest: +SKIP
    True


    **Fuzzing example of a field that contains a repeat of a variable**

    >>> fuzz = Fuzz()
    >>> f_rep = Field(name="rep", domain=Repeat(Integer(interval=(1, 4), unitSize=UnitSize.SIZE_16),
    ...                                             2))
    >>> symbol = Symbol(name="sym", fields=[f_rep])
    >>> fuzz.set(f_rep, PseudoRandomIntegerMutator, interval=(20, 32000)) # doctest: +SKIP
    >>> symbol.specialize(fuzz=fuzz) # doctest: +SKIP
    b'\x02\x84\x04\xf5'


    **Fuzzing example of a field that contains a size relationship with another field**

    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=Integer(3, unitSize=UnitSize.SIZE_16))
    >>> f_size = Field(name="size", domain=Size([f_data], Integer(unitSize=UnitSize.SIZE_16)))
    >>> symbol = Symbol(name="sym", fields=[f_data, f_size])
    >>> fuzz.set(f_size, PseudoRandomIntegerMutator, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x03\x00\x02'


    **Fuzzing example in mutation mode of a field that contains an integer**

    >>> from netzob.Fuzzing.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator
    >>> from netzob.Fuzzing.DomainMutator import MutatorMode
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=Integer(2, unitSize=UnitSize.SIZE_16))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, mode=MutatorMode.MUTATE, interval=(20, 32000))
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res != b'\x00\x02'  # doctest: +SKIP
    True

    **Multiple fuzzing call on the same symbol**

    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=Integer(2, unitSize=UnitSize.SIZE_16))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, interval=(20, 30000))
    >>> nbFuzz = 1000
    >>> result = set()
    >>> for i in range(nbFuzz):
    ...     result.add(symbol.specialize(fuzz=fuzz))
    >>> assert len(result) == 980  # doctest: +SKIP

    **Fuzzing of a whole symbol, and covering all fields storage spaces**

    >>> from netzob.Fuzzing.DomainMutator import MutatorInterval
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=Integer(interval=(2, 4)))
    >>> f_data2 = Field(name="data2", domain=Integer(interval=(5, 8)))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'\x85\x85'


    **Fuzzing of a whole symbol except one field, and covering all fields storage spaces**

    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=Integer(2))
    >>> f_data2 = Field(name="data2", domain=Integer(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> fuzz.set(f_data2, MutatorMode.NONE)
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'\x85\x04'


    **Fuzzing of a field with default mutator, and covering field storage space**

    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=Integer(2))
    >>> f_data2 = Field(name="data2", domain=Integer(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(f_data2, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'\x02\x85'


    **Fuzzing and changing the default Mutator for types**

    >>> from netzob.Fuzzing.DeterministIntegerMutator import DeterministIntegerMutator
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=Integer(2))
    >>> f_data2 = Field(name="data2", domain=Integer(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(Integer, DeterministIntegerMutator)
    >>> fuzz.set(f_data2, MutatorMode.GENERATE)
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'\x02\xdf'


    **Fuzzing example with counter limiting**

    >>> fuzz = Fuzz(counterMax=1, counterMaxRelative=False)
    >>> f_data = Field(name="data", domain=Alt([String("aaa"), String("bbb")]))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, AlternativeMutator)
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    b'bbb'
    >>> symbol.specialize(fuzz=fuzz)  # doctest: +SKIP
    Traceback (most recent call last):
    Exception: Max mutation counter reached

    """

    mappingTypesMutators = {}   # type: Dict[AbstractType, DomainMutator]
    mappingFieldsMutators = {}  # type: Dict[Field, DomainMutator]

    # Initialize mapping of types with their mutators
    @staticmethod
    def initializeMappings():
        Fuzz.mappingFieldsMutators = {}
        Fuzz.mappingTypesMutators = {}
        Fuzz.mappingTypesMutators[Integer] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[String] = StringMutator
        Fuzz.mappingTypesMutators[HexaString] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[Raw] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[BitArray] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[IPv4] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[Timestamp] = PseudoRandomIntegerMutator

    def __init__(self,
                 counterMax=None,           # type: Union[int, float]
                 counterMaxRelative=False   # type: bool
                 ):
        Fuzz.initializeMappings()
        self._counterMax = counterMax
        self._counterMaxRelative = counterMaxRelative
        self.mappingTypesMutators = Fuzz.mappingTypesMutators
        self.mappingFieldsMutators = Fuzz.mappingFieldsMutators

    def set(self, key, value, **kwargs):
        r"""The method :meth:`set <.Fuzz.set>` specifies the fuzzing
        strategy for a symbol, a field, a variable or a type.

        The :meth:`set <.Fuzz.set>` method expects some parameters:

        :param key: the targeted object (either a symbol, a field, a
                    variable or a type).
        :param value: the fuzzing strategy (see below for available
                      strategies).
        :param kwargs: some context dependent parameters.
        :type key: :class:`AbstractField
                   <netzob.Model.Vocabulary.AbstractField.AbstractField>`,
                   or :class:`AbstractVariable
                   <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`,
                   or :class:`AbstractType
                   <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`

        The fuzzing strategy is defined by a fuzzing mode and a
        mutator. The fuzzing mode can be:

        * ``MutatorMode.MUTATE``: in this mode, the specialization process generates a legitimate message from a symbol, then some mutations are applied on it.
        * ``MutatorMode.GENERATE``: in this mode, the fuzzing component directly produces a random message.

        By default, the ``MutatorMode.GENERATE`` mode is used.

        It is also possible to define a specific mutator for the
        targeted object. The default mutator depends on the data type
        of the fuzzed field. It is possible to specify a different
        behavior for a mutator by passing parameters in ``kwargs``.

        """

        if isinstance(key, type):
            # kwargs are useless here
            self.mappingTypesMutators[key] = value
        elif isinstance(key, AbstractField):
            self.mappingFieldsMutators[key] = (value, kwargs)
            self._normalize_mappingFieldsMutators()
        else:
            raise TypeError("Unsupported type for key: '{}'".format(type(key)))

    def get(self, key):
        if isinstance(key, type):
            # We return the associated mutator class
            if key in self.mappingTypesMutators:
                return self.mappingTypesMutators[key][0]
            else:
                return None
        elif isinstance(key, AbstractField) or isinstance(key, str):
            # We return the associated mutator instance
            if key in self.mappingFieldsMutators:
                return self.mappingFieldsMutators[key][0]
            else:
                return None
        else:
            raise TypeError("Unsupported type for key: '{}'".format(type(key)))

    @staticmethod
    def defaultMutator(domain, **kwargs):
        """Instanciate and return the default mutator according to the
        provided domain.

        """

        # Retrieve the default mutator for the domain dataType
        mutator = None
        if type(getattr(domain, 'dataType', None)) in Fuzz.mappingTypesMutators:
            mutator = Fuzz.mappingTypesMutators[type(domain.dataType)]
        else:
            raise Exception("The domain '{}' has no configured dataType. Cannot find a default Mutator without information regarding the domain type.")

        # Instanciate the mutator
        mutatorInstance = mutator(domain, **kwargs)

        return mutatorInstance

    def _normalize_mappingFieldsMutators(self):
        """Normalize the fuzz structure.

        Fields described with field name are converted into field
        object.

        """

        # Normalize fuzzing keys
        new_keys = {}
        keys_to_remove = []
        for k, v in self.mappingFieldsMutators.items():

            # Handle case where k is a Field -> nothing to do
            if isinstance(k, Field):
                pass
            # Handle case where k is a Symbol -> we retrieve all its sub-fields
            elif isinstance(k, Symbol):
                subfields = k.getLeafFields(includePseudoFields=True)
                keys_to_remove.append(k)
                for f in subfields:
                    # We check if the field is not already present in the fields to mutate
                    if f not in self.mappingFieldsMutators.keys():
                        new_keys[f] = v
            else:
                raise Exception("Fuzz's keys must be a Symbol or a "
                                "Field, but not a '{}'".format(type(k)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
        self.mappingFieldsMutators.update(new_keys)

        # Normalize fuzzing values
        keys_to_remove = []
        from netzob.Fuzzing.Mutator import Mutator
        for k, v in self.mappingFieldsMutators.items():
            if not isinstance(v, tuple):
                raise TypeError("Value should be a tuple. Got: '{}'".format(v))
            (v_m, v_kwargs) = v
            if inspect.isclass(v_m) and issubclass(v_m, Mutator):
                # We instanciate the mutator
                v_m_instance = v_m(domain=k.domain, **v_kwargs)
                v_m_instance.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                # We replace the mutator class by the mutate instance in the main dict
                self.set(k, v_m_instance)
            elif isinstance(v_m, Mutator):
                pass
            elif v_m == MutatorMode.NONE:
                keys_to_remove.append(k)
            elif v_m in [MutatorMode.GENERATE, MutatorMode.MUTATE]:
                mut_inst = Fuzz.defaultMutator(k.domain, **v_kwargs)
                mut_inst.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                mut_inst.mode = v_m
                self.set(k, mut_inst)
            else:
                raise Exception("Fuzz's value '{} (type: {})' must be a "
                                "Mutator instance or Mutator.(GENERATE|MUTATE"
                                "|NONE)".format(v, type(v)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
