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
from netzob.Common.MMSTD.Dictionary.VariableManagementToken import VariableManagementToken


class AbstractVariable:
    """AbstractVariable:
            An abstract variable defined in a dictionary.
    """

    def __init__(self, id, name):
        """Constructor of AbstractVariable:

                @type id: string
                @param id: a unique identifying string.
                @type name: string
                @param name: the name of the variable being constructed.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.py')
        self.id = id
        self.name = name
        self.mutable = True  # TODO: implement mutability.
        self.defined = True  # TODO: implement definition.

#+---------------------------------------------------------------------------+
#| Visitor functions                                                         |
#+---------------------------------------------------------------------------+
    def read(self, readingToken):
        """read:
                Grants a reading access to the variable. The value of readingToken is read bit by bit.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this reading access.
        """
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, readingToken)
                self.learn(self, readingToken)
                self.memorize(self, readingTokenreadingToken)

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

    def write(self, writingToken):
        """write:
                Grants a writing access to the variable. A value is written according to encountered node variable rules. This value is stored in writingToken.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
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
        raise NotImplementedError(_("The current variable does not implement 'getValueToSend'."))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def isMutable(self):
        return self.mutable

    def isDefined(self):
        return self.defined

    def setId(self, id):
        self.id = id

    def getName(self, name):
        self.name = name

    def setMutable(self, mutable):
        self.mutable = mutable

    def setDefined(self, defined):
        self.defined = defined
