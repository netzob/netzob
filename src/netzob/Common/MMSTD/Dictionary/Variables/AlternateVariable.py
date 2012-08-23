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
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable


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
        self.log.debug(_("[ {0} (Alternate): read access:").format(AbstractVariable.toString(self)))
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

        if self.isLearnable() and not readingToken.isOk():
            # If we dont not found a proper child but the node can learn, we learn the value.
            self.learn(child, readingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def writeChildren(self, writingToken):
        """write:
                Each child tries to write its value..
                If it fails, it restore it value and the next child try.
                It stops if one child successes.
        """
        self.log.debug(_("[ {0} (Alternate): write access:").format(AbstractVariable.toString(self)))

        savedValue = writingToken.getValue()
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

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

    def learn(self, child, readingToken):
        """learn:
                The alternate variable learns the given value and adds it at the end of its children.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the child we expected to find while reading the given value.
                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: learn.").format(self.toString()))

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

        # We add the value in the current variable's children.
        insValue = tmp[:(len(tmp) - maxBrotherSize)]
        insVariable = DataVariable(uuid.uuid4(), "Learned Inserted Variable", True, True, BinaryType(True, len(insValue), len(insValue)), insValue.to01())

        self.addChild(insVariable)
        # We execute a read access on the inserted variable.
        insVariable.read(readingToken)

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

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
        self.log.debug(_("[ {0} (Alternate): read access:").format(AbstractVariable.toString(self)))
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
        self.log.debug(_("[ {0} (Alternate): write access:").format(AbstractVariable.toString(self)))
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
                If one of them successes, the treatment successes.
        """
        self.log.debug(_("[ {0} (Alternate): trivialCompareFormat:").format(AbstractVariable.toString(self)))

        for child in self.children:
            # Child execution.
            child.trivialCompareFormat(readingToken)
            if readingToken.isOk():
                break

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

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
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads an alternate variable from an XML definition.
        """
        logging.debug(_("[ AlternateVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable") == "True"
            xmlLearnable = xmlRoot.get("learnable") == "True"

            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable"):
                child = AbstractVariable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            result = AlternateVariable(xmlID, xmlName, xmlMutable, xmlLearnable, children)
            logging.debug(_("AlternateVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("AlternateVariable: loadFromXML fails"))
        return None
