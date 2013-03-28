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
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class AbstractVariableProcessingToken():
    """AbstractVariableProcessingToken:
            A communication token used by variable when they are processed.
    """

    def __init__(self, negative, vocabulary, memory, value):
        """Constructor of AbstractVariableProcessingToken:

                @type negative: boolean
                @param negative: tells if we use the processed variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the processed variable.
                @type value: bitarray
                @param value: the current read value in binary format.
        """
        self.ok = True  # We consider that a communication token is always correct at construction.
        self.negative = negative
        self.vocabulary = vocabulary
        self.memory = memory
        self.value = value
        self.index = 0
        self.linkedValue = []  # A list of (id, value) that associates the contribution to the final value of every variable to its ID.

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def isOk(self):
        return self.ok

    def getNegative(self):
        return self.negative

    def getVocabulary(self):
        return self.vocabulary

    def getMemory(self):
        return self.memory

    def getValue(self):
        return self.value

    def getIndex(self):
        return self.index

    def getLinkedValue(self):
        return self.linkedValue

    def appendLinkedValue(self, value):
        self.linkedValue.append(value)

    def setOk(self, ok):
        logging.debug("The token's ok flag is set to {0}.".format(ok))
        self.ok = ok

    def setValue(self, value):
        self.value = value
