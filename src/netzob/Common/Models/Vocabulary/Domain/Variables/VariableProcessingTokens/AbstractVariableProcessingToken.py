# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw

from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


@NetzobLogger
class AbstractVariableProcessingToken(object):
    """This token is used to share information regarding the current generation or reading process
    based on variable definition.
    """

    def __init__(self, memory=None, value=None, vocabulary=None):
        """Constructor of AbstractVariableProcessingToken:

        :keyword memory: a memory which can contain a former value of the processed variable.
        :type memory: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Memory.Memory`
        :keyword value: the current value in binary format (bitarray).
        :type value: :class:`bitarray`
        :raises :class:`TypeError` if types of arguments are not valid.

        """
        self.__memory = None
        self.__value = bitarray(endian=AbstractType.defaultEndianness())
        self.__Ok = True
        self.__index = 0
        self.__vocabulary = None

        if memory is None:
            memory = Memory()
        self.memory = memory

        if value is not None:
            self.value = value

        self.vocabulary = vocabulary

        # A dict that associated each variable with the related portion of data
        self.__linkedValues = dict()

        # A dist that describes callbacks for relations
        self.__relationCallbacks = dict()

        # A list of (id, value) that associates the contribution to the final value of every variable to its ID.
        #self.__linkedValues = []

    @typeCheck(AbstractVariable, bitarray)
    def setValueForVariable(self, variable, value):
        if variable is None:
            raise TypeError("Variable cannot be None")
        
        self._logger.fatal("Saving value {0} in variable {1}".format(TypeConverter.convert(value, BitArray, Raw), variable))
        
        self.__linkedValues[variable.id] = value
        if variable.id in self.__relationCallbacks.keys():
            self._logger.debug("{0} participates in a relation, we might be able to complete it now...".format(variable))
            toCall = self.__relationCallbacks[variable.id]
            
            for cb in toCall:
                (domain, call) = cb
                self._logger.debug("Execute Relation callback {0} / {1}".format(domain, call))
                self.__relationCallbacks[variable.id].remove(cb)
                if domain.isDefined(self):
                    self._logger.debug("relation defined.")
                    call(self)
                    if not self.Ok:
                        raise Exception("A relation has failed.")
                else:
                    self._logger.debug("Relation cannot yet be computed, more dependencies required.")

        self._logger.debug("End of setValueForVariable.")

    @typeCheck(AbstractVariable)
    def getValueForVariable(self, variable):
        if variable is None:
            raise TypeError("Variable cannot be None")
        return self.__linkedValues[variable.id]

    @typeCheck(AbstractVariable)
    def isValueForVariableAvailable(self, variable):
        if variable is None:
            raise TypeError("Variable cannot be None")
        return variable.id in self.__linkedValues.keys()

    @typeCheck(AbstractVariable)
    def removeValueForVariable(self, variable):
        if variable is None:
            raise TypeError("Variable cannot be None")
        del self.__linkedValues[variable.id]

    def addRelationCallback(self, triggerVariable, callbackVar, callbackMethod):
        callbackVariable = (callbackVar, callbackMethod)
        if triggerVariable.id in self.__relationCallbacks.keys():
            if not callbackVariable in self.__relationCallbacks[triggerVariable.id]:
                self.__relationCallbacks[triggerVariable.id].add(callbackVariable)
        else:
            self.__relationCallbacks[triggerVariable.id] = [callbackVariable]

    @property
    def Ok(self):
        """Returns False if an error was encounter in the generation process.

        :type: :class:`bool`
        """
        return self.__Ok

    @Ok.setter
    @typeCheck(bool)
    def Ok(self, Ok):
        self.__Ok = Ok

    @property
    def memory(self):
        """The memory that will be used to learn, store and restore values of fields

        :type: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Memory.Memory`
        return self.__memory
        """
        return self.__memory

    @memory.setter
    @typeCheck(Memory)
    def memory(self, memory):
        self.__memory = memory

    @property
    def value(self):
        """The current value in bitarray format

        :type: :class:`bitarray`
        """
        return self.__value

    @value.setter
    @typeCheck(bitarray)
    def value(self, value):
        self.__value = value

    @property
    def index(self):
        """The current index in the generation/reading process

        :type: :class:`int`
        """
        return self.__index

    @index.setter
    def index(self, index):
        if index < 0:
            raise ValueError("Index must be >= 0")
        self.__index = index

    # @property
    # def linkedValues(self):
    #     """Store the ID of the variable and its value.

    #     :type: a :class:`dict` made of keys :class:`str` and values :class:`object`.
    #     """

    #     return self.__linkedValues

    # @linkedValues.setter
    # def linkedValues(self, linkedValues):
    #     self.__linkedValues = dict
    #     for key, val in linkedValues.iteritems():
    #         self.__linkedValues[key] = val

    @property
    def vocabulary(self):
        """Vocabulary attached to the processing token
        """

        return self.__vocabulary

    @vocabulary.setter
    def vocabulary(self, vocabulary):
        self.__vocabulary = vocabulary
