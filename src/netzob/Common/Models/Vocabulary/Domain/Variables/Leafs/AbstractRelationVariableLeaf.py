#-*- coding: utf-8 -*-

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
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken


@NetzobLogger
class AbstractRelationVariableLeaf(AbstractVariableLeaf):
    """Represents a relation relation between variables, one being updated with the others.

    """

    def __init__(self, varType, name=None):
        super(AbstractRelationVariableLeaf, self).__init__(varType, name)

    @typeCheck(AbstractVariableProcessingToken)
    def getDictOfValues(self, processingToken):
        """ Simply return a dict that contains the value associated to the ID of the variable.
        """
        if processingToken is None:
            raise TypeError("Processing token cannot be none")
        dictOfValues = dict()
        dictOfValues[self.id] = self.getValue(processingToken)
        return dictOfValues

    @abc.abstractmethod
    def getValue(processingToken):
        raise NotImplementedError("getValues is not implemented in at least one relation type.")

    def writeValue(self, writingToken):
        self._logger.debug("- [ {0}: writeValue.".format(self))
        writingToken.write(self, self.getValue(writingToken))

        self._logger.debug("WritingToken linkedValue: {0}".format(writingToken.linkedValues))

    @typeCheck(VariableReadingToken)
    def compare(self, readingToken):
        """The variable compares its value to the read value.
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: compare.".format(self))
        localValue = self.getValue(readingToken)
        tmp = readingToken.value[readingToken.index:]

        self._logger.debug("Compare {0} against {1}".format(localValue, tmp))

        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self._logger.debug("Comparison successful.")
                readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + len(localValue))
                readingToken.incrementIndex(len(localValue))
                readingToken.Ok = True
            else:
                readingToken.Ok = False
                self._logger.debug("Comparison failed: wrong value.")
        else:
            readingToken.Ok = False
            self._logger.debug("Comparison failed: wrong size.")
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
