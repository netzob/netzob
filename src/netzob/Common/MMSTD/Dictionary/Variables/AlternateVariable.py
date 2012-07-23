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


class AlternateVariable(AbstractNodeVariable):
    """AlternateVariable:
            A data variable defined in a dictionary which is a logical or of several variables.
    """

    def __init__(self, id, name, children=None):
        """Constructor of AlternateVariable:
        """
        AbstractNodeVariable.__init__(self, id, name, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AlternateVariable.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def isDefined(self):
        """isDefined:
                If one child is defined the node is defined.
        """
        if self.children is not None:
            self.setDefined(False)
            for child in self.getChildren():
                if child.isDefined():
                    self.setDefined(True)
                    break
        else:
            self.setDefined(False)

    def read(self, readingToken):
        """read:
                Each child tries to read the value.
                If it fails, it restore it value and the next child try.
                It stops if one child successes.
        """
        self.log.debug(_("Children of variable {0} read.").format(self.getName()))
        savedIndex = readingToken.getIndex()
        childValue = None
        for child in self.getChildren():
            childValue = child.getValue()
            child.read(readingToken)
            if readingToken.isOk():
                break
            else:
                readingToken.setIndex(savedIndex)
                child.setValue(childValue)

    def write(self, writingToken):
        """write:
                Each child tries to write its value..
                If it fails, it restore it value and the next child try.
                It stops if one child successes.
        """
        self.log.debug(_("Children of variable {0} write.").format(self.getName()))
        childValue = None
        savedValue = writingToken.getValue()
        for child in self.getChildren():
            childValue = child.getValue()
            child.write(writingToken)
            if writingToken.isOk() and writingToken.getValue() is not None:
                break
            else:
                writingToken.setValue(savedValue)
                child.setValue(childValue)

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AlternateVariable")

        # Definition of children variables
        for child in self.children:
            child.toXML(xmlVariable, namespace)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an alternate variable from an XML definition.
        """
        self.log.debug(_("AlternateVariable's function loadFromXML is used."))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AlternateVariable(id, name, children)
        return None
