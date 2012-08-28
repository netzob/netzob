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
        self.directPointer = self.findDirectPointer()
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
        foundSelf = False
        for element in treeElements:
            if not foundSelf and element.getID() == self.getID():
                foundSelf = True
            if element.getID() == self.pointedID:
                if not foundSelf:
                    return True
                else:
                    return False
        return True

    def randomizePointedVariable(self, writingToken):
        """randomizePointedVariable
                Replace the pointed variable by another one, randomly found in the global tree.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
        self.log.debug(_("- [ {0}: randomizePointedVariable.").format(self.toString()))
        variables = writingToken.getVocabulary().getVariables()
        i = random.randint(0, len(variables))
        self.pointedVariable = variables[i]
        self.pointedID = self.pointedVariable.getID()
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

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
        self.log.debug(_("- {0}: retrieveValue.").format(self.toString()))
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
        self.log.debug(_("- [ {0}: compare.").format(self.toString()))
        localValue = self.currentValue
        tmp = readingToken.getValue()[readingToken.getIndex():]
        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self.log.debug(_("Comparison successful."))
                readingToken.incrementIndex(len(localValue))
                readingToken.setOk(True)
            else:
                readingToken.setOk(False)
                self.log.debug(_("Comparison failed: wrong value."))
        else:
            readingToken.setOk(False)
            self.log.debug(_("Comparison failed: wrong size."))

        if readingToken.isOk():
            readingToken.getChoppedValue().append(localValue)

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug(_("- [ {0}: writeValue.").format(self.toString()))

        for choppy in self.getChoppedValue(writingToken):
            self.addTokenChoppedIndexes(len(writingToken.getChoppedValue()))
            writingToken.getChoppedValue().append(choppy)
        writingToken.updateValue()

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

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
        raise NotImplementedError(_("The current variable does not implement 'compareFormat'."))

    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learn (starting at the "indice"-th character) value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def computeValue(self, value):
        """computeValue:
                Compute the value of the relation variable from the given value..

                @type value: bitarray
                @param value: the pointed variable's value.
                @rtype: bitarray
                @return: the computed value.
        """
        raise NotImplementedError(_("The current variable does not implement 'computeValue'."))

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

    def getChoppedValue(self, processingToken):
        """getChoppedValue:
                Return the pointedVariable's chopped value.
        """
        if self.getPointedVariable() is None:
            self.log.debug("No pointed variable.")
            return None
        else:
            return self.getPointedVariable().getChoppedValue(processingToken)

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
        self.log.debug(_("[ {0} (relation): read access:").format(AbstractVariable.toString(self)))
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
                    # We will compare at notification time.
                    self.bindValue(readingToken)

            else:
                # not mutable and not defined
                self.log.debug(_("Read abort: the variable is neither defined, nor mutable."))
                readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The relation variable returns a computed or a generated value.
        """
        self.log.debug(_("[ {0} (relation): write access:").format(AbstractVariable.toString(self)))
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
                self.log.debug(_("Write abort: the variable is neither defined, nor random."))
                writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Notified function                                                         |
#+---------------------------------------------------------------------------+
    def notifiedRead(self, readingToken):
        """notifiedRead:
                A read access called by a notification of the pointed variable (when it has finished its own treatment).
                It checks that the new value complies with the reading token value at this very position.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("[ {0} (relation): read access:").format(AbstractVariable.toString(self)))
        if not self.isMutable():
            if self.isDefined(readingToken):
                # not mutable and defined
                self.notifiedCompare(readingToken)

            else:
                # not mutable and not defined
                self.log.debug(_("Read abort: the variable is neither defined, nor mutable."))
                readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def notifiedWrite(self, writingToken):
        """notify:
                A write access called by a notification of the pointed variable (when it has finished its own treatment).
                It updates the values this variable has written in the writingToken value.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("[ {0} (relation): notifiedWrite access:").format(AbstractVariable.toString(self)))
        if self.isMutable():
            # mutable
            self.notifiedWriteValue(writingToken)

        else:
            if self.isDefined(writingToken):
                # not mutable and defined
                self.notifiedWriteValue(writingToken)
            else:
                # not mutable and not defined
                self.log.debug(_("Write abort: the variable is neither defined, nor random."))
                writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

    def notifiedWriteValue(self, writingToken):
        """notifiedWriteValue:
                We update each piece of value the current variable has written with the new piece of values given by the pointed variable.
                Beware : if the pointed variable points to an aggregate or a repeat variable they may have plenty of different new piece of values.
                And if the pointed variable is in a repeatVariable, each of the piece of values are written several times.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: notifiedWriteValue.").format(self.toString()))
        choppedValue = self.getChoppedValue(writingToken)

        for i in len(self.getTokenChoppedIndexes()):
            # If the current variable is in a repeat variable, len(self.getTokenChoppedIndexes()) = k * len(choppedValue) with k natural integer.
            value = self.computeValue(choppedValue[i % len(choppedValue)])
            # We write down the actualized corresponding value in the proper segment of the writing token chopped value.
            writingToken.getChoppedValue()[self.getTokenChoppedIndexes()[i]] = value
        # We update the value.
        writingToken.updateValue()
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

    def notifiedCompare(self, readingToken):
        """notifiedCompare:
                We compare the reading token value to the new value of the current variable on the proper segment.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: notifiedCompare.").format(self.toString()))
        choppedValue = self.getChoppedValue(readingToken)

        # We retrieve the values.
        for i in len(self.getTokenChoppedIndexes()):
            value = self.computeValue(choppedValue[i % len(choppedValue)])
            if readingToken.getChoppedValue()[self.getTokenChoppedIndexes()[i]] != value:
                # One piece of value differs.
                readingToken.setOk(False)
                break

        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

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
