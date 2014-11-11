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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken


class AbstractVariableNode(AbstractVariable):
    """Represents a node in the variable definition of a field.

    A node is a variable which accepts children, such as Alternate(:class:`netzob.Common.Models.Vocabulary.Variables.Nodes.Alt.Alt`)
    and Aggregate (:class:`netzob.Common.Models.Vocabulary.Variables.Nodes.Agg.Agg`).
    Thus both of them inherits from this.

    """

    def __init__(self, varType, children=None, svas=None):
        super(AbstractVariableNode, self).__init__(varType, svas=svas)
        self._children = []
        if children is not None:
            self.children = children

    @typeCheck(AbstractVariableProcessingToken)
    def getDictOfValues(self, processingToken):
        """We concatenate every dictOfValues of each child.
        """
        if processingToken is None:
            raise TypeError("Processing token cannot be None")

        dictOfValues = dict()
        for child in self.children:
            dictOfValue = child.getDictOfValues(processingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val
        return dictOfValues

    @property
    def children(self):
        """Sorted typed list of children attached to the variable node.
        .. warning:: Setting this value with a list copies its members and not the list itself.

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Variables.Variable`

        """
        return self._children

    @children.setter
    def children(self, children):
        from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
        self._children = []
        for child in children:
            normalizedChild = DomainFactory.normalizeDomain(child)
            self._children.append(normalizedChild)

    def _str_debug(self, deepness=0):
        """Returns a string which denotes
        the current field definition using a tree display"""

        tab = ["     " for x in xrange(deepness - 1)]
        tab.append("|--   ")
        tab.append("{0}".format(self))
        lines = [''.join(tab)]
        for f in self.children:
            lines.append(" " + f._str_debug(deepness + 1))
        return '\n'.join(lines)
