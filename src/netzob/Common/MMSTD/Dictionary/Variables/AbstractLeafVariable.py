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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import AbstractVariable


class AbstractLeafVariable(AbstractVariable):
    """AbstractLeafVariable:
            An abstract variable defined in a dictionary which is a leaf (variable containing data for example) in the global variable tree.
    """

    def __init__(self, _id, name, mutable, learnable):
        """Constructor of AbstractLeafVariable:
        """
        AbstractVariable.__init__(self, _id, name, mutable, learnable, False)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractLeafVariable.py')

#+---------------------------------------------------------------------------+
#| Visitor abstract subFunctions                                             |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def forget(self, processingToken):
        """forget:
                Remove the variable from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'forget'.")

    @abstractmethod
    def recall(self, processingToken):
        """recall:
                Recall the variable value from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'recall'.")

    @abstractmethod
    def memorize(self, processingToken):
        """memorize:
                Add the variable to the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'memorize'.")

    @abstractmethod
    def compareFormat(self, readingToken):
        """compareFormat:
                Compare (starting at the "indice"-th character) the readingToken's value format to the variable type format.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'compareFormat'.")

    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learn (starting at the "indice"-th character) the readingToken's value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'learn'.")

    @abstractmethod
    def compare(self, readingToken):
        """compare:
                Compare (starting at the "indice"-th character) the readingToken's value to the current or a previously memorized value of variable.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'compare'.")

    @abstractmethod
    def mutate(self, writingToken):
        """mutate:
                Mutate the memorized value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'generate'.")

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'generate'.")

    @abstractmethod
    def writeValue(self, writingToken):
        """writeValue:
                Write the local value of a leaf variable in the writing token.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'writeValue'.")

    @abstractmethod
    def getValue(self, processingToken):
        """getValue:
                Return the current value if it has one, a memorized value in other cases.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'writeValue'.")

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def read(self, readingToken):
        """read:
                The leaf element tries to compare/learn the read value.
        """
        self.log.debug("[ {0} (leaf): read access:".format(AbstractVariable.toString(self)))
        if self.isMutable():
            if self.isLearnable():
                if self.isDefined(readingToken):
                    # mutable, learnable and defined.
                    self.forget(readingToken)
                    self.compareFormat(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)

                else:
                    # mutable, learnable and not defined.
                    self.compareFormat(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)

            else:
                if self.isDefined(readingToken):
                    # mutable, not learnable and defined.
                    self.compareFormat(readingToken)

                else:
                    # mutable, learnable and not defined.
                    self.compareFormat(readingToken)

        else:
            if self.isLearnable():
                if self.isDefined(readingToken):
                    # not mutable, learnable and defined.
                    self.compare(readingToken)

                else:
                    # not mutable, learnable and not defined.
                    self.compareFormat(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)

            else:
                if self.isDefined(readingToken):
                    # not mutable, not learnable and defined.
                    self.compare(readingToken)

                else:
                    # not mutable, not learnable and not defined.
                    self.log.debug("Read abort: the variable is neither defined, nor mutable.")
                    readingToken.setOk(False)

        # Variable notification
        if readingToken.isOk():
            self.notifyBoundedVariables("read", readingToken, self.getValue(readingToken))

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The leaf element returns its value or a generated one.
        """
        self.log.debug("[ {0} (leaf): write access:".format(AbstractVariable.toString(self)))
        if self.isMutable():
            if self.isLearnable():
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
            if self.isLearnable():
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
                    self.log.debug("Write abort: the variable is neither defined, nor mutable.")
                    writingToken.setOk(False)

        # Variable notification
        if writingToken.isOk():
            self.notifyBoundedVariables("write", writingToken)

        self.log.debug("Variable {0}: {1}. ]".format(self.getName(), writingToken.toString()))
