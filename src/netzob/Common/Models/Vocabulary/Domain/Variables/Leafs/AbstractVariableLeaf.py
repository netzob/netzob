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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken


@NetzobLogger
class AbstractVariableLeaf(AbstractVariable):
    """Represents a leaf in the variable definition of a field.

    A leaf is a variable with no children. Most of of leaf variables
    are :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Data.Data` variables and
    :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Relations.AbstractRelation.AbstractRelation`.

    """

    def __init__(self, varType, name=None):
        super(AbstractVariableLeaf, self).__init__(varType, name=name)

    @typeCheck(VariableReadingToken)
    def read(self, readingToken):
        """Grants a reading access to the variable. The value of readingToken is read bit by bit.

        if the variable is
        - mutable & learnable & defined: forget, compareFormat, learn, memorize, read
        - mutable & learnable & !defined: compareFormat, learn, memorize, read

        - mutable & !learnable & defined: compareFormat
        - mutable & !learnable & !defined: compareFormat

        - !mutable & learnable & defined: compare
        - !mutable & learnable & !defined: compareFormat, learn, memorize

        - !mutable & !learnable & defined: compare
        - !mutable & !learnable & !defined: KO


        :param readingToken: a token which contains all critical information on this reading access.
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableReadingToken.VariableReadingToken`
        """
        self._logger.debug("[ Read access on {0}:".format(self))

        if self.mutable:
            if self.learnable:
                if self.isDefined(readingToken):
                    self._logger.debug("\t mutable, learnable, defined")
                    # mutable, learnable and defined.
                    self.compareFormat(readingToken)
                    if readingToken.Ok:
                        self.forget(readingToken)
                        self.learn(readingToken)
                        self.memorize(readingToken)
                        tmpSize = len(readingToken.value[readingToken.index:])
                        readingToken.incrementIndex(tmpSize)
                else:
                    self._logger.debug("\t mutable, learnable, !defined")
                    # mutable, learnable and not defined.
                    self.compareFormat(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)
                    tmpSize = len(readingToken.value[readingToken.index:])
                    readingToken.incrementIndex(tmpSize)

            else:
                if self.isDefined(readingToken):
                    self._logger.debug("\t mutable, !learnable, defined")
                    # mutable, not learnable and defined.
                    self.compareFormat(readingToken)
                else:
                    self._logger.debug("\t mutable, !learnable, !defined")
                    # mutable, learnable and not defined.
                    self.compareFormat(readingToken)
        else:
            if self.learnable:
                if self.isDefined(readingToken):
                    self._logger.debug("\t !mutable, learnable, defined")
                    # not mutable, learnable and defined.
                    self.compare(readingToken)

                else:
                    self._logger.debug("\t !mutable, learnable, defined")
                    # not mutable, learnable and not defined.
                    self.compareFormat(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)

            else:
                if self.isDefined(readingToken):
                    self._logger.debug("\t !mutable, !learnable, defined")
                    # not mutable, not learnable and defined.
                    self.compare(readingToken)

                else:
                    self._logger.debug("\t !mutable, !learnable, !defined")
                    # not mutable, not learnable and not defined.
                    self._logger.debug("Read abort: the variable is neither defined, nor mutable.")
                    readingToken.Ok = False

        # Variable notification
        if readingToken.Ok:
            self.notifyBoundedVariables("read", readingToken, self.getValue(readingToken))

        self._logger.debug("\t {0}. ]".format(readingToken))

    @typeCheck(VariableWritingToken)
    def write(self, writingToken):
        """Grants a writing access to the variable.
        A value is written according to encountered node variable rules and is stored in the provided writingToken.

        mutable & learnable & defined: mutate, writeValue
        mutable & learnable & !defined: generate, memorize, writeValue

        mutable & !learnable & defined: generate, writeValue
        mutable & !learnable & !defined: generate, writeValue

        !mutable & learnable & defined: writeValue
        !mutable & learnable & !defined: generate, memorize, writeValue

        !mutable & !learnable & defined: writeValue
        !mutable & !learnable & !defined: KO


        :param writingToken: a token which contains all critical information on this writing access.
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingToken.VariableWritingToken.VariableWritingToken`
        """
        self._logger.debug("[ {0} (leaf): write access:".format(self))
        self.tokenChoppedIndexes = []  # New write access => new final value and new reference to it.
        if self.mutable:
            if self.learnable:
                if self.isDefined(writingToken):
                    # mutable, learnable and defined.
                    self.mutate(writingToken)
                    self.writeValue(writingToken)

                else:
                    # mutable, learnable and not defined.
                    self.generate(writingToken)
                    self.memorize(writingToken)
                    self.writeValue(writingToken)
            else:
                if self.isDefined(writingToken):
                    # mutable, not learnable, defined.
                    self.generate(writingToken)
                    self.writeValue(writingToken)

                else:
                    # mutable, not learnable, not defined.
                    self.generate(writingToken)
                    self.writeValue(writingToken)

        else:
            if self.learnable:
                if self.isDefined(writingToken):
                    # not mutable, learnable and defined.
                    self.writeValue(writingToken)

                else:
                    # not mutable, learnable and not defined.
                    self.generate(writingToken)
                    self.memorize(writingToken)
                    self.writeValue(writingToken)

            else:
                if self.isDefined(writingToken):
                    # not mutable, not learnable and defined.
                    self.writeValue(writingToken)

                else:
                    # not mutable, not learnable and not defined.
                    self._logger.debug("Write abort: the variable is neither defined, nor mutable.")
                    writingToken.Ok = False

        # Variable notification
        #if writingToken.Ok:
        #    self.notifyBoundedVariables("write", writingToken)

        self._logger.debug("\t: {0}. ]".format(writingToken))
