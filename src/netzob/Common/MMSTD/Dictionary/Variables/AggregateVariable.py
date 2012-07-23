# -*- coding: utf-8 -*-

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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from bitarray import bitarray
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AbstractNodeVariable import AbstractNodeVariable


class AggregateVariable(AbstractNodeVariable):
    """AggregateVariable:
            A data variable defined in a dictionary which is a logical and of several variables.
    """

    def __init__(self, id, name, children=None):
        """Constructor of AggregateVariable:
        """
        AbstractNodeVariable.__init__(self, id, name, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AggregateVariable.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def isDefined(self):
        """isDefined:
                If one child is not defined the node is not defined.
        """
        if self.children is not None:
            self.setDefined(True)
            for child in self.getChildren():
                if not child.isDefined():
                    self.setDefined(False)
                    break
        else:
            self.setDefined(False)

    def learn(self, readingToken):
        """learn:
                Each child tries sequentially to learn a part of the read value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug(_("Children of variable {0} learn.").format(self.getName()))
        savedChildren = []
        savedIndex = readingToken.getIndex()
        for child in self.getChildren():
            child.learn(readingToken)
            savedChildren.append(child)
            if not readingToken.isOk():
                break
        # If it has failed we restore every executed children and the index.
        if not readingToken.isOk():
            readingToken.setIndex(savedIndex)
            for child in savedChildren:
                child.restore(readingToken)

    def compare(self, readingToken):
        """compare:
                Each child is sequentially compared to a part of the read value.
                If one comparison fails, the result is NOk, else it is Ok.
        """
        self.log.debug(_("Children of variable {0} are compared.").format(self.getName()))
        for child in self.getChildren():
            child.compare(readingToken)

    def getValue(self, writingToken):
        """getValue:
                Returns the concatenation of all its children values.
        """
        self.log.debug(_("Children of variable {0} return their values.").format(self.getName()))
        value = bitarray()
        for child in self.getChildren():
            value += child.getValue(writingToken)
        writingToken.setValue(value)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")

        # Definition of children variables
        for child in self.children:
            child.toXML(xmlVariable, namespace)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an aggregate variable from an XML definition.
        """
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AggregateVariable(id, name, children)
        return None
