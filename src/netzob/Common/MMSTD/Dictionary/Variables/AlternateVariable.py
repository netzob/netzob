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
from lxml import etree
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractNodeVariable import AbstractNodeVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import AbstractVariable


class AlternateVariable(AbstractNodeVariable):
    """AlternateVariable:
            A data variable defined in a dictionary which is a logical or of several variables.
    """

    TYPE = "AlternateVariable"

    def __init__(self, id, name, mutable, random, children=None):
        """Constructor of AlternateVariable:
        """
        AbstractNodeVariable.__init__(self, id, name, mutable, random, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AlternateVariable.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getType(self):
        """getType:
        """
        return AlternateVariable.TYPE

    def getDescription(self, processingToken):
        """getDescription:
        """
        values = []
        for child in self.children:
            values.append(child.getDescription(processingToken))
        return "[ALT] " + str(self.getName()) + "= (" + " OR ".join(values) + ")"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        values = []
        for child in self.children:
            values.append(child.getUncontextualizedDescription())
        return "[ALT] " + str(self.getName()) + "= (" + " OR ".join(values) + ")"

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

        # random
        xmlRandom = etree.SubElement(xmlVariable, "{" + namespace + "}random")
        xmlRandom.text = str(self.random)

        # mutable
        xmlMutable = etree.SubElement(xmlVariable, "{" + namespace + "}mutable")
        xmlMutable.text = str(self.mutable)

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
        logging.debug(_("AlternateVariable's function loadFromXML is used."))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")

            # mutable
            xmlMutable = xmlRoot.find("{" + namespace + "}mutable")
            if xmlMutable is not None:
                mutable = xmlMutable.text == "True"
            else:
                mutable = True

            # random
            xmlRandom = xmlRoot.find("{" + namespace + "}random")
            if xmlRandom is not None:
                random = xmlRandom.text == "True"
            else:
                random = False

            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AlternateVariable(xmlID, mutable, random, xmlName, children)
        return None
