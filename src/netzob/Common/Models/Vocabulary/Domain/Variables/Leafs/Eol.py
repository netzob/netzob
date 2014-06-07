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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken


@NetzobLogger
class Eol(AbstractVariableLeaf):
    """Represents the end of the current data.
    This domain verification only returns True if no more data is available to parse.
    on the other hand, nothing happen when writing.
    """

    def __init__(self):
        """The constructor."""
        super(Eol, self).__init__(self.__class__.__name__)

    def __key(self):
        return (self.dataType, self.currentValue, self.learnable, self.mutable)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @typeCheck(AbstractVariableProcessingToken)
    def isDefined(self, processingToken):
        return True

    @typeCheck(AbstractVariableProcessingToken)
    def getValue(self, processingToken):
        return bitarray()

    @typeCheck(AbstractVariableProcessingToken)
    def getDictOfValues(self, processingToken):
        """ Simply return a dict that contains the value associated to the ID of the variable.
        """
        dictOfValues = dict()
        dictOfValues[self.id] = self.getValue(processingToken)
        return dictOfValues

    #+---------------------------------------------------------------------------+
    #| Functions inherited from AbstractLeafVariable                             |
    #+---------------------------------------------------------------------------+
    @typeCheck(AbstractVariableProcessingToken)
    def forget(self, processingToken):
        pass

    @typeCheck(AbstractVariableProcessingToken)
    def recall(self, processingToken):
        pass

    @typeCheck(AbstractVariableProcessingToken)
    def memorize(self, processingToken):
        pass

    @typeCheck(VariableReadingToken)
    def compareFormat(self, readingToken):
        """The variable checks if its format complies with the read value's format.

        It only returns True if no more data is available for parsing.
        """

        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: compareFormat".format(self))

        # Retrieve the value to check
        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("Cannot compareFormat because not value is linked with the current data")

        data = readingToken.getValueForVariable(self)

        readingToken.Ok = len(data) == 0
        if readingToken.Ok:
            readingToken.setValueForVariable(self, bitarray())

        self._logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableReadingToken)
    def learn(self, readingToken):
        pass

    @typeCheck(VariableReadingToken)
    def compare(self, readingToken):
        """The variable compares its value to the read value.
        It returns True if no data is available.

        """

        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        data = readingToken.getValueForVariable(self)

        readingToken.Ok = len(data) == 0
        if readingToken.Ok:
            readingToken.setValueForVariable(self, bitarray())

    @typeCheck(VariableWritingToken)
    def mutate(self, writingToken):
        pass

    @typeCheck(VariableWritingToken)
    def generate(self, writingToken):
        pass

    def writeValue(self, writingToken):
        pass

    @typeCheck(AbstractVariableProcessingToken)
    def restore(self, processingToken):
        pass

    def buildRegex(self):
        pass

    def __str__(self):
        """The str method, mostly for debugging purpose."""
        return "EOL"
