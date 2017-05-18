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
import abc
import random

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp 
from netzob.Model.Grammar.Automata import Automata
from netzob.Fuzzing.PseudoRandomIntegerMutator import PseudoRandomIntegerMutator


class Fuzz(object):
    """The root class for fuzzing.

    This class holds the mapping between fields and their mutator, as
    well as the mapping between types and their default mutator.

    """

    mappingTypesMutators = {}
    mappingFieldsMutators = {}

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
        elif isinstance(key, AbstractField) or isinstance(key, str):
            self.mappingFieldsMutators[key] = (value, kwargs)
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
        if hasattr(domain, 'dataType') and domain.dataType is not None and type(domain.dataType) in Fuzz.mappingTypesMutators:
            mutator = Fuzz.mappingTypesMutators[type(domain.dataType)]
        else:
            raise Exception("The domain '{}' has no configured dataType. Cannot find a default Mutator without information regarding the domain type.")

        # Instanciate the mutator
        mutatorInstance = mutator(domain=domain, **kwargs)

        return mutatorInstance
