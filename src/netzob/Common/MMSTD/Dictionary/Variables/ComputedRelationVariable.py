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
from netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType import \
    AbstractRelationType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.Type.TypeConvertor import TypeConvertor


class ComputedRelationVariable(AbstractVariable):
    """ComputedRelationVariable:
            A variable which points to an other variable and gets its value by computing in a certain way the pointed variable.
    """

    TYPE = "Computed Relation Variable"

    def __init__(self, _id, name, mutable, learnable, relationType, pointedID, symbol):
        """Constructor of ComputedRelationVariable:
                Mutable and learnable are useless.

                @type relationType: string
                @param relationType: the type of computation we will use.
        """
        AbstractVariable.__init__(self, _id, name, mutable, learnable, False)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.ComputedRelationVariable.py')
        self.relationType = relationType
        self.currentValue = None
        self.pointedID = pointedID
        self.symbol = symbol
        self.pointedVariable = None

    def findDirectPointer(self):
        """findDirectPointer:
                A direct pointer or left pointer points from the right of a tree to the left or an other tree.
                A reverse pointer or right pointer points from the left of a tree to its right.
        """
        if self.pointedID is None:
            return True
            self.log.debug("No pointed ID.")
        treeElements = self.symbol.getRoot().getProgeny()
        found = False
        for element in treeElements:
            if not found and element.getID() == self.pointedID:
                self.log.debug("We found the pointed value.")
                found = True
            if element.getID() == self.getID():
                if found:
                    self.log.debug("The pointing value is after the pointed value in the same tree.")
                    return True
                else:
                    self.log.debug("The pointing value is before the pointed value or in a different tree.")
                    return False
        self.log.debug("Default case.")
        return True

    def retrieveValue(self, processingToken):
        """retrieveValue:
                Retrieve a value according to the pointed variable's own value and attribute it to the variable

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- {0}: retrieveValue.".format(self.toString()))
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
            self.currentValue = None
        else:
            self.currentValue = self.computeValue(self.getPointedVariable().getValue(processingToken))

    def guessValue(self):
        """guessValue:
                Try to guess the pointed variable's value and give it to the current value.
        """
        # The 'TEMP' value is explicit enough.
        self.currentValue = TypeConvertor.stringB2bin("TEMP")

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: compare.".format(self.toString()))
        localValue = self.currentValue
        tmp = readingToken.getValue()[readingToken.getIndex():]
        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self.log.debug("Comparison successful.")
                readingToken.read(self, len(localValue))
                readingToken.setOk(True)
            else:
                readingToken.setOk(False)
                self.log.debug("Comparison failed: wrong value.")
        else:
            readingToken.setOk(False)
            self.log.debug("Comparison failed: wrong size.")

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def compareFormat(self, readingToken):
        """compareFormat:
                Similar to the pointedVariable's own compareFormat function.
        """
        self.log.debug("- [ {0}: compareFormat.".format(self.toString()))
        self.getDataType().compareFormat(readingToken)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def bindValue(self, processingToken):
        """bindValue:
                Bind itself to the pointed variable in order to be notified by this variable in case of modification of it.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
        else:
            self.getPointedVariable().bindVariable(self)

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

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug("- [ {0}: writeValue.".format(self.toString()))
        writingToken.write(self, self.currentValue)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

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

    def getDescription(self, processingToken):
        """getDescription:
        """
        return _("[{0}]").format(self.toString())

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        return _("[{0}]").format(self.toString())

    def isDefined(self, processingToken):
        """isDefined:
        """
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
            return False
        else:
            return True

    def restore(self, processingToken):
        """restore:
        """
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
            return False
        else:
            return self.getPointedVariable().restore(processingToken)

    def getDictOfValues(self, processingToken):
        """getDictOfValues:
        """
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
            return dict()
        else:
            return self.getPointedVariable().getDictOfValues(processingToken)

    def read(self, readingToken):
        """read:
                The relation variable tries to compare/learn the read value.
        """
        self.log.debug("[ {0} (relation): read access:".format(AbstractVariable.toString(self)))
        self.directPointer = self.findDirectPointer()

        if self.isDefined(readingToken):
            if self.directPointer:
                # We directly retrieve and compare the value.
                self.retrieveValue(readingToken)
                self.compare(readingToken)
            else:
                # We make a small format comparison.
                self.compareFormat(readingToken)
                # We will verify the value at notification time.
                self.bindValue(readingToken)

        else:
            self.log.debug("Read abort: the variable is not defined.")
            readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken, self.currentValue)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The relation variable returns a computed or a generated value.
        """
        self.log.debug("[ {0} (relation): write access:".format(AbstractVariable.toString(self)))
        self.directPointer = self.findDirectPointer()

        if self.isDefined(writingToken):
            if not self.directPointer:
                # We will write the real value at notification time. (An awaiting value is written though.)
                self.bindValue(writingToken)
                self.guessValue()
            else:
                # We directly retrieve and write the actual value (which would be deprecated and replaced if the variable is directPointer).
                self.retrieveValue(writingToken)
            self.writeValue(writingToken)
        else:
            self.log.debug("Write abort: the variable is not defined.")
            writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

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

        # maxChars
        xmlMaxChars = etree.SubElement(xmlVariable, "{" + namespace + "}maxChars")
        xmlMaxChars.text = str(self.relationType.getAssociatedDataType().getMaxChars())

        # delimiter
        xmlDelimiter = etree.SubElement(xmlVariable, "{" + namespace + "}delimiter")
        xmlDelimiter.text = str(TypeConvertor.bin2hexstring(self.relationType.getAssociatedDataType().getDelimiter()))

#+---------------------------------------------------------------------------+
#| Notified functions                                                        |
#+---------------------------------------------------------------------------+
    def notifiedRead(self, readingToken, pointedValue):
        """notifiedRead:
                A read access called by a notification of the pointed variable (when it has finished its own treatment).
                It checks that the new value complies with the reading token value at this very position.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("[ {0} (relation): read access:".format(AbstractVariable.toString(self)))

        if self.isDefined(readingToken):
            for linkedValue in readingToken.getLinkedValue():
                if linkedValue[0] == self.getID():
                    # We compare the pointed value to the value the current variable wrote in memory.
                    if linkedValue[1] != self.computeValue(pointedValue):
                        readingToken.setOk(False)
                        break

        else:
            self.log.debug("Read abort: the variable is neither defined, nor mutable.")
            readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken, pointedValue)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def notifiedWrite(self, writingToken):
        """notify:
                A write access called by a notification of the pointed variable (when it has finished its own treatment).
                It updates the values this variable has written in the writingToken value.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug("[ {0} (relation): notifiedWrite access:".format(AbstractVariable.toString(self)))

        if self.isDefined(writingToken):

            # Compute the value
            self.retrieveValue(writingToken)

            # replace the new value in the writing token
            writingToken.setValueForVariable(self, self.currentValue)

        else:
            self.log.debug("Write abort: the variable is neither defined, nor random.")
            writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getCurrentValue(self):
        return self.currentValue

    def getPointedID(self):
        return self.pointedID

    def getPointedVariable(self):
        if self.pointedVariable is not None:
            if self.pointedVariable.getID() == self.pointedID:
                # The pointed variable is already set.
                return self.pointedVariable
        self.pointedVariable = self.symbol.getProject().getVocabulary().getVariableByID(self.pointedID)
        return self.pointedVariable

    def getDataType(self):
        return self.relationType.getAssociatedDataType()

    def getRelationType(self):
        return self.relationType

    def isDirectPointer(self):
        return self.directPointer

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue

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
