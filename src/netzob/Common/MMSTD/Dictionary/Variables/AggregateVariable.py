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
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
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
        self.log.debug(_("- [ {0}: sortChildrenToRead.").format(self.toString()))

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
                    orderedChildren.append(childrenLeft.pop(child))
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

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def readChildren(self, readingToken):
        """readChildren:
                Execute a read access sequentially on each child of the variable.
                If all child successes, then it returns OK, else it returns NOK and restores the former value for each child.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: readChildren.").format(self.toString()))

        # Computing memory, contains all values before the start of the computation. So, if an error occured, we can restore the former and correct values.
        dictOfValues = dict()
        savedIndex = readingToken.getIndex()
        # The children list is retrieved once for all, which protect from inner-loop modification.
        children = self.getChildren()
        for child in children:
            # Memorize each child susceptible to be restored. One by one.
            dictOfValue = child.getDictOfValues(readingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val

            # Child execution.
            child.read(readingToken)
            if not readingToken.isOk():
                # If something went wrong and we can adapt, we learn to adapt.
                if self.isLearnable():
                    self.learn(child, readingToken)  # This may add new child to self.getChildren().
                break

        # If it has failed we restore every executed children and the index.
        if not readingToken.isOk():
            readingToken.setIndex(savedIndex)
            vocabulary = readingToken.getVocabulary()
            for key, val in dictOfValues.iteritems():
                child = vocabulary.getVariableByID(key)
                # We restore the current values.
                child.setCurrentValue(val)
                # We restore the cached values.
                child.restore(readingToken)

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def learn(self, child, readingToken):
        """learn:
                The aggregate variable learns the given value: it tries to add mutable children in order to comply with the given value.
                This learning can only extend the variable, not remove some children of it. If you want to potentially not take care of some variables, you can include them in 0-1 repeat variable.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the child we expected to find while reading the given value.
                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))

        childPosition = self.indexOfChild(child)
        tmp = readingToken.getValue()[readingToken.getIndex():]
        # The list of all leaf variable of the current symbol.
        leafList = readingToken.getRootVariable().getLeafProgeny()

        # We find the index of the current variable among all leaf variable.
        currentVarIndex = 0
        for var in leafList:
            if var.getID() == child.getID():
                break
            currentVarIndex += 1

        # We find the first static right brother.
        staticVar = None
        # Sum of mutable right brother sizes until the first static one:
        maxBrotherSize = 0
        # We take into account only the maximum number of bits of variables because the parser behaves greedily.
        staticVarIndex = currentVarIndex
        for staticVar in leafList[currentVarIndex:]:  # Perhaps, child of potentially null repeat variable should not matter.
            if not staticVar.isMutable() and staticVar.isDefined():
                break
            else:
                staticVarIndex += 1
                # We increment the dynamic brother size.
                maxBrotherSize += staticVar.getType().getMaxBits()

        found = False
        if staticVar is not None:
            # We search the child variable further
            currentVarPos = 0
            for currentVarPos in range(len(tmp) - len(staticVar.getValue())):
                if tmp[currentVarPos:currentVarPos + len(child.getValue())] == child.getValue():
                    found = True
                    break

        # We found the current variable further in the message (but before the first next static variable)
        if found:
            # We insert a new variable (defined by the value between the expected and the real position of the current variable) under a 0-1 repeat variable.
            insValue = tmp[:len(tmp) - maxBrotherSize]
            insVariable = DataVariable(uuid.uuid4(), "Learned Inserted Variable", True, True, BinaryType(True, len(insValue), len(insValue)), insValue.to01())
            repeatVariable = RepeatVariable(uuid.uuid4(), "Learned Option Variable", False, True, self, 0, 1)
            repeatVariable.add(insVariable)
            self.insertChild(childPosition, repeatVariable)

            # Memorize the newly created variable so as to restore them in case of problem
            #dictOfValue = repeatVariable.getDictOfValues(readingToken)
            #for key, val in dictOfValue.iteritems():
            #    dictOfValues[key] = val

            # We execute a read access on both variables.
            repeatVariable.read(readingToken)
            child.read(readingToken)
        else:
            # We found an other value which could replace the current variable's value. So we put both in an alternate.
            insValue = tmp[:(len(tmp) - maxBrotherSize)]
            insVariable = DataVariable(uuid.uuid4(), "Learned Inserted Variable", True, True, BinaryType(True, len(insValue), len(insValue)), insValue.to01())

            alternateVariable = AlternateVariable(uuid.uuid4(), "Learned Alternate Variable", False, True, self, 0, 1)
            self.addChild(alternateVariable)
            alternateVariable.addChild(child)
            alternateVariable.addChild(insVariable)  # We add the inserted variable at the end, so it may be choose in last.

            # Memorize the newly created variable so as to restore them in case of problem
            #dictOfValue = alternateVariable.getDictOfValues(readingToken)
            #for key, val in dictOfValue.iteritems():
            #    dictOfValues[key] = val

            # We execute a read access on the inserted variable.
            insVariable.read(readingToken)

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def writeChildren(self, writingToken):
        """writeChildren:
                Execute a write access sequentially on each child of the variable.
                If all child successes, then it returns OK, else it returns NOK and restores the former value for each child.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: readChildren.").format(self.toString()))

        dictOfValues = dict()
        savedValue = writingToken.getValue()
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

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

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
        self.log.debug(_("[ {0} (Aggregate): read access:").format(AbstractVariable.toString(self)))
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
            self.log.debug(_("Write abort: the variable has no child."))
            readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                Each child tries sequentially to write its value.
                If one of them fails, the whole operation is cancelled.
        """
        self.log.debug(_("[ {0} (Aggregate): write access:").format(AbstractVariable.toString(self)))
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
            self.log.debug(_("Write abort: the variable has no child."))
            writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

    def trivialCompareFormat(self, readingToken):
        """trivialCompareFormat:
                Run recursively the format comparison on the children.
                If one of them fails, the treatment fails.
        """
        self.log.debug(_("[ {0} (Aggregate): trivialCompareFormat:").format(AbstractVariable.toString(self)))

        for child in self.children:
            # Child execution.
            child.trivialCompareFormat(readingToken)
            if not readingToken.isOk():
                break

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        self.log.debug(_("[ {0} (Aggregate): toXML:").format(AbstractVariable.toString(self)))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("learnable", str(self.isLearnable()))

        # Definition of children variables
        for child in self.getChildren():
            child.toXML(xmlVariable, namespace)
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an aggregate variable from an XML definition.
        """
        logging.debug(_("[ AggregateVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            result = AggregateVariable(xmlID, xmlName, xmlMutable, xmlLearnable, children)
            logging.debug(_("AggregateVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("AggregateVariable: loadFromXML fails"))
        return None
