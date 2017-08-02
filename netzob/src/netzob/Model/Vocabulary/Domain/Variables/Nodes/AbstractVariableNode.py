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
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


class AbstractVariableNode(AbstractVariable):
    """Represents a node in the variable definition of a field.

    A node is a variable which accepts children, such as Alternate(:class:`netzob.Model.Vocabulary.Variables.Nodes.Alt.Alt`)
    and Aggregate (:class:`netzob.Model.Vocabulary.Variables.Nodes.Agg.Agg`).
    Thus both of them inherits from this.

    """

    def __init__(self, varType, children=None, svas=None):
        super(AbstractVariableNode, self).__init__(varType, svas=svas)
        self._children = []
        if children is not None:
            self.children = children

    @property
    def children(self):
        """Sorted typed list of children attached to the variable node.
        .. warning:: Setting this value with a list copies its members and not the list itself.

        :type: a list of :class:`netzob.Model.Vocabulary.Variables.Variable`

        """
        return self._children

    @children.setter
    def children(self, children):
        from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory
        self._children = []
        for child in children:
            normalizedChild = DomainFactory.normalizeDomain(child)
            self._children.append(normalizedChild)

    def _str_debug(self, deepness=0):
        """Returns a string which denotes
        the current field definition using a tree display"""

        tab = ["     " for x in range(deepness - 1)]
        tab.append("|--   ")
        tab.append("{0}".format(self))
        lines = [''.join(tab)]
        for f in self.children:
            lines.append(" " + f._str_debug(deepness + 1))
        return '\n'.join(lines)

    def XMLProperties(currentNode, xmlAbsVarNode, symbol_namespace, common_namespace):
        AbstractVariable.XMLProperties(currentNode, xmlAbsVarNode, symbol_namespace, common_namespace)

        if currentNode.children is not None and len(currentNode.children) > 0:
            xmlChildren = etree.SubElement(xmlAbsVarNode, "{" + symbol_namespace + "}children")
            for child in currentNode.children:
                child.saveToXML(xmlChildren, symbol_namespace, common_namespace)

    def saveToXML(self, xmlroot, symbol_namespace, common_namespace):
        xmlAbsVarNode = etree.SubElement(xmlroot, "{" + symbol_namespace + "}abstractVariableNode")

        AbstractVariableNode.XMLProperties(self, xmlAbsVarNode, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):
        from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable

        children = []
        if xmlroot.find("{" + symbol_namespace + "}children") is not None:
            xmlChildren= xmlroot.find("{" + symbol_namespace + "}children")
            for xmlData in xmlChildren.findall("{" + symbol_namespace + "}data"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
                data = Data.loadFromXML(xmlData, symbol_namespace, common_namespace)
                if data is not None:
                    children.append(data)
            for xmlValue in xmlChildren.findall("{" + symbol_namespace + "}value"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.Value import Value
                value = Value.loadFromXML(xmlValue, symbol_namespace, common_namespace)
                if value is not None:
                    children.append(value)
            for xmlSize in xmlChildren.findall("{" + symbol_namespace + "}size"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.Size import Size
                size = Size.loadFromXML(xmlSize, symbol_namespace, common_namespace)
                if size is not None:
                    children.append(size)
            for xmlChecksum in xmlChildren.findall("{" + symbol_namespace + "}checksum"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.InternetChecksum import InternetChecksum
                checksum = InternetChecksum.loadFromXML(xmlChecksum, symbol_namespace, common_namespace)
                if checksum is not None:
                    children.append(checksum)
            for xmlAgg in xmlChildren.findall("{" + symbol_namespace + "}aggregation"):
                from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
                agg = Agg.loadFromXML(xmlAgg, symbol_namespace, common_namespace)
                if agg is not None:
                    children.append(agg)
            for xmlAlt in xmlChildren.findall("{" + symbol_namespace + "}alternative"):
                from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
                alt = Alt.loadFromXML(xmlAlt, symbol_namespace, common_namespace)
                if alt is not None:
                    children.append(alt)
            for xmlRepeat in xmlChildren.findall("{" + symbol_namespace + "}repeat"):
                from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
                repeat = Repeat.loadFromXML(xmlRepeat, symbol_namespace, common_namespace)
                if repeat is not None:
                    children.append(repeat)
            for xmlabsRelVarLeaf in xmlChildren.findall("{" + symbol_namespace + "}abstractRelationVariableLeaf"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
                absRelVarLeaf = AbstractRelationVariableLeaf.loadFromXML(xmlabsRelVarLeaf, symbol_namespace, common_namespace)
                if absRelVarLeaf is not None:
                    children.append(absRelVarLeaf)
            for xmlabsVarLeaf in xmlChildren.findall("{" + symbol_namespace + "}abstractVariableLeaf"):
                from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
                absVarLeaf = AbstractVariableLeaf.loadFromXML(xmlabsVarLeaf, symbol_namespace, common_namespace)
                if absVarLeaf is not None:
                    children.append(absVarLeaf)
            for xmlabstractVariableNode in xmlChildren.findall("{" + symbol_namespace + "}abstractVariableNode"):
                from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
                abstractVariableNode = AbstractVariableNode.loadFromXML(xmlabstractVariableNode, symbol_namespace, common_namespace)
                if abstractVariableNode is not None:
                    children.append(abstractVariableNode)
            for xmlabstractVariable in xmlChildren.findall("{" + symbol_namespace + "}abstractVariable"):
                abstractVariable = AbstractVariable.loadFromXML(xmlabstractVariable, symbol_namespace, common_namespace)
                if abstractVariable is not None:
                    children.append(abstractVariable)
        attributes['children'] = children

        AbstractVariable.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = AbstractVariableNode.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        absVarNode = None

        if 'varType' in a.keys() and 'id' in a.keys():
            absVarNode = AbstractVariableNode(varType=a['varType'], children=a['children'], svas=a['svas'])
            if 'id' in a.keys():
                absVarNode.id = a['id']
            if 'name' in a.keys():
                absVarNode.name = a['name']
        return absVarNode


