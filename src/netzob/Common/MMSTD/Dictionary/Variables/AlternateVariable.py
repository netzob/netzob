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
    def learn(self, readingToken):
        """learn:
                Each child tries to learn the read value. If it fails, it restore it value and the next child try.
                If one child successes, the result is Ok and the process is stopped.
        """
        self.log.debug(_("Children of variable {0} learn.").format(self.getName()))
        for child in self.children:
            readingToken.setOk(True)
            child.learn(readingToken)
            if readingToken.isOk():
                break
            child.restore(readingToken)

    def compare(self, readingToken):
        """compare:
                Each child tries to compare its value to the read value. If it fails, it restore it value and the next child try.
                If one child successes, the result is Ok.
        """
        self.log.debug(_("Children of variable {0} are compared.").format(self.getName()))
        for child in self.children:
            readingToken.setOk(True)
            child.compare(readingToken)
            if readingToken.isOk():
                break

    def getValue(self, writingToken):
        """getValue:
                Returns the value of the first child which is not None.
        """
        self.log.debug(_("Children of variable {0} return their values.").format(self.getName()))
        for child in self.children:
            child.getValue(writingToken)
            if writingToken.getValue() is not None:
                break

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
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            return AlternateVariable(id, name, children)
        return None
