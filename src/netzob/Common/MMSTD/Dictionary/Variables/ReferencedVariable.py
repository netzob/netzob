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
            Beware when using it, it can leads to obviously dangerous behavior.
    """

    TYPE = "Referenced Variable"

    def __init__(self, _id, name, mutable, random, pointedID):
        """Constructor of ReferencedVariable:
        """
        AbstractVariable.__init__(self, _id, name, mutable, random, False)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.ReferencedVariable.py')
        self.pointedID = pointedID

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
        return _("[Referenced] {0}, pointed ID: {1}").format(AbstractVariable.toString(self), str(self.pointedID))

    def getDescription(self, processingToken):
        """getDescription:
        """
        return _("[{0}]").format(self.toString())

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        return _("[{0}]").format(self.toString())

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

    def restore(self, processingToken):
        """restore:
            Restore the value of the pointed variable.
        """
        var = self.getPointedVariable()
        if var is not None:
            var.restore(processingToken)

    def getDictOfValues(self, processingToken):
        """getDictOfValues:
                Get the dictionary of values of the pointed variable.
        """
        var = self.getPointedVariable()
        if var is not None:
            return var.getDictOfValues(processingToken)
        else:
            return None

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        self.log.debug(_("[ {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ReferencedVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("random", str(self.isRandom()))

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = self.pointedVariable.getID()
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getPointedID(self):
        return self.pointedID

    def getPointedVariable(self, vocabulary):
        variable = vocabulary.getVariableByID(self.pointedID)
        return self.getPointedVariable(variable)

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
        logging.debug(_("[ ReferencedVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlRandom = xmlRoot.get("random") == "True"

            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            result = ReferencedVariable(xmlID, xmlName, xmlMutable, xmlRandom, xmlRefID)
            logging.debug(_("ReferencedVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("ReferencedVariable: loadFromXML fails"))
        return None
