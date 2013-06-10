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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class DomainNode(object):
    """Represents a node in the domain definition which has some child

    Alternative (:class:`netzob.Common.Models.Vocabulary.Domain.Alt.Alt`)
    and Aggregate (:class:`netzob.Common.Models.Vocabulary.Domain.Agg.Agg`) inherit
    from this.
    """
    def __init__(self, nodeType, children=None):
        self.__logger = logging.getLogger(__name__)
        self.__nodeType = nodeType
        self._children = []
        if children is not None:
            self.children = children

    @property
    def nodeType(self):
        """The type of the domain node.

        :type: `str`
        :raises: :class:`TypeError` if node type is not an str.
        """
        return self.__nodeType

    @nodeType.setter
    @typeCheck(str)
    def nodeType(self, nodeType):
        self.__nodeType = nodeType

    @property
    def children(self):
        """Sorted typed list of children attached to the domain node.
        .. warning:: Setting this value with a list copies its members and not the list itself.

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Domain.DomainNode`

        """
        return self._children

    @children.setter
    def children(self, children):
        for child in children:
            self._children.append(child)
