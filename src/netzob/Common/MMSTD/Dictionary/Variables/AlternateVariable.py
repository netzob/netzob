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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractNodeVariable import \
    AbstractNodeVariable
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable


class AlternateVariable(AbstractNodeVariable):
    """AlternateVariable:
            A data variable defined in a dictionary which is a logical or of several variables.
    """

    TYPE = "Alternate Variable"

    def __init__(self, _id, name, mutable, learnable, children=[]):
        """Constructor of AlternateVariable:
        """
        AbstractNodeVariable.__init__(self, _id, name, mutable, learnable, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AlternateVariable.py')

    def readChildren(self, readingToken):
        """read:
                Each child tries to read the value.
                If it fails, it restore it value and the next child try.
                It stops if one child successes.
        """
        self.log.debug("[ {0} (Alternate): readChildren:".format(AbstractVariable.toString(self)))
        savedIndex = readingToken.getIndex()
        for child in self.getChildren():
            # Memorized values for the child and its successors.
            dictOfValues = dict()
            dictOfValue = child.getDictOfValues(readingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            child.read(readingToken)
            if readingToken.isOk():
                break
            else:
                readingToken.setIndex(savedIndex)

                # We restore values for the child and its successors.
                child.restore(readingToken)
                vocabulary = readingToken.getVocabulary()
                for key, val in dictOfValues.iteritems():
                    vocabulary.getVariableByID(key).setCurrentValue(val)

        if readingToken.isOk():
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.getValue()[savedIndex:readingToken.getIndex()]

        if self.isLearnable() and not readingToken.isOk() and not self.isLearning():
            # If we dont not found a proper child but the node can learn, we learn the value.
            self.learn(child, readingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def learn(self, child, readingToken):
        """learn:
                The alternate variable learns the given value and adds it at the end of its children.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the child we expected to find while reading the given value.
                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: learn.".format(self.toString()))

        dictOfValues = dict()
        savedIndex = readingToken.getIndex()
        savedFather = self.getFathers()[0]  # TODO: not accurate. But yet  we can only have one father
        selfPosition = savedFather.indexOfChild(self)

        # We create a fake father for this alternate.
        if self.getFathers()[0].getType() == AggregateVariable.TYPE:
            fakeFather = AggregateVariable(str(uuid.uuid4()), "Fake father", False, False)
            # We add this element and its right brother as child of the fake father in order to pursue the read access from where we are.
            fakeFather.addChild(self)
            for rightBrother in self.getFathers()[0].getChildren()[selfPosition:]:
                fakeFather.addChild(rightBrother)
        elif self.getFathers()[0].getType() == RepeatVariable.TYPE:
            (minIterations, maxIterations) = self.getFathers()[0].getNumberIterations()
            # Some iterations of this treatment could have be made before. The fake father should not make more iterations than it remains for the real father.
            minIterations = max(0, minIterations - self.getFathers()[0].getCurrentIteration())
            maxIterations = max(0, maxIterations - self.getFathers()[0].getCurrentIteration())
            fakeFather = RepeatVariable(str(uuid.uuid4()), "Fake father", False, False, self, minIterations, maxIterations)
        else:
            self.log.error("The father is neither an aggregate nor a repeat variable.")

        # We execute the treatment on the fake father.
        valueToBeRead = readingToken.getValue()[readingToken.getIndex():]
        for index in len(valueToBeRead):
            # We search if, by shifting the position of actual variable, we could read the given value.
            tmpValue = valueToBeRead[:index]
            tmpChild = DataVariable(str(uuid.uuid4()), "Learned Inserted Variable", True, True, BinaryType(True, len(tmpValue), len(tmpValue)), tmpValue.to01())
            # We add the new variable at the end, in order to minimize its impact.
            self.add(tmpChild)

            # We read this new variable from the father in a learning context.
            self.setLearning(True)
            fakeFather.read(readingToken)
            # If this read access works, we learn the variable.
            if readingToken.isOk():
                break
            else:
                # We remove the just added child.
                self.removeChild(tmpChild)

        self.removefather(fakeFather)
        # We restore the action induced by the fake father.
        readingToken.setIndex(savedIndex)
        vocabulary = readingToken.getVocabulary()
        for key, val in dictOfValues.iteritems():
            child = vocabulary.getVariableByID(key)
            # We restore the current values.
            child.setCurrentValue(val)
            # We restore the cached values.
            child.restore(readingToken)

        if readingToken.isOk():
            # We continue the treatment. The real father's treatment will pursue.
            self.read(readingToken)

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def writeChildren(self, writingToken):
        """write:
                Each child tries to write its value..
                If it fails, it restore it value and the next child try.
                It stops if one child successes.
        """
        self.log.debug("[ {0} (Alternate): writeChildren:".format(AbstractVariable.toString(self)))

        savedValue = writingToken.getValue()
        savedIndex = writingToken.getIndex()
        for child in self.getChildren():
            # Memorized values for the child and its successor.
            dictOfValues = dict()
            dictOfValue = child.getDictOfValues(writingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            child.write(writingToken)
            if writingToken.isOk() and writingToken.getValue() is not None:
                break
            else:
                writingToken.setValue(savedValue)

                # We restore values for the child and its successor.
                child.restore(writingToken)
                vocabulary = writingToken.getVocabulary()
                for key, val in dictOfValues.iteritems():
                    vocabulary.getVariableByID(key).setCurrentValue(val)

        if writingToken.isOk():
            # The value of the variable is simply the value we made.
            self.currentValue = writingToken.getValue()[savedIndex:writingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return AlternateVariable.TYPE

    def toString(self):
        """toString:
        """
        lgth = 0
        if self.children is not None:
            lgth = len(self.children)
        return _("[Alternate] {0} ({1})").format(AbstractVariable.toString(self), str(lgth))

    def isDefined(self, processingToken):
        """isDefined:
                If one child is defined the node is defined.
        """
        if self.children is not None:
            for child in self.getChildren():
                if child.isDefined(processingToken):
                    return True
        return False

    def read(self, readingToken):
        """read:
                Each child tries sequentially to read a part of the read value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug("[ {0} (Alternate): read access:".format(AbstractVariable.toString(self)))
        if self.getChildren() is not None:
            if self.isMutable():
                # mutable.
                self.shuffleChildren()
                self.readChildren(readingToken)

            else:
                # not mutable.
                self.readChildren(readingToken)

        else:
            # no child.
            self.log.debug("Write abort: the variable has no child.")
            readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken, self.currentValue)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                Each child tries sequentially to write its value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug("[ {0} (Alternate): write access:".format(AbstractVariable.toString(self)))
        if self.getChildren() is not None:
            if self.isMutable():
                # mutable.
                self.shuffleChildren()
                self.writeChildren(writingToken)

            else:
                # not mutable.
                self.writeChildren(writingToken)

        else:
            # no child.
            self.log.debug("Write abort: the variable has no child.")
            writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AlternateVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # Definition of children variables
        for child in self.children:
            child.toXML(xmlVariable, namespace)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads an alternate variable from an XML definition.
        """
        logging.debug("[ AlternateVariable: loadFromXML:")
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            result = AlternateVariable(xmlID, xmlName, xmlMutable, xmlLearnable, [])
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version, symbol)
                result.addChild(child)

            logging.debug("AlternateVariable: loadFromXML successes: {0} ]".format(result.toString()))
            return result
        logging.debug("AlternateVariable: loadFromXML fails")
        return None
