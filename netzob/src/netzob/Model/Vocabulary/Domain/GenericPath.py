# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import uuid
from bitarray import bitarray
from random import shuffle

# +---------------------------------------------------------------------------+
# | related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class GenericPath(object):
    """This class is the parent class of both abstraction paths and
    specialization paths"""

    def __init__(self,
                 memory=None,
                 dataAssignedToField=None,
                 dataAssignedToVariable=None,
                 variablesCallbacks=None):
        self.name = str(uuid.uuid4())
        self.memory = memory

        if variablesCallbacks is not None:
            self._variablesCallbacks = variablesCallbacks
        else:
            self._variablesCallbacks = []

        if dataAssignedToField is None:
            self._dataAssignedToField = {}
        else:
            self._dataAssignedToField = dataAssignedToField

        if dataAssignedToVariable is None:
            self._dataAssignedToVariable = {}
        else:
            self._dataAssignedToVariable = dataAssignedToVariable

    def addResult(self, variable, result):
        """This method can be used to register the bitarray obtained after having parsed a variable

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        >>> path = GenericPath()
        >>> var = Data(dataType=String())
        >>> print(path.isDataAvailableForVariable(var))
        False
        >>> path.addResult(var, TypeConverter.convert("test", String, BitArray))
        >>> print(path.isDataAvailableForVariable(var))
        True
        >>> print(path.getDataAssignedToVariable(var))
        bitarray('01110100011001010111001101110100')

        """

        self.assignDataToVariable(result, variable)

        if not self._triggerVariablesCallbacks(variable):
            pass
            #raise Exception("Impossible to assign this result to the variable (CB has failed)")

    @typeCheck(AbstractVariable)
    def getDataAssignedToVariable(self, variable):
        """Return the data that is assigned to the specified varibale

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        >>> path = GenericPath()
        >>> v1 = Data(dataType=String(nbChars=(5, 10)), name="netzob")
        >>> print(path.isDataAvailableForVariable(v1))
        False
        >>> path.assignDataToVariable(TypeConverter.convert("kurt", String, BitArray), v1)
        >>> print(path.getDataAssignedToVariable(v1))
        bitarray('01101011011101010111001001110100')

        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if variable.id in self._dataAssignedToVariable:
            return self._dataAssignedToVariable[variable.id]
        elif self.memory is not None and self.memory.hasValue(variable):
            return self.memory.getValue(variable)

        raise Exception(
            "No data is assigned to variable '{0}'".format(variable.name))

    @typeCheck(AbstractVariable)
    def isDataAvailableForVariable(self, variable):
        if variable is None:
            raise Exception("Variable cannot be None")
        if variable.id in self._dataAssignedToVariable:
            return True
        if self.memory is not None:
            return self.memory.hasValue(variable)
        return False

    @typeCheck(bitarray, AbstractVariable)
    def assignDataToVariable(self, data, variable):
        if data is None:
            raise Exception("Data cannot be None")
        if variable is None:
            raise Exception("Variable cannot be None")

        self._dataAssignedToVariable[variable.id] = data

    @typeCheck(AbstractVariable)
    def removeAssignedDataToVariable(self, variable):
        self._logger.debug("Remove assigned data to variable: {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        del self._dataAssignedToVariable[variable.id]

    @typeCheck(AbstractVariable)
    def removeAssignedDataToVariableAndChildren(self, variable):
        self._logger.debug("Remove assigned data to variable (and its children): {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        if variable.id in self._dataAssignedToVariable:
            del self._dataAssignedToVariable[variable.id]

        if self.memory is not None and self.memory.hasValue(variable):
            self.memory.forget(variable)

        if hasattr(variable, 'children'):
            for child in variable.children:
                self.removeAssignedDataToVariableAndChildren(child)

    def registerVariablesCallBack(self, targetVariables, currentVariable, parsingCB=True):
        if targetVariables is None:
            raise Exception("Target variables cannot be None")
        if currentVariable is None:
            raise Exception("Current variable cannot be None")

        if len(targetVariables) == 0:
            raise Exception(
                "At least one target variable must be defined in the callback")

        self._variablesCallbacks.append((targetVariables, currentVariable, parsingCB))

    def _triggerVariablesCallbacks(self, triggeringVariable):

        moreCallBackFound = True

        # Try n-times to trigger callbacks in different orders as there can have deadlocks
        # between mutually linked domain definitions
        for i in range(10):
            if moreCallBackFound is False:
                break

            moreCallBackFound = False
            callBackToExecute = None

            # Mix the callbacks functions, as we want to call them
            # randomly in order to eliminate potential deadlocks due
            # to mutually linked domain definitions
            shuffle(self._variablesCallbacks)

            for (targetVariables, currentVariable, parsingCB) in self._variablesCallbacks:

                found = False
                for v in targetVariables:
                    if not isinstance(v, AbstractVariable):
                        break
                    if v == triggeringVariable:
                        found = True
                        break
                if found is False:
                    break
                # if not triggeringVariable in targetVariables:
                #     break

                variablesHaveValue = True
                for v in targetVariables:
                    if not self.isDataAvailableForVariable(v):
                        variablesHaveValue = False
                if variablesHaveValue:
                    self._logger.debug("Found a callback that must be able to trigger (all its target variables are set)")
                    callBackToExecute = (targetVariables, currentVariable, parsingCB)
                    break

            if callBackToExecute is not None:
                moreCallBackFound = True
                i_cbk = self._variablesCallbacks.index(callBackToExecute)
                self._variablesCallbacks.pop(i_cbk)
                (targetVariables, currentVariable, parsingCB) = callBackToExecute
                if parsingCB:
                    resultingPaths = currentVariable.parse(self, acceptCallBack=False)
                else:
                    resultingPaths = currentVariable.specialize(self, acceptCallBack=True)
                if len(resultingPaths) == 0:
                    self._variablesCallbacks.insert(i_cbk, callBackToExecute)
                    return False

        return True

    @property
    def name(self):
        """Returns the name of the path (mostly for debug purposes)"""
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise Exception("Name of the path cannot be None")
        self.__name = name

    @property
    def memory(self):
        return self.__memory

    @memory.setter
    @typeCheck(Memory)
    def memory(self, memory):
        self.__memory = memory
