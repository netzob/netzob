#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Common.Models.Vocabulary.Domain.Alt import Alt
from netzob.Common.Models.Vocabulary.Domain.Agg import Agg
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Models.Types.Decimal import Decimal
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.DataTypes.WordType import WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType


class VariableFactory(object):
    """This factory builds Variables following the specifications provided by the user.

    For instance, it allows to create a simple variable for a Raw Field

    >>> from netzob.all import *
    >>> variable = VariableFactory.buildVariableForDomain(["netzob"])
    >>> print variable.__class__.__name__
    AlternateVariable

    """

    @staticmethod
    def buildVariableForDomain(domain):
        # First we assume this domain is not normalized
        normalizedDomain = DomainFactory.normalizeDomain(domain)

        # For each kind of domain we create the proper variable
        if isinstance(normalizedDomain, Alt):
            return VariableFactory._buildVariableForAlternate(normalizedDomain)
        elif isinstance(normalizedDomain, Agg):
            return VariableFactory._buildVariableForAggregate(normalizedDomain)
        elif isinstance(normalizedDomain, AbstractType):
            return VariableFactory._buildVariableForLeafDomain(normalizedDomain)
        else:
            raise TypeError("The provided domain cannot be transformed into a variable")

    @staticmethod
    def _buildVariableForAlternate(alternative):
        variable = AlternateVariable(uuid.uuid4(), "ALT", False, False)
        for child in alternative.children:
            variable.addChild(VariableFactory.buildVariableForDomain(child))
        return variable

    @staticmethod
    def _buildVariableForAggregate(aggregate):
        variable = AggregateVariable(uuid.uuid4(), "AGG", False, False)
        for child in aggregate.children:
            variable.addChild(VariableFactory.buildVariableForDomain(child))
        return variable

    @staticmethod
    def _buildVariableForLeafDomain(leaf):
        # TODO : this MUST be upgraded
        originalValue = bitarray()
        if isinstance(leaf, ASCII):
            if leaf.value is not None:
                originalValue.frombytes(leaf.value)
            typeData = WordType(True, minChars=10, maxChars=100, delimiter=None)
        elif isinstance(leaf, Decimal):
            if leaf.value is not None:
                originalValue = bitarray(leaf.value)
            typeData = IntegerType(True, minChars=0, maxChars=0, delimiter=None)
        elif isinstance(leaf, Raw):
            if leaf.value is not None:
                originalValue = bitarray(leaf.value)
            typeData = BinaryType(True, minChars=0, maxChars=0, delimiter=None)
        else:
            raise TypeError("Unknown type so we can not create a variable.")

        return DataVariable(uuid.uuid4(), "DATA", False, False, typeData, originalValue)
