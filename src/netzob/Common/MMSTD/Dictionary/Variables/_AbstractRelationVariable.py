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
from abc import abstractmethod
from bitarray import bitarray
from gettext import gettext as _
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable


class AbstractRelationVariable(AbstractVariable):
    """RelationVariable:
            A variable which points to an other variable and uses its value.
            Beware when using it, it can leads to obviously dangerous behavior.
    """

    def __init__(self, _id, name, mutable, learnable, pointedID, symbol):
        """Constructor of AbstractRelationVariable:

                @type pointedID: string
                @param pointedID: the pointed variable's ID.
        """
        AbstractVariable.__init__(self, _id, name, mutable, learnable, False)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractRelationVariable.py')
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

    def randomizePointedVariable(self, writingToken):
        """randomizePointedVariable
                Replace the pointed variable by another one, randomly found in the global tree.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
        self.log.debug("- [ {0}: randomizePointedVariable.".format(self.toString()))
        variables = writingToken.getVocabulary().getVariables()
        i = random.randint(0, len(variables))
        self.pointedVariable = variables[i]
        self.pointedID = self.pointedVariable.getID()
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

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
            choppedValue = self.getChoppedValue(processingToken)
            currentValue = bitarray('')
            for choppy in choppedValue:
                currentValue += choppy
            self.currentValue = self.computeValue(currentValue)

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

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug("- [ {0}: writeValue.".format(self.toString()))
        writingToken.write(self, self.currentValue)
        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def compareFormat(self, readingToken):
        """compare:
                The variable compares the format of its value to the format of the read value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'compareFormat'.")

    @abstractmethod
    def lightRead(self, readingToken):
        """lightRead:
                A read which is confirmed and completed by a notified read.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'lightRead'.")

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'generate'.")

    @abstractmethod
    def computeValue(self, value):
        """computeValue:
                Compute the value of the relation variable from the given value..

                @type value: bitarray
                @param value: the pointed variable's value.
                @rtype: bitarray
                @return: the computed value.
        """
        raise NotImplementedError("The current variable does not implement 'computeValue'.")

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
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
            return False
        else:
            return self.getPointedVariable().getDictOfValues(processingToken)

    def read(self, readingToken):
        """read:
                The relation variable tries to compare/learn the read value.
        """
        self.log.debug("[ {0} (relation): read access:".format(AbstractVariable.toString(self)))
        self.directPointer = self.findDirectPointer()

        if self.isMutable():
            self.compareFormat(readingToken)

        else:
            if self.isDefined(readingToken):
                # not mutable and defined
                if self.directPointer:
                    # We directly retrieve and compare the value.
                    self.retrieveValue(readingToken)
                    self.compare(readingToken)
                else:
                    # We make a light comparison.
                    self.lightRead(readingToken)
                    # We will verify at notification time.
                    self.bindValue(readingToken)

            else:
                # not mutable and not defined
                self.log.debug("Read abort: the variable is neither defined, nor mutable.")
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

        if self.isMutable():
            # mutable
            self.randomizePointedVariable(writingToken)
            self.directPointer = self.findDirectPointer()
            if not self.directPointer:
                # We will write the real value at notification time. (An awaiting value is written though.)
                self.bindValue(writingToken)

            # We directly retrieve and write the actual value (which would be deprecated and replaced if the variable is directPointer).
            self.retrieveValue(writingToken)
            self.writeValue(writingToken)

        else:
            if self.isDefined(writingToken):
                # not mutable and defined
                if not self.directPointer:
                    # We will write the real value at notification time. (An awaiting value is written though.)
                    self.bindValue(writingToken)

                # We directly retrieve and write the actual value (which would be deprecated and replaced if the variable is directPointer).
                self.retrieveValue(writingToken)
                self.writeValue(writingToken)
            else:
                # not mutable and not defined
                self.log.debug("Write abort: the variable is neither defined, nor random.")
                writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Notified function                                                         |
#+---------------------------------------------------------------------------+
    def notifiedRead(self, readingToken, pointedValue):
        """notifiedRead:
                A read access called by a notification of the pointed variable (when it has finished its own treatment).
                It checks that the new value complies with the reading token value at this very position.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("[ {0} (relation): read access:".format(AbstractVariable.toString(self)))
        if not self.isMutable():
            if self.isDefined(readingToken):
                # not mutable and defined
                self.notifiedCompare(readingToken, pointedValue)

            else:
                # not mutable and not defined
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
        if self.isMutable():
            # mutable
            self.notifiedWriteValue(writingToken)

        else:
            if self.isDefined(writingToken):
                # not mutable and defined
                self.notifiedWriteValue(writingToken)
            else:
                # not mutable and not defined
                self.log.debug("Write abort: the variable is neither defined, nor random.")
                writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))

    def notifiedWriteValue(self, writingToken):
        """notifiedWriteValue:
                We update each piece of value the current variable has written with the new piece of values given by the pointed variable.
                Beware : if the pointed variable points to an aggregate or a repeat variable they may have plenty of different new piece of values.
                And if the pointed variable is in a repeatVariable, each of the piece of values are written several times.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: notifiedWriteValue.".format(self.toString()))

        for linkedValue in writingToken.getLinkedValue():
            if linkedValue[0] == self.getID():
                linkedValue[1] = self.currentValue
        writingToken.updateValue()

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), writingToken.toString()))

    def notifiedCompare(self, readingToken, pointedValue):
        """notifiedCompare:
                We compare the reading token value to the new value of the current variable on the proper segment.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug("- [ {0}: notifiedCompare.".format(self.toString()))

        for linkedValue in readingToken.getLinkedValue():
            if linkedValue[0] == self.getID():
                # We compare the pointed value to the value the current variable wrote in memory.
                if linkedValue[1] != self.computeValue(pointedValue):
                    readingToken.setOk(False)
                    break

        self.log.debug("Variable {0}: {1}. ] -".format(self.getName(), readingToken.toString()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getType(self):
        return self.type

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

    def isDirectPointer(self):
        return self.directPointer

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue
