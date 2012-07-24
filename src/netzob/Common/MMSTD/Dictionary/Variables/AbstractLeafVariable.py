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

    def __init__(self, id, name, mutable, random):
        """Constructor of AbstractLeafVariable:
        """
        AbstractVariable.__init__(self, id, name, mutable, random)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractLeafVariable.py')
        self.defined = True

#+---------------------------------------------------------------------------+
#| Visitor abstract subFunctions                                             |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def forget(self, processingToken):
        """forget:
                Removes the variable from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'forget'."))

    @abstractmethod
    def recall(self, processingToken):
        """recall:
                Recalls the variable from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'recall'."))

    @abstractmethod
    def memorize(self, processingToken):
        """memorize:
                Adds the variable to the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'memorize'."))

    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learns (starting at the "indice"-th character) value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def compare(self, readingToken):
        """compare:
                Compares (starting at the "indice"-th character) value to the current or a previously memorized value of variable.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'compare'."))

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generates a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def getValue(self, writingToken):
        """getValue:

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'getValue'."))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def read(self, readingToken):
        """read:
                The leaf element tries to compare/learn the read value.
        """
        self.log.debug(_("[ {0} (leaf): read access:").format(AbstractVariable.toString()))
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, readingToken)
                self.learn(self, readingToken)
                self.memorize(self, readingToken)

            else:
                # mutable and not defined
                self.learn(self, readingToken)
                self.memorize(self, readingToken)

        else:
            if self.defined:
                # not mutable and defined
                self.compare(self, readingToken)

            else:
                # not mutable and not defined
                readingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The leaf element return its value or a generate one.
        """
        self.log.debug(_("[ {0} (leaf): write access:").format(AbstractVariable.toString()))
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, writingToken)
                self.generate(self, writingToken)
                self.memorize(self, writingToken)
                valueToSend = self.getValue(self, writingToken)

            else:
                # mutable and not defined
                self.generate(self, writingToken)
                self.memorize(self, writingToken)
                valueToSend = self.getValue(self, writingToken)

        else:
            if self.defined:
                # not mutable and defined
                valueToSend = self.getValue(self, writingToken)

            else:
                # not mutable and not defined
                writingToken.setOk(False)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def isDefined(self):
        return self.defined

    def setDefined(self, defined):
        self.defined = defined
