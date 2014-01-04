#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode


class DomainFactory(object):
    """This factory allows to manipulate a domain as for example to normalize it.

    For instance, you can normalize domains provided by users

    >>> from netzob.all import *
    >>> domain = DomainFactory.normalizeDomain([Raw(), 10])
    >>> print domain.varType
    Alt
    >>> print domain.children[0].dataType
    Raw=None ((0, None))
    >>> print domain.children[1].dataType
    Decimal=10 ((8, 8))

    >>> domain = DomainFactory.normalizeDomain(Agg([Alt(["toto", 20]), ASCII("!")]))
    >>> print domain.varType
    Agg
    >>> print domain.children[0].varType
    Alt
    >>> print domain.children[0].children[1].dataType
    Decimal=20 ((8, 8))
    >>> print domain.children[1].dataType
    ASCII=! ((0, None))

    >>> f = Field(domain=[Alt(["bb", ASCII("aa", nbChars=2), ASCII("aa", nbChars=2)]), ["aaaa", "aaaa"]])
    >>> print f._str_debug()
    Field
    |--   Alt (L=False, M=True)
          |--   Alt (L=False, M=True)
               |--   ASCII=bb ((0, None)) (currentValue=bb, L=False, M=False)
               |--   ASCII=aa ((16, 16)) (currentValue=aa, L=False, M=False)
          |--   ASCII=aaaa ((0, None)) (currentValue=aaaa, L=False, M=False)

    """

    @staticmethod
    def normalizeDomain(domain):
        # If domain starts with an Alternative (or a list)
        if isinstance(domain, (list, Alt)):
            return DomainFactory.__normalizeAlternateDomain(domain)
        # If domain starts with an Aggregate
        elif isinstance(domain, Agg):
            return DomainFactory.__normalizeAggregateDomain(domain)
        else:
            return DomainFactory.__normalizeLeafDomain(domain)

    @staticmethod
    def __normalizeLeafDomain(domain):
        if isinstance(domain, (Data, AbstractRelationVariableLeaf)):
            return domain
        else:
            return AbstractType.normalize(domain).buildDataRepresentation()

    @staticmethod
    def __normalizeAlternateDomain(domain):
        result = Alt()
        if isinstance(domain, list):
            if len(domain) == 1:
                return DomainFactory.__normalizeLeafDomain(domain[0])
        if isinstance(domain, (list, Alt)):
            # Eliminate duplicate elements
            tmpResult = []
            if isinstance(domain, list):
                for child in domain:
                    tmpResult.append(DomainFactory.normalizeDomain(child))
            else:
                for child in domain.children:
                    tmpResult.append(DomainFactory.normalizeDomain(child))
            uniqResult = []    
            for elt in tmpResult:
                if isinstance(elt, AbstractVariableNode):
                    uniqResult.append(elt)
                else:
                    found = False
                    for uElt in uniqResult:
                        if uElt == elt:
                            found = True
                            break
                    if found == False:
                        uniqResult.append(elt)
            if len(uniqResult) == 1:
                return uniqResult[0]
            else:
                for elt in uniqResult:
                    result.children.append(elt)
        else:
            raise TypeError("Impossible to normalize the provided domain as an alternate.")
        return result

    @staticmethod
    def __normalizeAggregateDomain(domain):
        result = Agg()
        if isinstance(domain, Agg):
            for child in domain.children:
                result.children.append(DomainFactory.normalizeDomain(child))
        else:
            raise TypeError("Impossible to normalize the provided domain as an aggregate.")
        return result
