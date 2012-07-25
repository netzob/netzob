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
from gettext import gettext as _
from lxml import etree
import copy
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class ReferencedVariable(AbstractVariable):
    """ReferencedVariable:
            A variable which points to an other variable.
    """

    TYPE = "ReferencedVariable"

    def __init__(self, id, name, pointedID, vocabulary):
        """Constructor of ReferencedVariable:
        """
        AbstractVariable.__init__(self, id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.ReferencedVariable.py')
        pointedVariable = vocabulary.getVariableByID(pointedID)
        self.setPointedVariable(pointedVariable)

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return ReferencedVariable.TYPE

    def toString(self):
        """toString:
        """
        return _("[Referenced] {0}").format(AbstractVariable.toString(self))

    def getDescription(self, processingToken):
        """getDescription:
        """
        return _("[{0}, pointed variable:\n - {3}]").format(self.toString(), self.pointedVariable.getDescription(processingToken))

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        return _("[{0}, pointed variable:\n - {3}]").format(self.toString(), self.pointedVariable.getUncontextualizedDescription())

    def isDefined(self):
        return self.getPointedVariable().isDefined()

    def read(self, readingToken):
        """read:
                The pointed variable reads the value.
        """
        self.log.debug(_("[ {0}: read access:").format(self.toString()))
        var = self.getPointedVariable()
        if var is not None:
            var.read(readingToken)
        else:
            readingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The pointed variable writes its value.
        """
        self.log.debug(_("[ {0}: write access:").format(self.toString()))
        var = self.getPointedVariable()
        if var is not None:
            var.write(writingToken)
        else:
            writingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        self.log.debug(_("[ {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ReferencedVariable")

        # random
        xmlRandom = etree.SubElement(xmlVariable, "{" + namespace + "}random")
        xmlRandom.text = str(self.random)

        # mutable
        xmlMutable = etree.SubElement(xmlVariable, "{" + namespace + "}mutable")
        xmlMutable.text = str(self.mutable)

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = self.pointedVariable.getID()
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getPointedVariable(self):
        return self.getPointedVariable()

    def setPointedVariable(self, pointedVariable):
        self.origPointedVariable = pointedVariable
        if self.isRandom():
            # We use a deepĉopy with the random attribute.
            self.pointedVariable = copy.deepcopy(pointedVariable)
            self.pointedVariable.setRandom(True)
        else:
            self.pointedVariable = pointedVariable

    def setRandom(self, random):
        self.random = random
        self.setPointedVariable(self.origPointedVariable)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an alternate variable from an XML definition.
        """
        logging.debug(_("ReferencedVariable's function loadFromXML is used."))
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

            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            return ReferencedVariable(xmlID, xmlName, mutable, random, xmlRefID)
        return None
