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
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable


class AggregateVariable(AbstractNodeVariable):
    """AggregateVariable:
            A data variable defined in a dictionary which is a logical and of several variables.
    """

    TYPE = "Aggregate Variable"

    def __init__(self, _id, name, mutable, learnable, children=[]):
        """Constructor of AggregateVariable:
        """
        AbstractNodeVariable.__init__(self, _id, name, mutable, learnable, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AggregateVariable.py')

    def sortChildrenToRead(self, readingToken):
        """sortChildrenToRead:
                Sort children of the variable in order to read the entry value.
                If an arrangement is found then it returns OK, else it returns NOK and restores the former value for each child.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: sortChildrenToRead.".format(self.toString()))

        # We save the state of the underlying variables and the readingToken index before the first treatment.
        globalDictOfValues = dict()
        globalSavedIndex = readingToken.getIndex()

        childrenLeft = self.getChildren()
        orderedChildren = []
        processing = True
        # The while loop stops if there is no child left, no entry data left or if an entire for loop was not successful.
        while childrenLeft is not None and readingToken.getIndex() < len(readingToken.getValue()) and processing:
            # Tell if an entire tour has not been successful. In such a case the while loop is terminated. (Instead of re-doing the same treatment again and again).
            processing = False

            # We search a suitable child for the value we have to read.
            for child in childrenLeft:
                # We save the state of the underlying variables and the readingToken between each treatment.
                localDictOfValues = dict()
                localSavedIndex = readingToken.getIndex()

                # Memorize each child susceptible to be restored. One by one.
                dictOfValue = child.getDictOfValues(readingToken)
                for key, val in dictOfValue.iteritems():
                    localDictOfValues[key] = val

                # Child execution.
                child.read(readingToken)
                if readingToken.isOk():
                    # We have found a suitable child, so we remove it from childrenLeft and add it (at the end, to respect the order) to the orderedChildren list.
                    orderedChildren.append(child)
                    childrenLeft.remove(child)
                    processing = True  # We want to continue the process on what is left.
                    break

                else:
                    # It was not a good candidate, so we restore the former values and continue.
                    readingToken.setIndex(localSavedIndex)
                    # We restore values for the child and its successors.
                    child.restore(readingToken)
                    vocabulary = readingToken.getVocabulary()
                    for key, val in localDictOfValues.iteritems():
                        vocabulary.getVariableByID(key).setCurrentValue(val)

        if not childrenLeft is None:
            # If something went wrong and we can adapt, we learn to adapt.
            if self.isLearnable():
                self.learn(child, readingToken)  # This may add new child to self.getChildren().
            else:
                readingToken.setOk(False)

        # If it has failed we restore every executed children and the index.
        if not readingToken.isOk():
            readingToken.setIndex(globalSavedIndex)
            vocabulary = readingToken.getVocabulary()
            for key, val in globalDictOfValues.iteritems():
                child = vocabulary.getVariableByID(key)
                # We restore the current values.
                child.setCurrentValue(val)
                # We restore the cached values.
                child.restore(readingToken)
        else:
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.getValue()[globalSavedIndex:readingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def readChildren(self, readingToken):
        """readChildren:
                Execute a read access sequentially on each child of the variable.
                If all child successes, then it returns OK, else it returns NOK and restores the former value for each child.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: readChildren.".format(self.toString()))

        # Computing memory, contains all values before the start of the computation. So, if an error occured, we can restore the former and correct values.
        dictOfValues = dict()
        savedIndex = readingToken.getIndex()
        self.currentValue = bitarray('')

        for child in self.getChildren():
            # Memorize each child susceptible to be restored. One by one.
            dictOfValue = child.getDictOfValues(readingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            # Child execution.
            child.read(readingToken)
            if not readingToken.isOk():
                break

        # If it has failed we restore every executed children and the index.
        if not readingToken.isOk():
            # If something went wrong and we can adapt, we learn to adapt.
            if self.isLearnable() and not self.isLearning():
                self.learn(child, readingToken)
            # If it is still not OK.
            if not readingToken.isOk():
                readingToken.setIndex(savedIndex)
                vocabulary = readingToken.getVocabulary()
                for key, val in dictOfValues.iteritems():
                    child = vocabulary.getVariableByID(key)
                    # We restore the current values.
                    child.setCurrentValue(val)
                    # We restore the cached values.
                    child.restore(readingToken)
        else:
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.getValue()[savedIndex:readingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def learn(self, child, readingToken):
        """learn:
                The aggregate variable learns the given value: it tries to add ONE mutable child before child in order to comply with the given value.
                We do not manage the learning of several children because we think that it is not the usecase and it inserts many errors.
                This learning can only extend the variable, not remove some children of it. If you want to potentially not take care of some variables, you can include them in 0-1 repeat variable.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the child we expected to find while reading the given value.
                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: learn.".format(self.toString()))
        savedIndex = readingToken.getIndex()

        childPosition = self.indexOfChild(child)
        repeatVariable = RepeatVariable(str(uuid.uuid4()), "Learned Option Variable", False, True, self, 0, 1)
        # We will insert the new child under a 0-1 repeat variable to potentially not take care of it, just before the position of the problematic child.
        self.insertChild(childPosition, repeatVariable)
        valueToBeRead = readingToken.getValue()[readingToken.getIndex():]
        for index in len(valueToBeRead):
            tmpValue = valueToBeRead[:index]
            tmpChild = DataVariable(str(uuid.uuid4()), "Learned Inserted Variable", True, True, BinaryType(True, len(tmpValue), len(tmpValue)), tmpValue.to01())
            repeatVariable.add(tmpChild)

            # We read this new variable in a learning context.
            self.setLearning(True)
            self.read(readingToken)
            # If this read access works, we learn the proper variable.
            if readingToken.isOk():
                break
            else:
                # We remove the just added child.
                repeatVariable.removeChild(tmpChild)

        # We did not found, so we restore and give up.
        if not readingToken.isOk():
            self.removeChild(repeatVariable)
            readingToken.setIndex(savedIndex)
        else:
            # The value of the variable is simply the value we 'ate'.
            self.currentValue = readingToken.getValue()[savedIndex:readingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

    def writeChildren(self, writingToken):
        """writeChildren:
                Execute a write access sequentially on each child of the variable.
                If all child successes, then it returns OK, else it returns NOK and restores the former value for each child.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: readChildren.".format(self.toString()))

        dictOfValues = dict()
        savedValue = writingToken.getValue()
        savedIndex = writingToken.getIndex()
        for child in self.getChildren():
            # Memorize each child susceptible to be restored. One by one.
            dictOfValue = child.getDictOfValues(writingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            # Child execution.
            child.write(writingToken)
            if not writingToken.isOk():
                break

        # If it has failed we restore every executed children and the value.
        if not writingToken.isOk():
            writingToken.setValue(savedValue)
            vocabulary = writingToken.getVocabulary()
            for key, val in dictOfValues.iteritems():
                child = vocabulary.getVariableByID(key)
                # We restore the current values.
                child.setCurrentValue(val)
                # We restore the cached values.
                child.restore(writingToken)
        else:
            # The value of the variable is simply the value we made.
            self.currentValue = writingToken.getValue()[savedIndex:writingToken.getIndex()]

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return AggregateVariable.TYPE

    def toString(self):
        """toString:
        """
        lgth = 0
        if self.getChildren() is not None:
            lgth = len(self.getChildren())
        return _("[Aggregate] {0} ({1})").format(AbstractVariable.toString(self), str(lgth))

    def isDefined(self, processingToken):
        """isDefined:
                If one child is not defined the node is not defined.
        """
        if self.children is not None:
            for child in self.getChildren():
                if not child.isDefined(processingToken):
                    return False
            return True
        else:
            return False

    def read(self, readingToken):
        """read:
                Each child tries sequentially to read a part of the read value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug("[ {0} (Aggregate): read access:".format(AbstractVariable.toString(self)))
        if self.getChildren() is not None:
            if self.isMutable():
                # mutable.
                self.sortChildrenToRead(readingToken)
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
        self.log.debug("[ {0} (Aggregate): write access:".format(AbstractVariable.toString(self)))
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
        self.log.debug("[ {0} (Aggregate): toXML:".format(AbstractVariable.toString(self)))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # Definition of children variables
        for child in self.getChildren():
            child.toXML(xmlVariable, namespace)
        self.log.debug("Variable {0}. ]".format(self.getName()))

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads an aggregate variable from an XML definition.
        """
        logging.debug("[ AggregateVariable: loadFromXML:")
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            result = AggregateVariable(xmlID, xmlName, xmlMutable, xmlLearnable, [])
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version, symbol)
                result.addChild(child)
            logging.debug("AggregateVariable: loadFromXML successes: {0} ]".format(result.toString()))
            return result
        logging.debug("AggregateVariable: loadFromXML fails")
        return None
