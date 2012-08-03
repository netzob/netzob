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

    def __init__(self, _id, name, mutable, random):
        """Constructor of AbstractLeafVariable:
        """
        AbstractVariable.__init__(self, _id, name, mutable, random, False)
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
        raise NotImplementedError(_("The current variable does not implement 'forget'."))

    @abstractmethod
    def recall(self, processingToken):
        """recall:
                Recall the variable value from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'recall'."))

    @abstractmethod
    def memorize(self, processingToken):
        """memorize:
                Add the variable to the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'memorize'."))

    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learn (starting at the "indice"-th character) value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def compare(self, readingToken):
        """compare:
                Compare (starting at the "indice"-th character) value to the current or a previously memorized value of variable.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'compare'."))

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def writeValue(self, writingToken):
        """writeValue:
                Write the local value of a leaf variable in the writing token.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'writeValue'."))

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def read(self, readingToken):
        """read:
                The leaf element tries to compare/learn the read value.
        """
        self.log.debug(_("[ {0} (leaf): read access:").format(AbstractVariable.toString(self)))
        if self.isMutable():
            if self.isDefined(readingToken):
                # mutable and defined
                if not self.isChecked():
                    self.forget(readingToken)
                    self.learn(readingToken)
                    self.memorize(readingToken)
                else:  # We compare the value previously learned (during the checking access) to the one that should have been learned.
                    self.log.debug(_("The variable is already checked, so we compare the value formerly learned to the proposed one."))
                    self.compare(readingToken)

            else:
                # mutable and not defined
                if not self.isChecked():
                    self.learn(readingToken)
                    self.memorize(readingToken)
                else:
                    self.log.debug(_("The variable is already checked, so we compare the value formerly learned to the proposed one."))
                    self.compare(readingToken)

        else:
            if self.isDefined(readingToken):
                # not mutable and defined
                self.compare(readingToken)

            else:
                # not mutable and not defined
                self.log.debug(_("Read abort: the variable is neither defined, nor mutable."))
                readingToken.setOk(False)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The leaf element returns its value or a generated one.
        """
        self.log.debug(_("[ {0} (leaf): write access:").format(AbstractVariable.toString(self)))
        if self.isRandom():
            if self.isDefined(writingToken):
                # random and defined
                if not self.isChecked():  # A checked variable does not modify its value.
                    self.forget(writingToken)
                    self.generate(writingToken)
                    self.memorize(writingToken)
                self.writeValue(writingToken)

            else:
                # random and not defined
                if not self.isChecked():
                    self.generate(writingToken)
                    self.memorize(writingToken)
                self.writeValue(writingToken)

        else:
            if self.isDefined(writingToken):
                # not random and defined
                self.writeValue(writingToken)

            else:
                # not random and not defined
                self.log.debug(_("Write abort: the variable is neither defined, nor random."))
                writingToken.setOk(False)

        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))
