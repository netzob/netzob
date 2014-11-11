#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Models.Types.BitArray import BitArray


@NetzobLogger
class AbstractRelationVariableLeaf(AbstractVariableLeaf):
    """Represents a relation relation between variables, one being updated with the others.

    """

    def __init__(self, varType, fieldDependencies=None, name=None):
        super(AbstractRelationVariableLeaf, self).__init__(varType, name, learnable=False, mutable=True)
        if fieldDependencies is None:
            fieldDependencies = []
        self.fieldDependencies = fieldDependencies

    def isDefined(self, processingToken):
        """Tells if the variable is defined (i.e. has a value for a leaf, enough leaf have values for a node...)

        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken
        :param processingToken: a token which contains all critical information on this access.
        :rtype: boolean
        :return: True if the variable is defined.
        """
        ready = True
        for dep in self.fieldDependencies:
            if not processingToken.isValueForVariableAvailable(dep.domain):
                self._logger.debug("Relation dependencies {0} not ready!".format(dep.domain))
                ready = False
                break
            else:
                self._logger.debug("Relation dependencies {0} ready!".format(dep.domain))
        return ready

    @abc.abstractmethod
    def getValue(processingToken):
        raise NotImplementedError("getValues is not implemented in at least one relation type.")

    def writeValue(self, writingToken):
        self._logger.debug("- [ {0}: writeValue.".format(self))
        if not self.isDefined(writingToken):
            self._logger.debug("Relation field is not defined, more dependencies required")
            self.toBeComputed(writingToken)
        else:
            self._logger.debug("writing the value ({0}) in the writingToken for var {1}".format(self.getValue(writingToken), self))
            writingToken.setValueForVariable(self, self.getValue(writingToken))

    def generate(self, writingToken):
        if not self.isDefined(writingToken):
            self.toBeComputed(writingToken)
        else:
            self.currentValue = self.getValue(writingToken)

    def toBeComputed(self, processingToken):
        self._logger.debug("A relation cannot yet be computed, mark its dependencies...")
        for field in self.fieldDependencies:
            if not processingToken.isValueForVariableAvailable(field.domain):
                processingToken.addRelationCallback(field.domain, self, self.writeValue)

        #add temporary marker
        processingToken.setValueForVariable(self, TypeConverter.convert("TEMPORARY", ASCII, BitArray))

    @typeCheck(VariableReadingToken)
    def compare(self, readingToken):
        """The variable compares its value to the read value.
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: compare.".format(self))

        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("No value to read seems attached to this relation variable.")

        # retrieve the value to parse
        valueToParse = readingToken.getValueForVariable(self)

        # retrieve the expected value
        valueExpected = self.getValue(readingToken)

        self._logger.debug("Compare read value {0} against expected one {1}".format(valueToParse, valueExpected))

        if len(valueToParse) >= len(valueExpected):
            if valueToParse[:len(valueExpected)] == valueExpected:
                self._logger.debug("Comparison successful.")
                readingToken.Ok = True
            else:
                readingToken.Ok = False
                self._logger.debug("Comparison failed: wrong value.")
        else:
            readingToken.Ok = False
            self._logger.debug("Comparison failed: wrong size.")

        if readingToken.Ok:
            readingToken.setValueForVariable(self, valueExpected)
        self._logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    def notifiedWrite(self, writingToken):
        """notify:
                A write access called by a notification of the pointed variable (when it has finished its own treatment).
                It updates the values this variable has written in the writingToken value.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        self._logger.debug("[ {0} (relation): notifiedWrite access:".format(self))

        if self.isDefined(writingToken):
            # Compute the value
            value = self.getValue(writingToken)

            self._logger.debug("Notified Write : {0}".format(value))

            # replace the new value in the writing token
            writingToken.setValueForVariable(self, value)

        else:
            self._logger.debug("Write abort: the variable is neither defined, nor random.")
            writingToken.Ok = False

        # Variable notification
        if writingToken.Ok:
            self.notifyBoundedVariables("write", writingToken)

        self._logger.debug("Variable {0}: {1}. ]".format(self.name, writingToken))

    @property
    def fieldDependencies(self):
        """A list of fields that are required before computing the value of this relation

        :type: a list of :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        """
        return self.__fieldDependencies

    @fieldDependencies.setter
    @typeCheck(list)
    def fieldDependencies(self, fields):
        if fields is None:
            fields = []
        for field in fields:
            if not isinstance(field, AbstractField):
                raise TypeError("At least one specified field is not a Field.")
        self.__fieldDependencies = []
        for f in fields:
            self.__fieldDependencies.extend(f._getLeafFields())
