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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable import AbstractVariable


class ReferencedVariable(AbstractVariable):
    """ReferencedVariable:
            A variable which points to an other variable.
    """

    def __init__(self, id, name, pointedID):
        """Constructor of ReferencedVariable:
        """
        AbstractVariable.__init__(self, id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.ReferencedVariable.py')
        self.pointedID = pointedID

    def getPointedVariable(self, processingToken):
        """getPointedVariable:

                @rtype: netzob.Common.MMSTD.Dictionary.Variable.Variable
                @return: the pointed variable.
        """
        var = processingToken.getVocabulary().getVariableByID(self.varID)
        self.log.debug(_("The variable pointed by variable {0} is variable {1}.").format(var.getName()))
        if var is not None:
            return var
        else:
            self.log.error("Impossible to retrieve the referenced variable which ID is " + self.pointedID)
            processingToken.setOk(False)
            return None

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def forget(self, processingToken):
        """forget:
                The pointed variable forgets its value.
        """
        self.log.debug(_("The variable pointed by variable {0} is forgotten.").format(self.getName()))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            processingToken.getMemory().forget(var)

    def memorize(self, processingToken):
        """memorize:
                The pointed variable memorizes its value.
        """
        self.log.debug(_("The variable pointed by variable {0} is memorized.").format(self.getName()))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            processingToken.getMemory().memorize(var)

    def learn(self, readingToken):
        """learn:
                The pointed variable tries to learn the read value.
        """
        self.log.debug(_("The variable pointed by variable {0} learns {1} (if their format are compatible) starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            var.learn(readingToken)

    def compare(self, readingToken):
        """compare:
                The pointed variable compares its value to the read value.
        """
        self.log.debug(_("The variable pointed by variable {0} compares its current value to {1} starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            var.compare(readingToken)

    def generate(self, writingToken):
        """generate:
                A new current value is generated for the pointed variable according to the variable type and the given generation strategy.
        """
        self.log.debug(_("The variable pointed by variable {0} generates a value.").format(self.getName()))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            var.generate(writingToken)

    def getValue(self, writingToken):
        """getValue:
                Returns the pointed variable value.
        """
        self.log.debug(_("The variable pointed by variable {0} gets its value.").format(self.getName()))
        var = self.getPointedVariable(processingToken)
        if var is not None:
            var.getValue(writingToken)

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ReferencedVariable")

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlWordVariable, "{" + namespace + "}ref")
        xmlRefID.text = self.pointedID

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
            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            return ReferencedVariable(xmlID, xmlName, xmlRefID)
        return None
