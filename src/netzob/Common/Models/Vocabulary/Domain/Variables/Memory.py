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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


@NetzobLogger
class Memory(object):
    """Definition of a memory, used to store variable values in a persisting and independent way.

    Example of usages:


    >>> from netzob.all import *
    >>> f1 = Field("hello1")
    >>> f2 = Field(100)
    >>> m = Memory()
    >>> m.memorize(f1.domain)
    >>> m.memorize(f2.domain)
    >>> m.persistMemory()
    >>> print len(m.memory.keys())
    2
    >>> duplicatedMemory = m.duplicate()
    >>> print len(duplicatedMemory.memory.keys())
    2

    """

    def __init__(self):
        """Constructor of Memory"""
        # create logger with the given configuration

        self.__memory = dict()
        self.__temporaryMemory = dict()
        self.__memoryAccessCB = None

    def duplicate(self):
        """Duplicates in a new memory

        >>> from netzob.all import *
        >>> f1 = Field("Protocol RE")
        >>> f2 = Field(100)
        >>> m = Memory()
        >>> m.memorize(f1.domain)
        >>> m.memorize(f2.domain)
        >>> m.persistMemory()
        >>> print len(m.memory.keys())
        2
        >>> n = m.duplicate()
        >>> print len(n.memory.keys())
        2

        :return: a new memory containing the same entries than current one
        :rtype: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Memory`
        """
        duplicatedMemory = Memory()
        for k in self.memory.keys():
            duplicatedMemory.memory[k] = self.memory[k]
        duplicatedMemory.createMemory()
        return duplicatedMemory

#+---------------------------------------------------------------------------+
#| Functions on memories                                                     |
#+---------------------------------------------------------------------------+
    def createMemory(self):
        """Reinit the temporary memory and copy all values from the real memory in it.
        """
        self.__temporaryMemory = dict()
        for key in self.memory.keys():
            self.__temporaryMemory[key] = self.memory[key]

    def persistMemory(self):
        """Copy all values from the temporary memory into the real memory.
        """
        self.__memory = dict()
        for key in self.__temporaryMemory.keys():
            self.memory[key] = self.__temporaryMemory[key]

    def cleanMemory(self):
        """Remove all variables and values from real and temporary memories.
        """
        # self.memory = dict()  # TODO: impement this change in all calling functions.
        self.__temporaryMemory = dict()

    def recallMemory(self):
        """Return all values store in the temporary memory.

        :return: the value of all variables in the temporary memory.
        :rtype: a :class:`dict`
        """
        return self.__temporaryMemory

    def printMemory(self):
        """Debug functions which print all values in temporary memory.
        """
        self._logger.debug("Memory map:")
        for _id, _val in self.__temporaryMemory.iteritems():
            self._logger.debug("> {0}  = {1}".format(_id, _val))

#+---------------------------------------------------------------------------+
#| Functions on temporary memory elements                                    |
#+---------------------------------------------------------------------------+
    @typeCheck(AbstractVariable)
    def hasMemorized(self, variable):
        """Check if a variable is in the temporary memory.

        :param variable: the given variable we search in memory.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :return: True if the variable has been found in the memory.
        :rtype: :class:`bool`
        :raise: :class:`TypeError` if parameter is not valid
        """
        if variable is None:
            raise TypeError("variable cannot be None")

        return variable.id in self.__temporaryMemory.keys()

    @typeCheck(AbstractVariable)
    def restore(self, variable):
        """Copy back the value of a variable from the real memory in the temporary memory.

        :param variable: the given variable, the value of which we want to restore.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :raise: :class:`TypeError` if parameter is not valid
        """
        if variable is None:
            raise TypeError("variable cannot be None")

        if variable.id in self.memory.keys():
            self.__temporaryMemory[variable.id] = self.memory[variable.id]
            if self.memoryAccessCB is not None:
                value = variable.currentValue
                self.memoryAccessCB("W", variable, value)

    @typeCheck(AbstractVariable)
    def memorize(self, variable):
        """Save the current value of a variable in memory.

        :param variable: the given variable, the value of which we want to save.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :raise: :class:`TypeError` if parameter is not valid
        """
        if variable is None:
            raise TypeError("variable cannot be None")

        if variable.currentValue is not None:
            self.__temporaryMemory[variable.id] = variable.currentValue
            if self.memoryAccessCB is not None:
                value = variable.currentValue
                self.memoryAccessCB("W", variable, value)

    @typeCheck(AbstractVariable)
    def forget(self, variable):
        """Remove a variable and its value from the temporary memory.

        :param variable: the given variable, the value of which we want to forget.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :raise: :class:`TypeError` if parameter is not valid
        """
        if variable is None:
            raise TypeError("variable cannot be None")

        if self.hasMemorized(variable):
            del self.__temporaryMemory[variable.id]
            if self.memoryAccessCB is not None:
                self.memoryAccessCB("D", variable, None)

    @typeCheck(AbstractVariable)
    def recall(self, variable):
        """Return the value of one variable store in the temporary memory.

        :param variable: the given variable, the value of which we are searching.
        :type variable: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
        :return: the value of the given variable in the temporary memory or None is not available
        :rtype: :class:`bitarray`
        :raise: :class:`TypeError` if parameter is not valid
        """
        if variable is None:
            raise TypeError("variable cannot be None")

        if self.hasMemorized(variable):
            value = self.__temporaryMemory[variable.id]
            if self.memoryAccessCB is not None:
                self.memoryAccessCB("R", variable, value)
            return value
        else:
            return None

    @property
    def memory(self):
        """The content of the memory is stored in this dict().

        :type: :class:`dict`
        """
        return self.__memory

    @memory.setter
    def memory(self, memory):
        self.__memory = dict()
        for k, v in memory.iteritems():
            self.__memory[k] = v

    @property
    def memoryAccessCB(self):
        """Callback to execute after a memory access.

        :type: function
        :raise: `TypeError` if parameter's type is not valid
        """
        return self.__memoryAccessCB

    @memoryAccessCB.setter
    def memoryAccessCB(self, memoryAccessCB):
        self.__memoryAccessCB = memoryAccessCB
