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
from typing import Dict  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType  # noqa: F401
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
from netzob.Fuzzing.DomainMutator import DomainMutator, MutatorMode  # noqa: F401
from netzob.Fuzzing.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator


class Fuzz(object):
    """The root class for fuzzing.

    This class holds the mapping between fields and their mutator, as
    well as the mapping between types and their default mutator.

    """

    mappingTypesMutators = {}   # type: Dict[AbstractType, DomainMutator]
    mappingFieldsMutators = {}  # type: Dict[Field, DomainMutator]

    # Initialize mapping of types with their mutators
    @staticmethod
    def initializeMappings():
        Fuzz.mappingFieldsMutators = {}
        Fuzz.mappingTypesMutators = {}
        Fuzz.mappingTypesMutators[Integer] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[String] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[HexaString] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[Raw] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[BitArray] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[IPv4] = PseudoRandomIntegerMutator
        Fuzz.mappingTypesMutators[Timestamp] = PseudoRandomIntegerMutator

    def __init__(self):
        Fuzz.initializeMappings()
        self.mappingTypesMutators = Fuzz.mappingTypesMutators
        self.mappingFieldsMutators = Fuzz.mappingFieldsMutators

    def set(self, key, value, **kwargs):
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
        from netzob.Fuzzing.Fuzz import Fuzz
        from netzob.Fuzzing.Mutator import Mutator
        for k, v in self.mappingFieldsMutators.items():
            if not isinstance(v, tuple):
                raise TypeError("Value should be a tuple. Got: '{}'".format(v))
            (v_m, v_kwargs) = v
            if inspect.isclass(v_m) and issubclass(v_m, Mutator):
                # We instanciate the mutator
                v_m_instance = v_m(domain=k.domain, **v_kwargs)
                # We replace the mutator class by the mutate instance in the main dict
                self.set(k, v_m_instance)
            elif isinstance(v_m, Mutator):
                pass
            elif v_m == MutatorMode.NONE:
                keys_to_remove.append(k)
            elif v_m in [MutatorMode.GENERATE, MutatorMode.MUTATE]:
                mutator_instance = Fuzz.defaultMutator(k.domain, **v_kwargs)
                mutator_instance.mode = v_m
                self.set(k, mutator_instance)
            else:
                raise Exception("Fuzz's value '{} (type: {})' must be a Mutator instance or Mutator.(GENERATE|MUTATE|NONE)".format(v, type(v)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
