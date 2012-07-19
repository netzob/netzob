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
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.AbstractVariable.py')
        self.type = type
        self.id = id
        self.name = name
        self.mutable = True  # TODO: implement mutability.
        self.defined = True  # TODO: implement definition.

#+---------------------------------------------------------------------------+
#| Visitor functions                                                         |
#+---------------------------------------------------------------------------+
    def read(self, negative, vocabulary, memory):
        """read:
                Grant a reading access to the variable.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: netzob.Common.MMSTD.Dictionary.VariableManagementToken.VariableManagementToken
                @return: a token which gives all critical information on this reading access.
        """
        vmt = VariableManagementToken()
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, negative, vocabulary, memory)
                self.learn(self, value, indice, negative, vocabulary, vmt)
                self.memorize(self, negative, vocabulary, memory)

            else:
                # mutable and not defined
                self.learn(self, value, indice, negative, vocabulary, vmt)
                self.memorize(self, negative, vocabulary, memory)

        else:
            if self.defined:
                # not mutable and defined
                self.compare(self, value, indice, negative, vocabulary, memory, vmt)

            else:
                # not mutable and not defined
                vmt.setOk(False)
        return vmt
                
        
    def write(self, negative, vocabulary, memory):
        """write:
                Grant a writing access to the variable.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: bitarry
                @return: the value that has to be send/written.
        """
        valueToSend = None
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, negative, vocabulary, memory)
                self.generate(self, negative, vocabulary)
                self.memorize(self, negative, vocabulary, memory)
                valueToSend = self.getValue(self, negative, vocabulary, memory)

            else:
                # mutable and not defined
                self.generate(self, negative, vocabulary)
                self.memorize(self, negative, vocabulary, memory)
                valueToSend = self.getValue(self, negative, vocabulary, memory)

        else:
            if self.defined:
                # not mutable and defined
                valueToSend = self.getValue(self, negative, vocabulary, memory)

            else:
                # not mutable and not defined
                vmt.setOk(False)
        return valueToSend

#+---------------------------------------------------------------------------+
#| Visitor abstract subFunctions                                             |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def forget(self, negative, vocabulary, memory):
        """forget:
                Remove the variable from the memory cache.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
        """
        raise NotImplementedError(_("The current variable does not implement 'forget'."))

    @abstractmethod
    def memorize(self, negative, vocabulary, memory):
        """memorize:
                Add the variable to the memory cache.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
        """
        raise NotImplementedError(_("The current variable does not implement 'memorize'."))

    @abstractmethod
    def learn(self, value, indice, negative, vocabulary, vmt):
        """learn:
                Learn (starting at the "indice"-th character) value.

                @type value: bitarray.bitarray
                @param value: a bit array a subarray of which we compare to the current variable binary value.
                @type indice: integer
                @param indice: the starting point of comparison in value.
                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type vmt: netzob.Common.MMSTD.Dictionary.VariableManagementToken.VariableManagementToken
                @param vmt: a token which contains all critical information on the current operation.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def compare(self, value, indice, negative, vocabulary, memory, vmt):
        """compare:
                Compare (starting at the "indice"-th character) value to the current or a previously memorized value of variable.

                @type value: bitarray.bitarray
                @param value: a bit array a subarray of which we compare to the current variable binary value.
                @type indice: integer
                @param indice: the starting point of comparison in value.
                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @type vmt: netzob.Common.MMSTD.Dictionary.VariableManagementToken.VariableManagementToken
                @param vmt: a token which contains all critical information on the current operation.
        """
        raise NotImplementedError(_("The current variable does not implement 'compare'."))

    @abstractmethod
    def generate(self, negative, vocabulary, generationStrategy):
        """generate:
                Generate a value according to a given strategy and attribute it to the variable.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type generationStrategy: string
                @param generationStrategy: a strategy ("random" for instance) that defines the way the value will be generated.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def getValue(self, negative, vocabulary, memory):
        """getValue:

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: bitarray
                @return: the current value, or the last value stored in memory or None.
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
