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
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class GenericPath(object):
    """This class allows access to variables data during both abstraction
    and specialization.

    """

    def __init__(self,
                 memory=None,
                 dataAssignedToVariable=None,
                 variablesCallbacks=None):
        self.name = str(uuid.uuid4())
        self.memory = memory

        if variablesCallbacks is not None:
            self._variablesCallbacks = variablesCallbacks
        else:
            self._variablesCallbacks = []

        self._pendingValueVariables = {}

        if dataAssignedToVariable is None:
            self._dataAssignedToVariable = {}
        else:
            self._dataAssignedToVariable = dataAssignedToVariable

    def addResult(self, variable, result):
        """This method can be used to register the bitarray obtained after having parsed a variable

        >>> from netzob.all import *
        >>> path = GenericPath()
        >>> var = Data(dataType=String())
        >>> print(path.hasData(var))
        False
        >>> path.addResult(var, String("test").value)
        True
        >>> print(path.hasData(var))
        True
        >>> print(path.getData(var))
        bitarray('01110100011001010111001101110100')

        """

        self.assignData(result, variable)
        self._pendingValueVariables.pop(variable.id, None)

        return self._triggerVariablesCallbacks(variable)

    @typeCheck(AbstractVariable)
    def setPendingValueVariable(self, variable):
        self._pendingValueVariables[variable.id] = True

    @typeCheck(AbstractVariable)
    def getData(self, variable):
        """Return the data that is assigned to the specified variable.

        >>> from netzob.all import *
        >>> path = GenericPath()
        >>> v1 = Data(dataType=String(nbChars=(5, 10)), name="netzob")
        >>> print(path.hasData(v1))
        False
        >>> path.assignData(String("kurt").value, v1)
        >>> print(path.getData(v1))
        bitarray('01101011011101010111001001110100')

        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if variable.id in self._dataAssignedToVariable:
            return self._dataAssignedToVariable[variable.id]
        elif self.memory is not None and self.memory.hasValue(variable):
            return self.memory.getValue(variable)

        raise Exception(
            "No data assigned to variable '{}' {}".format(variable.name,
                                                          variable.field))

    @typeCheck(AbstractVariable)
    def hasData(self, variable):
        """Return True if a data has been assigned to the specified variable.
        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if variable.id in self._dataAssignedToVariable:
            return True
        if self.memory is not None:
            return self.memory.hasValue(variable)
        return False

    @typeCheck(bitarray, AbstractVariable)
    def assignData(self, data, variable):
        """Assign a data to the specified variable.

        """

        if data is None:
            raise Exception("Data cannot be None")
        if variable is None:
            raise Exception("Variable cannot be None")

        self._dataAssignedToVariable[variable.id] = data

    @typeCheck(AbstractVariable)
    def removeData(self, variable):
        self._logger.debug("Remove assigned data to variable: {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        del self._dataAssignedToVariable[variable.id]

    @typeCheck(AbstractVariable)
    def removeDataRecursively(self, variable):
        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import SELF

        self._logger.debug("Remove assigned data to variable (and its children): {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        if variable.id in self._dataAssignedToVariable:
            del self._dataAssignedToVariable[variable.id]

        if self.memory is not None and self.memory.hasValue(variable):
            self.memory.forget(variable)

        if hasattr(variable, 'children'):
            for child in variable.children:
                # We check if we reach the recursive pattern 'SELF' (in such case, no propagation is needed)
                if type(child) == type and child == SELF:
                    pass
                else:
                    self.removeDataRecursively(child)

    def registerVariablesCallBack(self, targetVariables, currentVariable, parsingCB=True):
        if targetVariables is None:
            raise Exception("Target variables cannot be None")
        if currentVariable is None:
            raise Exception("Current variable cannot be None")

        if len(targetVariables) == 0:
            raise Exception(
                "At least one target variable must be defined in the callback")

        newCB = (targetVariables, currentVariable, parsingCB)
        if newCB not in self._variablesCallbacks:
            self._variablesCallbacks.append(newCB)

    def _triggerVariablesCallbacks(self, triggeringVariable):

        moreCallBackFound = True

        # Try n-times to trigger callbacks in different orders as there can
        # have deadlocks between mutually linked domain definitions
        for _ in range(10):
            if moreCallBackFound is False:
                break

            moreCallBackFound = False
            callBackToExecute = None

            # Mix the callbacks functions, as we want to call them
            # randomly in order to eliminate potential deadlocks due
            # to mutually linked domain definitions
            shuffle(self._variablesCallbacks)

            for (targetVariables, currentVariable, parsingCB) in self._variablesCallbacks:

                if triggeringVariable == currentVariable:
                    break

                found = False
                for v in targetVariables:
                    if not isinstance(v, AbstractVariable):
                        break
                    if v == triggeringVariable:
                        found = True
                        break
                if found:
                    self._logger.debug("Found a callback that should be able to trigger")
                    callBackToExecute = (targetVariables, currentVariable, parsingCB)
                    break

            if callBackToExecute is not None:
                moreCallBackFound = True
                (targetVariables, currentVariable, parsingCB) = callBackToExecute
                if parsingCB:
                    resultingPaths = currentVariable.parse(self, acceptCallBack=False)
                else:
                    resultingPaths = currentVariable.specialize(self, acceptCallBack=True)
                if len(resultingPaths) == 0:
                    return False
                if self.hasData(currentVariable):
                    self._variablesCallbacks.remove(callBackToExecute)

        return True

    @property
    def name(self):
        """Returns the name of the path (mostly for debug purposes)"""
        return self.__name

    @name.setter  # type: ignore
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise Exception("Name of the path cannot be None")
        self.__name = name

    @property
    def memory(self):
        return self.__memory

    @memory.setter  # type: ignore
    @typeCheck(Memory)
    def memory(self, memory):
        self.__memory = memory
