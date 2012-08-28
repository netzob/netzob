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
from netzob.Common.MMSTD.Dictionary.Variables.AbstractRelationVariable import \
    AbstractRelationVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class DirectRelationVariable(AbstractRelationVariable):
    """DirectRelationVariable:
            A variable which simply points to an other value.
    """

    TYPE = "Direct Relation Variable"

    def __init__(self, _id, name, mutable, learnable, pointedID, symbol):
        """Constructor of DirectRelationVariable:
        """
        AbstractRelationVariable.__init__(self, _id, name, mutable, learnable, pointedID, symbol)
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
        return _("[Direct Relation] {0}, pointed ID: {1}").format(AbstractVariable.toString(self), str(self.getPointedID()))

    def trivialCompareFormat(self, readingToken):
        """trivialCompareFormat:
                We call recursively the function on the pointed variable.
                This may cause infinite loop so be careful.
        """
        self.getPointedVariable().trivialCompareFormat(readingToken)

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
        xmlVariable.set("learnable", str(self.isLearnable()))

        # Definition of the referenced variable ID.
        xmlRefID = etree.SubElement(xmlVariable, "{" + namespace + "}ref")
        xmlRefID.text = str(self.pointedID)
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractRelationVariable                         |
#+---------------------------------------------------------------------------+
    def compareFormat(self, readingToken):
        """compareFormat:
                The variable checks if its format complies with the read value's format.
        """
        self.log.debug(_("- [ {0}: compareFormat.").format(self.toString()))
        self.getPointedVariable().getType().compareFormat(readingToken)
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def learn(self, readingToken):
        """learn:
        """
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))
        if readingToken.isOk():  # A format comparison had been executed before, its result must be "OK".
            tmp = readingToken.getValue()[readingToken.getIndex():]

            # If the type has a definite size.
            if self.getPointedVariable().getType().isSized():
                maxBits = self.getPointedVariable().getType().getMaxBits()
                # Length comparison. (len(tmp) >= minBits is implicit as the readingToken is OK.)
                if len(tmp) <= maxBits:
                    self.setCurrentValue(tmp)
                    readingToken.incrementIndex(len(tmp))

                else:  # len(tmp) > maxBits
                    # We learn as much as we can.
                    self.setCurrentValue(tmp[:maxBits])
                    readingToken.incrementIndex(maxBits)

            # If the type is delimited from 0 to a delimiter.
            else:
                endi = 0
                for i in range(len(tmp)):
                    if self.getPointedVariable().getType().endsHere(tmp[i:]):
                        endi = i
                        break
                # We learn from the beginning to the delimiter.
                self.setCurrentValue(tmp[:endi + len(self.getPointedVariable().getType().getDelimiter())])  # The delimiter token is a part of the variable.
                readingToken.incrementIndex(endi + len(self.getPointedVariable().getType().getDelimiter()))

            self.log.info(_("Learning done."))
        else:
            self.log.info(_("Learning abort because the previous format comparison failed."))

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def generate(self, writingToken):
        """generate:
                A new current value is generated according to the pointed variable type and the given generation strategy.
        """
        self.log.debug(_("- {0}: generate.").format(self.toString()))
        if self.getPointedVariable() is None:
            writingToken.setOk(False)
            self.log.debug("No pointed variable.")
        else:
            self.setCurrentValue(self.getPointedVariable().getType().generateValue(writingToken.getGenerationStrategy()))

    def computeValue(self, value):
        """computeValue:
                Just affect the value to the current variable.
        """
        self.log.debug(_("- {0}: computeValue.").format(self.toString()))
        return value

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads a DirectRelationVariable variable from an XML definition.
        """
        logging.debug(_("[ DirectRelationVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            xmlRefID = xmlRoot.find("{" + namespace + "}ref").text
            result = DirectRelationVariable(xmlID, xmlName, xmlMutable, xmlLearnable, xmlRefID, symbol)
            logging.debug(_("DirectRelationVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("DirectRelationVariable: loadFromXML fails"))
        return None
