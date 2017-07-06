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
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
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
from netzob.Fuzzing.Mutators.AltMutator import AltMutator  # noqa: F401
from netzob.Fuzzing.Mutators.RepeatMutator import RepeatMutator  # noqa: F401
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorMode  # noqa: F401
from netzob.Fuzzing.Mutators.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator
from netzob.Fuzzing.Mutators.StringMutator import StringMutator
from netzob.Fuzzing.Mutators.TimestampMutator import TimestampMutator
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class Fuzz(object):
    r"""The Fuzz class is the entry point for the fuzzing component.

    We can apply fuzzing on symbols, fields, variables and types
    through the :meth:`set <.Fuzz.set>` method.

    By default, types have an associated mutator (e.g. :class:`String
    <netzob.Model.Vocabulary.Types.String.String>` type is associated
    by default to the :class:`StringMutator
    <netzob.Model.Fuzzing.StringMutator.StringMutator>`).
    The :meth:`set <.Fuzz.set>` method changes the default behavior.

    The Fuzz constructor expects some parameters:

    :param counterMax: the max number of values that the mutator would produce. See definition of Mutator.counterMax.
    :param counterMaxRelative: whether the counter value is absolute (``False``) or relative (``True``). See definition of Mutator.counterMaxRelative.

    The following examples show the different usages of the fuzzing
    component.

    **Fuzzing example of a field that contains an integer**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(interval=(1, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)
    b'`n'


    **Fuzzing example of a field that contains an aggregate of variables**

    >>> fuzz = Fuzz()
    >>> f_agg = Field(name="agg", domain=Agg([int16(interval=(1, 4)),
    ...                                       int16(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_agg])
    >>> fuzz.set(f_agg, PseudoRandomIntegerMutator, interval=(20, 32000)) # doctest: +SKIP
    >>> symbol.specialize(fuzz=fuzz) # doctest: +SKIP
    b'\x02\x84\x04\xf5'


    **Fuzzing example of a field that contains a size relationship with another field**

    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(3))
    >>> f_size = Field(name="size", domain=Size([f_data], Integer(unitSize=UnitSize.SIZE_16)))
    >>> symbol = Symbol(name="sym", fields=[f_data, f_size])
    >>> fuzz.set(f_size, PseudoRandomIntegerMutator, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x03`n'


    **Fuzzing example in mutation mode of a field that contains an integer**

    >>> from netzob.Fuzzing.Mutators.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator
    >>> from netzob.Fuzzing.Mutators.DomainMutator import MutatorMode
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(2))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, mode=MutatorMode.MUTATE, interval=(20, 32000))
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res != b'\x00\x02'
    True


    **Multiple fuzzing call on the same symbol**

    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(2))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, PseudoRandomIntegerMutator, interval=(20, 30000))
    >>> nbFuzz = 1000
    >>> result = set()
    >>> for i in range(nbFuzz):
    ...     result.add(symbol.specialize(fuzz=fuzz))
    >>> len(result) == 980
    True


    **Fuzzing of a whole symbol, and covering all fields storage spaces with default mutator per types**

    >>> from netzob.Fuzzing.Mutators.DomainMutator import MutatorInterval
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(interval=(2, 4)))
    >>> f_data2 = Field(name="data2", domain=int8(interval=(5, 8)))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)
    b'DD'


    **Fuzzing of a whole symbol except one field, and covering all fields storage spaces**

    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> fuzz.set(f_data2, MutatorMode.NONE)
    >>> symbol.specialize(fuzz=fuzz)
    b'D\x04'


    **Fuzzing of a field with default mutator, and covering field storage space**

    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(f_data2, MutatorMode.GENERATE, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x02D'


    **Fuzzing and changing the default Mutator for types**

    >>> from netzob.Fuzzing.Mutators.DeterministIntegerMutator import DeterministIntegerMutator
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(Integer, DeterministIntegerMutator)
    >>> fuzz.set(f_data2, MutatorMode.GENERATE)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x02\xfc'


    **Fuzzing configuration with a maximum number of mutations**

    >>> fuzz = Fuzz(counterMax=1, counterMaxRelative=False)
    >>> f_alt = Field(name="alt", domain=Alt([int8(interval=(1, 4)),
    ...                                       int8(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> fuzz.set(f_alt, AltMutator)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x07'
    >>> symbol.specialize(fuzz=fuzz)
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
        Fuzz.mappingTypesMutators[Timestamp] = TimestampMutator

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
            for t in self.mappingTypesMutators:
                if type(key) == t:
                    self.mappingTypesMutators[t] = value
                    break
                elif issubclass(key, t):  # For cases where partial() is used (e.g. on Integer types)
                    self.mappingTypesMutators[t] = value
                    break
            else:
                raise TypeError("Unsupported type for key: '{}'".format(type(key)))
        elif isinstance(key, (AbstractField, AbstractVariable)):
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
        elif isinstance(key, (AbstractField, AbstractVariable)) or isinstance(key, str):
            # We return the associated mutator instance
            if key in self.mappingFieldsMutators:
                return self.mappingFieldsMutators[key][0]
            else:
                return None
        else:
            raise TypeError("Unsupported type for key: '{}'".format(type(key)))

    @staticmethod
    def _retrieveDefaultMutator(domain, mapping, **kwargs):
        """Instanciate and return the default mutator according to the
        provided domain.

        """

        # Retrieve the domain mutator if the domain is complex (such as Repeat, Agg or Alt)
        if isinstance(domain, AbstractVariableNode):
            if isinstance(domain, Repeat):
                mutator = RepeatMutator
            elif isinstance(domain, Alt):
                mutator = AltMutator
            # elif isinstance(domain, Agg):
            #     mutator = AggregateMutator

        # Else, retrieve the default mutator for the domain dataType
        else:
            mutator = None
            for t in mapping:
                # Two type checks are made here, in order to handle cases where partial() is used (e.g. on Integer types)
                if type(getattr(domain, 'dataType', None)) == t or isinstance(getattr(domain, 'dataType', None), t):
                    mutator = mapping[t]
                    break
            else:
                raise Exception("Cannot find a default Mutator for the domain '{}'.".format(domain))

        # Instanciate the mutator
        mutatorInstance = mutator(domain, **kwargs)

        return mutatorInstance

    def _normalize_mappingFieldsMutators(self):
        """Normalize the fuzzing configuration.

        Fields described with field name are converted into field
        object, and then all key elements are converted into
        variables.

        """

        # Normalize fuzzing keys
        self._normalizeKeys()

        # Normalize fuzzing values
        self._normalizeValues()

        # Second loop, to handle cases where domains are complex (Alt, Agg or Repeat)
        new_keys = {}
        for k, v in self.mappingFieldsMutators.items():
            new_keys[k] = v
            if isinstance(k, AbstractVariableNode):
                if not isinstance(v, tuple):
                    raise TypeError("Value should be a tuple. Got: '{}'".format(v))
                (v_m, v_kwargs) = v
                new_keys.update(self._propagateMutation(k, v_m))
        self.mappingFieldsMutators.update(new_keys)

        # Second loop to normalize fuzzing values, after handling complex domains (that may have added news keys:values)
        self._normalizeValues()

    def _normalizeKeys(self, ):
        # Normalize fuzzing keys
        new_keys = {}
        keys_to_remove = []
        for k, v in self.mappingFieldsMutators.items():

            # Handle case where k is a Variable -> nothing to do
            if isinstance(k, AbstractVariable):
                pass
            # Handle case where k is a Field -> retrieve the associated variable
            elif isinstance(k, Field):
                keys_to_remove.append(k)
                new_keys[k.domain] = v
            # Handle case where k is a Symbol -> we retrieve all its field variables
            elif isinstance(k, Symbol):
                subfields = k.getLeafFields(includePseudoFields=True)
                keys_to_remove.append(k)
                for f in subfields:
                    # We check if the variable is not already present in the variables to mutate
                    if f.domain not in self.mappingFieldsMutators.keys():
                        new_keys[f.domain] = v
            else:
                raise Exception("Fuzzing keys must contain Symbols, Fields or Variables"
                                ", but not a '{}'".format(type(k)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
        self.mappingFieldsMutators.update(new_keys)

    def _normalizeValues(self, ):
        # Normalize fuzzing values
        keys_to_update = {}
        keys_to_remove = []

        from netzob.Fuzzing.Mutator import Mutator
        for k, v in self.mappingFieldsMutators.items():
            if not isinstance(v, tuple):
                raise TypeError("Value should be a tuple. Got: '{}'".format(v))
            (v_m, v_kwargs) = v
            if inspect.isclass(v_m) and issubclass(v_m, Mutator):
                # We instanciate the mutator
                v_m_instance = v_m(domain=k, **v_kwargs)
                v_m_instance.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                # We replace the mutator class by the mutate instance in the main dict
                keys_to_update[k] = (v_m_instance, {})
            elif isinstance(v_m, Mutator):
                pass
            elif v_m == MutatorMode.NONE:
                keys_to_remove.append(k)
            elif v_m in [MutatorMode.GENERATE, MutatorMode.MUTATE]:
                mut_inst = Fuzz._retrieveDefaultMutator(domain=k, mapping=Fuzz.mappingTypesMutators, **v_kwargs)
                mut_inst.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                mut_inst.mode = v_m
                keys_to_update[k] = (mut_inst, {})
            else:
                raise Exception("Fuzz's value '{} (type: {})' must be a "
                                "Mutator instance or Mutator.(GENERATE|MUTATE"
                                "|NONE)".format(v, type(v)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
        self.mappingFieldsMutators.update(keys_to_update)

    def _propagateMutation(self, variable, mutator):
        """This method aims at propagating the fuzzing to the children of a
        complex variable (such as Repeat, Alt or Agg). The propagation
        strategy is included in the mutator associated to the parent
        variable.
        """

        tmp_new_keys = {}

        if isinstance(variable, Repeat) and isinstance(mutator, RepeatMutator) and mutator.mutateChild:
            # We check if the variable is not already present in the variables to mutate
            if variable.children[0] not in self.mappingFieldsMutators.keys():
                mut_inst = Fuzz._retrieveDefaultMutator(domain=variable.children[0], mapping=mutator.mappingTypesMutators)
                mut_inst.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                mut_inst.mode = mutator.mode
                tmp_new_keys[variable.children[0]] = (mut_inst, {})

                # Propagate mutation to the child if it is a complex domain
                if isinstance(variable.children[0], AbstractVariableNode):
                    tmp_new_keys.update(self._propagateMutation(variable.children[0], mut_inst))
        elif isinstance(variable, Alt) and isinstance(mutator, AltMutator) and mutator.mutateChild:
            for child in variable.children:
                if child not in self.mappingFieldsMutators.keys():
                    mut_inst = Fuzz._retrieveDefaultMutator(domain=child, mapping=mutator.mappingTypesMutators)
                    mut_inst.setCounterMax(self._counterMax, relative=self._counterMaxRelative)
                    mut_inst.mode = mutator.mode
                    tmp_new_keys[child] = (mut_inst, {})

                    # Propagate mutation to the child if it is a complex domain
                    if isinstance(child, AbstractVariableNode):
                        tmp_new_keys.update(self._propagateMutation(child, mut_inst))
        # elif isinstance(variable, Agg) and isinstance(mutator, AggregateMutator) and mutator.mutateChildren:
            # for child in variable.children:
            #     tmp_new_keys[variable.children] = (mutator.mode, {})
            #     if isinstance(child, AbstractVariableNode):
            #         tmp_new_keys.update(self._propagateMutation(child))

        return tmp_new_keys
