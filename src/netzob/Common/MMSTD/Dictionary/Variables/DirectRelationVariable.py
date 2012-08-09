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
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken import \
    VariableReadingToken
from netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken import \
    VariableWritingToken
from netzob.Common.MMSTD.Dictionary.Variables.AbstractRelationVariable import \
    AbstractRelationVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class DirectRelationVariable(AbstractRelationVariable):
    """DirectRelationVariable:
            A variable which simply points to an other value.
    """

    TYPE = "Direct Relation Variable"

    def __init__(self, _id, name, mutable, random, pointedID):
        """Constructor of DirectRelationVariable:
        """
        AbstractRelationVariable.__init__(self, _id, name, mutable, random, pointedID)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractRelationVariable.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return DirectRelationVariable.TYPE

    def toString(self):
        """toString:
        """
        return _("[Direct Relation] {0}, pointed ID: {1}").format(AbstractVariable.toString(self), str(self.pointedID))

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.
        """
        self.log.debug(_("[ {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:DirectRelationVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("random", str(self.isRandom()))

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = self.pointedID
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractRelationVariable                         |
#+---------------------------------------------------------------------------+
    def retrieveValue(self, readingToken):
        """retrieveValue:
        """
        self.log.debug(_("- {0}: generate.").format(self.toString()))
        pointedVariable = self.getPointedVariable(readingToken.getVocabulary())
        if pointedVariable is None:
            readingToken.setOk(False)
            self.log.debug("No pointed variable.")
        else:
            readingToken2 = VariableReadingToken(readingToken.getNegative(), readingToken.getVocabulary(), readingToken.getMemory(), readingToken.getValue(), readingToken.getIndex())
            pointedVariable.read(readingToken2)
            self.setCurrentValue(pointedVariable.getValue())

    def learn(self, readingToken):
        """learn:
                The variable checks if the pointed variable's format complies with the read value's format.
                If it matches, the variable learns, else it returns NOk.
        """
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))
        tmp = readingToken.getValue()[readingToken.getIndex():]

        pointedVariable = self.getPointedVariable(readingToken.getVocabulary())
        if pointedVariable is None:
            self.log.debug("No pointed variable.")
            readingToken.setOk(False)
        else:
            minBits = pointedVariable.getMinBits()
            maxBits = pointedVariable.getMaxBits()
            # Length comparison.
            if len(tmp) >= minBits:
                if len(tmp) <= maxBits:
                    # Format comparison.
                    if pointedVariable.getType().suitsBinary(tmp):
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
                    if pointedVariable.getType().suitsBinary(tmp[:maxBits]):
                        # We learn as much as we can.
                        self.setCurrentValue(tmp[:maxBits])
                        readingToken.incrementIndex(maxBits)
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
                A new current value is generated according to the pointed variable type and the given generation strategy.
        """
        self.log.debug(_("- {0}: generate.").format(self.toString()))
        pointedVariable = self.getPointedVariable(writingToken.getVocabulary())
        if pointedVariable is None:
            writingToken.setOk(False)
            self.log.debug("No pointed variable.")
        else:
            self.setCurrentValue(pointedVariable.getType().generateValue(writingToken.getGenerationStrategy()))

    def computeValue(self, writingToken):
        """computeValue:
                Compute the value of the relation variable according to the pointed variable's own value.
        """
        self.log.debug(_("- {0}: generate.").format(self.toString()))
        pointedVariable = self.getPointedVariable(writingToken.getVocabulary())
        if pointedVariable is None:
            writingToken.setOk(False)
            self.log.debug("No pointed variable.")
        else:
            writingToken2 = VariableWritingToken(writingToken.getNegative(), writingToken.getVocabulary(), writingToken.getMemory(), bitarray(''), writingToken.getGenerationStrategy())
            pointedVariable.write(writingToken2)
            self.setCurrentValue(writingToken2.getValue())

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a DirectRelationVariable variable from an XML definition.
        """
        logging.debug(_("[ DirectRelationVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlRandom = xmlRoot.get("random") == "True"

            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            result = DirectRelationVariable(xmlID, xmlName, xmlMutable, xmlRandom, xmlRefID)
            logging.debug(_("DirectRelationVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("DirectRelationVariable: loadFromXML fails"))
        return None
