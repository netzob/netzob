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
from netzob.Common.Type.TypeConvertor import TypeConvertor


class ComputedRelationVariable(AbstractRelationVariable):
    """ComputedRelationVariable:
            A variable which points to an other variable and gets its value by computing in a certain way the pointed variable.
    """

    TYPE = "Computed Relation Variable"

    def __init__(self, _id, name, mutable, learnable, relationType, pointedID, symbol):
        """Constructor of ComputedRelationVariable:

                @type relationType: string
                @param relationType: the type of computation we will use.
        """
        AbstractRelationVariable.__init__(self, _id, name, mutable, learnable, pointedID, symbol)
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
        return "[Computed Relation] {0}, pointed ID: {1}, type: {2}.".format(AbstractVariable.toString(self), str(self.getPointedID()), self.relationType.toString())

    def trivialCompareFormat(self, readingToken):
        """trivialCompareFormat:
                We call the compare format function.
        """
        self.log.debug("- [ {0}: trivialCompareFormat.".format(self.toString()))
        self.compareFormat(readingToken)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        self.log.debug("[ {0}: toXML:".format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:ComputedRelationVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # sized
        xmlSized = etree.SubElement(xmlVariable, "{" + namespace + "}sized")
        xmlSized.text = str(self.relationType.getAssociatedDataType().isSized())

        # type
        xmlType = etree.SubElement(xmlVariable, "{" + namespace + "}type")
        xmlType.text = self.relationType.getType()

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = str(self.pointedID)
        self.log.debug("Variable {0}. ]".format(self.getName()))

        # minChars
        xmlMinChars = etree.SubElement(xmlVariable, "{" + namespace + "}minChars")
        xmlMinChars.text = str(self.relationType.getAssociatedDataType().getMinChars())

        # maxBits
        xmlMaxChars = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxChars.text = str(self.relationType.getAssociatedDataType().getMaxChars())

        # delimiter
        xmlDelimiter = etree.SubElement(xmlVariable, "{" + namespace + "}delimiter")
        xmlDelimiter.text = str(TypeConvertor.bin2hexstring(self.relationType.getAssociatedDataType().getDelimiter()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractRelationVariable                         |
#+---------------------------------------------------------------------------+
    def compareFormat(self, readingToken):
        """compareFormat:
                Similar to the pointedVariable's own compareFormat function.
        """
        self.log.debug("- [ {0}: compareFormat.".format(self.toString()))
        self.getDataType().compareFormat(readingToken)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def lightRead(self, readingToken):
        """lightRead:
                We simply compare the format.
        """
        self.compareFormat(readingToken)

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the variable type and the given generation strategy.
        """
        self.log.debug("- {0}: generate.".format(self.toString()))
        self.setCurrentValue(self.relationType.getAssociatedDataType().generateValue(writingToken.getGenerationStrategy(), self.minChars, self.maxChars))

    def computeValue(self, value):
        """computeValue:
                Compute the value of the relation variable from the given value..
        """
        self.log.debug("- {0}: computeValue.".format(self.toString()))
        return self.relationType.computeValue(value)

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
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads a ComputedRelationVariable from an XML definition.
        """
        logging.debug("[ ComputedRelationVariable: loadFromXML:")
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            # sized
            xmlSized = xmlRoot.find("{" + namespace + "}sized")
            if xmlSized is not None and xmlSized.text != "None":
                sized = xmlSized.text == 'True'
            else:
                sized = True

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

            # delimiter
            xmlDelimiter = xmlRoot.find("{" + namespace + "}delimiter")
            if xmlDelimiter is not None and xmlDelimiter.text != "None":
                delimiter = xmlDelimiter.text
            else:
                delimiter = None

            # type
            _type = None
            xmlType = xmlRoot.find("{" + namespace + "}type")
            if xmlType is not None:
                _type = AbstractRelationType.makeType(xmlType.text, sized, minChars, maxChars, delimiter)
                if _type is None:
                    return None
            else:
                logging.error("No type specified for this variable in the xml file.")
                return None

            # ref
            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text

            result = ComputedRelationVariable(xmlID, xmlName, xmlMutable, xmlLearnable, _type, xmlRefID, symbol)
            logging.debug("ComputedRelationVariable: loadFromXML successes: {0} ]".format(result.toString()))
            return result
        logging.debug("ComputedRelationVariable: loadFromXML fails")
        return None
