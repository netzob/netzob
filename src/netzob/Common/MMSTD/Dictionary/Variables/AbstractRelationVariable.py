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
from gettext import gettext as _
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class AbstractRelationVariable(AbstractVariable):
    """RelationVariable:
            A variable which points to an other variable and uses its value.
            Beware when using it, it can leads to obviously dangerous behavior.
    """

    def __init__(self, _id, name, mutable, random, pointedID):
        """Constructor of AbstractRelationVariable:

                @type pointedID: string
                @param pointedID: the id of the pointed variable.
        """
        AbstractVariable.__init__(self, _id, name, mutable, random, False)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractRelationVariable.py')
        self.pointedID = pointedID
        self.currentValue = None

    def compare(self, readingToken):
        """compare:
                The variable compares its value to the read value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        self.log.debug(_("- [ {0}: compare.").format(self.toString()))
        localValue = self.getCurrentValue(readingToken)
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
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), readingToken.toString()))

    def writeValue(self, writingToken):
        """writeValue:
                Write the variable value if it has one, else it returns the memorized value.
                Write this value in the writingToken.
        """
        self.log.debug(_("- [ {0}: writeValue.").format(self.toString()))
        value = self.getCurrentValue(writingToken)
        writingToken.appendValue(value)
        self.log.debug(_("Variable {0}: {1}. ] -").format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learn (starting at the "indice"-th character) value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def retrieveValue(self, readingToken):
        """retrieveValue:
                Retrieve a value according to the pointed variable's own value and attribute it to the variable.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'computeValue'."))

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def computeValue(self, writingToken):
        """computeValue:
                Compute a value according to the pointed variable's own value and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
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
        pointedVariable = self.getPointedVariable()
        if pointedVariable is None:
            self.log.debug("No pointed variable.")
            return False
        else:
            return pointedVariable.isDefined()

    def restore(self, processingToken):
        """restore:
        """
        pointedVariable = self.getPointedVariable()
        if pointedVariable is None:
            self.log.debug("No pointed variable.")
            return False
        else:
            return pointedVariable.restore(processingToken)

    def getDictOfValues(self, processingToken):
        """getDictOfValues:
        """
        pointedVariable = self.getPointedVariable()
        if pointedVariable is None:
            self.log.debug("No pointed variable.")
            return False
        else:
            return pointedVariable.getDictOfValues(processingToken)

    def read(self, readingToken):
        """read:
                The relation variable tries to compare/learn the read value.
        """
        self.log.debug(_("[ {0} (relation): read access:").format(AbstractVariable.toString(self)))
        if self.isMutable():
            if not self.isChecked():
                self.retrieveValue(readingToken)
                self.learn(readingToken)
            else:  # We compare the value previously learned (during the checking access) to the one that should have been learned.
                self.log.debug(_("The variable is already checked, so we compare the value formerly learned to the proposed one."))
                self.compare(readingToken)

        else:
            if self.isDefined(readingToken):
                # not mutable and defined
                if not self.isChecked():
                    self.retrieveValue(readingToken)
                self.compare(readingToken)

            else:
                # not mutable and not defined
                self.log.debug(_("Read abort: the variable is neither defined, nor mutable."))
                readingToken.setOk(False)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The relation variable returns a computed or a generated value.
        """
        self.log.debug(_("[ {0} (relation): write access:").format(AbstractVariable.toString(self)))
        if self.isRandom():
            if not self.isChecked():  # A checked variable does not modify its value.
                self.generate(writingToken)
            self.writeValue(writingToken)

        else:
            if self.isDefined(writingToken):
                # not random and defined
                if not self.isChecked():  # A checked variable does not modify its value.
                    self.computeValue(writingToken)
                self.writeValue(writingToken)

            else:
                # not random and not defined
                self.log.debug(_("Write abort: the variable is neither defined, nor random."))
                writingToken.setOk(False)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getPointedID(self):
        return self.pointedID

    def getPointedVariable(self, vocabulary):
        variable = vocabulary.getVariableByID(self.pointedID)
        return self.getPointedVariable(variable)

    def getType(self):
        return self.type

    def getCurrentValue(self):
        return self.currentValue

    def setPointedID(self, pointedID):
        self.setPointedID(pointedID)

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue
