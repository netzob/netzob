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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType import \
    AbstractRelationType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractRelationVariable import \
    AbstractRelationVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class ComputedRelationVariable(AbstractRelationVariable):
    """ComputedRelationVariable:
            A variable which points to an other variable and gets its value by computing in a certain way the pointed variable.
    """

    TYPE = "Computed Relation Variable"

    def __init__(self, _id, name, mutable, learnable, relationType, pointedVariable, rootVariable):
        """Constructor of ComputedRelationVariable:

                @type relationType: string
                @param relationType: the type of computation we will use.
        """
        AbstractVariable.__init__(self, _id, name, mutable, learnable, pointedVariable, rootVariable)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.ComputedRelationVariable.py')
        self.relationType = relationType
        self.currentValue = None

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return ComputedRelationVariable.TYPE

    def toString(self):
        """toString:
        """
        return _("[Computed Relation] {0}, pointed ID: {1}, type: {2}, minChars: {3}, maxChars: {4}.").format(AbstractVariable.toString(self), str(self.pointedID), self.type.getType(), str(self.getMinChars()), str(self.getMaxChars()))

    def trivialCompareFormat(self, readingToken):
        """trivialCompareFormat:
                We call the compare format function.
        """
        self.log.debug(_("- [ {0}: trivialCompareFormat.").format(self.toString()))
        self.compareFormat(readingToken)
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        self.log.debug(_("[ {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ComputedRelationVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # type
        xmlType = etree.SubElement(xmlVariable, "{" + namespace + "}type")
        xmlType.text = self.type.getType()

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = self.pointedID
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

        # minChars
        xmlMinChars = etree.SubElement(xmlVariable, "{" + namespace + "}minChars")
        xmlMinChars.text = str(self.minChars)

        # maxBits
        xmlMaxChars = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxChars.text = str(self.maxChars)

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractRelationVariable                         |
#+---------------------------------------------------------------------------+
    def compareFormat(self, readingToken):
        """compareFormat:
                Similar to the pointedVariable's own compareFormat function.
        """
        self.log.debug(_("- [ {0}: compareFormat.").format(self.toString()))
        self.getDataType().compareFormat()
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def learn(self, readingToken):
        """learn:
                The pointed variable checks if its format complies with the read value's format.
                If it matches, the variable learns, else it returns NOK.
                Not used anymore but may be interesting in the future.
        """
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))
        tmp = readingToken.getValue()[readingToken.getIndex():]
        # Length comparison.
        if len(tmp) >= self.minBits:
            if len(tmp) <= self.maxBits:
                # Format comparison.
                if self.type.getAssociatedDataType().suitsBinary(tmp):
                    # We learn everything that last.
                    self.setCurrentValue(tmp)
                    readingToken.incrementIndex(len(tmp))
                    readingToken.setOk(True)
                    self.log.info(_("Format comparison successful."))
                else:
                    readingToken.setOk(False)
                    self.log.info(_("Format comparison failed: wrong format."))
            else:  # len(tmp) > self.maxBits
                # Format comparison.
                if self.type.getAssociatedDataType().suitsBinary(tmp[:self.maxBits]):
                    # We learn as much as we can.
                    self.setCurrentValue(tmp[:self.maxBits])
                    readingToken.incrementIndex(self.maxBits)
                    readingToken.setOk(True)
                    self.log.info(_("Format comparison successful."))
                else:
                    readingToken.setOk(False)
                    self.log.info(_("Format comparison failed: wrong format."))
        else:
            readingToken.setOk(False)
            self.log.info(_("Format comparison failed: wrong size."))
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug(_("- {0}: generate.").format(self.toString()))
        self.setCurrentValue(self.type.getAssociatedDataType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))

    def computeValue(self, value):
        """computeValue:
                Compute the value of the relation variable from the given value..
        """
        self.log.debug(_("- {0}: computeValue.").format(self.toString()))
        return self.type.computeValue(value)

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getMinChars(self):
        return self.minChars

    def getMaxChars(self):
        return self.maxChars

    def getDataType(self):
        return self.relationType.getAssociatedDataType()

    def getRelationType(self):
        return self.relationType

    def setDataType(self, dataType):
        self.dataType = AbstractType.makeType(dataType)

    def setRelationType(self, relationType):
        self.dataType = AbstractRelationType.makeType(relationType)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a ComputedRelationVariable from an XML definition.
        """
        logging.debug(_("[ ComputedRelationVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            # type
            _type = None
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                _type = AbstractRelationType.makeType(xmlType.text)
                if _type is None:
                    return None
            else:
                logging.error(_("No type specified for this variable in the xml file."))
                return None

            # minChars
            xmlMinChars = xmlRoot.find("{" + namespace + "}minChars")
            if xmlMinChars is not None:
                minChars = int(xmlMinChars.text)
            else:
                minChars = 0

            # maxChars
            xmlMaxChars = xmlRoot.find("{" + namespace + "}maxChars")
            if xmlMaxChars is not None:
                maxChars = int(xmlMaxChars.text)
            else:
                maxChars = minChars

            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            result = ComputedRelationVariable(xmlID, xmlName, xmlMutable, xmlLearnable, _type, xmlRefID, minChars, maxChars)
            logging.debug(_("ComputedRelationVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("ComputedRelationVariable: loadFromXML fails"))
        return None
