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

# +---------------------------------------------------------------------------+
# | related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class GenericPath(object):
    """This class allows access to variables data during both abstraction
    and specialization.

    """

    def __init__(self,
                 memory=None,
                 dataAssignedToVariable=None,
                 variablesCallbacks=None):
        self.memory = memory

        if variablesCallbacks is not None:
            self._variablesCallbacks = variablesCallbacks
        else:
            self._variablesCallbacks = []

        self._variablesWithResult = []

        if dataAssignedToVariable is None:
            self._dataAssignedToVariable = {}
        else:
            self._dataAssignedToVariable = dataAssignedToVariable

        self._current_callbacks_operation = []

        # List of inaccessible variables during specialization, due to preseting a parent variable
        # If a relationship targets one of those inaccessible variables, this should trigger an InaccessibleVariableException
        self._inaccessibleVariables = []

    def __str__(self):
        return "Path({})".format(str(id(self)))

    def addResult(self, variable, result, notify=True):
        """
        This method can be used to register the bitarray obtained after having parsed a variable.

        :param notify: decide to look for other variable that could be evaluated using this result
        :type notify: bool (default :const:`True`)

        >>> from netzob.all import *
        >>> path = GenericPath()
        >>> var = Data(dataType=String())
        >>> print(path.hasData(var))
        False
        >>> path.addResult(var, String("test").value)[0]
        True
        >>> print(path.hasData(var))
        True
        >>> print(path.getData(var))
        bitarray('01110100011001010111001101110100')

        """

        self.assignData(result, variable)

        if notify:
            self._logger.debug("Testing variable callbacks after addResult()")
            return self._triggerVariablesCallbacks(variable)
        return (True, (self, ))

    def hasResult(self, variable):
        return variable in self._variablesWithResult

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
        if variable in self._dataAssignedToVariable:
            return self._dataAssignedToVariable[variable]
        else:
            raise Exception(
                "In path '{}', no data assigned to variable '{}' (id={}), which is linked to field '{}'".format(self,
                                                                                                                variable,
                                                                                                                id(variable),
                                                                                                                variable.field))

    def hasData(self, variable):
        """Return True if a data has been assigned to the specified variable.
        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if variable in self._dataAssignedToVariable:
            return True
        else:
            return False

    def getDataInMemory(self, variable):
        """Return the data that is assigned to the specified variable in the memory.

        >>> from netzob.all import *
        >>> path = GenericPath(memory=Memory())
        >>> v1 = Data(dataType=String(nbChars=(5, 10)), name="netzob")
        >>> print(path.hasDataInMemory(v1))
        False
        >>> path.memory.memorize(v1, String("kurt").value)
        >>> print(path.getDataInMemory(v1))
        bitarray('01101011011101010111001001110100')

        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if self.memory is not None and self.memory.hasValue(variable):
            return self.memory.getValue(variable)
        raise Exception(
            "In path '{}', no data assigned to variable '{}' (id={}), which is linked to field '{}'".format(self,
                                                                                                            variable,
                                                                                                            id(variable),
                                                                                                            variable.field))

    def hasDataInMemory(self, variable):
        """Return True if a data has been assigned to the specified variable in the memory.
        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if self.memory is not None:
            return self.memory.hasValue(variable)
        else:
            return False

    def assignData(self, data, variable):
        """Assign a data to the specified variable.

        """

        if data is None:
            raise Exception("Data cannot be None")
        if variable is None:
            raise Exception("Variable cannot be None")

        # if variable in self._dataAssignedToVariable:
        #     self._logger.debug("Replacing '{}' by '{}' for variable '{}'".format(self._dataAssignedToVariable[variable].tobytes(), data.tobytes(), variable))

        self._dataAssignedToVariable[variable] = data

    def removeData(self, variable):
        self._logger.debug("Remove assigned data to variable: {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        if variable in self._dataAssignedToVariable:
            del self._dataAssignedToVariable[variable]

    def removeDataRecursively(self, variable):
        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import SELF

        self._logger.debug("Remove assigned data to variable (and its children): {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        if variable in self._dataAssignedToVariable:
            del self._dataAssignedToVariable[variable]

        if self.memory is not None and self.memory.hasValue(variable):
            self.memory.forget(variable)

        if hasattr(variable, 'children'):
            for child in variable.children:
                # We check if we reach the recursive pattern 'SELF' (in such case, no propagation is needed)
                if type(child) == type and child == SELF:
                    pass
                else:
                    self.removeDataRecursively(child)

    def setInaccessibleVariableRecursively(self, variable):
        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import SELF

        self._logger.debug("Set the variable (and its children) inaccessible: {}".format(variable))
        if variable is None:
            raise Exception("Variable cannot be None")

        self._inaccessibleVariables.append(variable)

        if hasattr(variable, 'children'):
            for child in variable.children:
                # We check if we reach the recursive pattern 'SELF' (in such case, no propagation is needed)
                if type(child) == type and child == SELF:
                    pass
                else:
                    self.setInaccessibleVariableRecursively(child)

    def isVariableInaccessible(self, variable):
        """Return True if a variable is inaccessible.
        """

        if variable is None:
            raise Exception("Variable cannot be None")
        if variable in self._inaccessibleVariables:
            return True
        else:
            return False

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
        else:
            self._logger.debug("Callback already registered")

    def _triggerVariablesCallbacks(self, triggeringVariable):
        """Returns a tuple, where the first element tell if the callback
        computation has been successful, and where the second element is a
        generator/list of the new computed parsingPaths.

        """

        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat

        callbacks_to_execute = []
        potentialCallback = None
        tested_callbacks = []
        self._logger.debug("Number of callbacks to analyze: {}".format(len(self._variablesCallbacks)))

        for potentialCallback in self._variablesCallbacks:
            self._logger.debug("Testing a new callback")

            if potentialCallback in tested_callbacks:
                self._logger.debug("Potential callback already tested")
                potentialCallback = None
                continue

            # Add current callback to a list of callbacks that have already been tested
            tested_callbacks.append(potentialCallback)

            if potentialCallback in self._current_callbacks_operation:
                self._logger.debug("Potential callback is currently tested")
                potentialCallback = None
                continue

            # Retrieve callback elements
            (targetVariables, currentVariable, parsingCB) = potentialCallback

            if triggeringVariable == currentVariable:
                self._logger.debug("Potential callback triggered by the variable concerned by the resolution")
                potentialCallback = None
                continue

            # Test if triggeringVariable may help in computing the
            # callback (i.e. it is in the list of the targeted
            # variables of the currentVariable)
            found = False
            for v in targetVariables:
                if v == triggeringVariable:
                    found = True
                    break
            if found:
                self._logger.debug("Found a callback on '{}' that should be able to be computed due to triggering variable '{}' from field '{}'".format(currentVariable, triggeringVariable, triggeringVariable.field))
                #break
            else:

                # Current callback is considered if there exists
                # another callback for which we have common target
                # variables (this means that the resolution of a
                # common target variable may resolve two callbacks)
                found = False
                for inner_cbk in self._variablesCallbacks:
                    (inner_targetVariables, inner_currentVariable, inner_parsingCB) = inner_cbk

                    # We verify those three conditions to say that a callback should be analyzed:
                    # - We don't consider Repeat variables here
                    # - We don't consider parsing mode
                    # - We verify that the set of common target variables is not empty
                    common_target_variables = list(set(inner_targetVariables).intersection(targetVariables))
                    if not inner_parsingCB and not isinstance(currentVariable, Repeat) and len(common_target_variables) > 0:
                        found = True
                        break
                if found:
                    if triggeringVariable.parent is not None and triggeringVariable.parent == currentVariable:
                        potentialCallback = None
                        continue
                    else:
                        self._logger.debug("Found a callback on '{}' that should be able to be computed due to indirect triggering variable '{}' from field '{}'".format(currentVariable, triggeringVariable, triggeringVariable.field))
                else:
                    self._logger.debug("Callback not concerned by the triggering variable")
                    potentialCallback = None
                    continue

            if potentialCallback is not None:
                callbacks_to_execute.append(potentialCallback)

        last_callback_succeed = True
        if len(callbacks_to_execute) > 0:
            from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import RelationDependencyException
            while len(callbacks_to_execute) > 0:
                callback_to_execute = callbacks_to_execute.pop()
                try:
                    # Add current callback to a list of callbacks that are currently being executed (recursively).
                    # This avoids computing a callback that is being already computing
                    self._current_callbacks_operation.append(callback_to_execute)

                    self._logger.debug("Executing a callback")
                    results = self._processCallback(callback_to_execute)
                    last_callback_succeed = True
                except RelationDependencyException as e:
                    last_callback_succeed = False
                    self._logger.debug("Callback execution did not succeed")
                    continue
                else:
                    self._logger.debug("Callback execution succeed")
                    return results
                finally:
                    self._current_callbacks_operation.remove(callback_to_execute)

        # If no callback execution succeed, or there were no callback at all
        resultingPaths = (self, )
        return (last_callback_succeed, resultingPaths)

    def _processCallback(self, callBackToExecute):
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat

        # Retrieve callback elements
        (targetVariables, currentVariable, parsingCB) = callBackToExecute

        # Callback computation
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import RelationDependencyException
        try:
            if parsingCB:
                resultingPaths = currentVariable.parse(self, acceptCallBack=True, triggered=True)
            else:
                resultingPaths = currentVariable.specialize(self, acceptCallBack=False)
        except RelationDependencyException as e:
            raise

        # Fails when not all paths are valid
        if not any(path.ok for path in resultingPaths):
            return (False, resultingPaths)
        else:
            self._variablesWithResult.append(currentVariable)

        # If needed, remove the callback from the list of callbacks
        remove_cb_cond = self.hasResult(currentVariable)
        remove_cb_cond &= isinstance(currentVariable, (Data, Repeat))
        if remove_cb_cond and callBackToExecute in self._variablesCallbacks:
            self._variablesCallbacks.remove(callBackToExecute)

        return (True, resultingPaths)

    def show(self):
        self._logger.debug("Variables registered for genericPath: '{}':".format(self))
        for (var, val) in self._dataAssignedToVariable.items():
            self._logger.debug("  [+] Variable: '{}' (id={}), with value: '{}', is linked to field '{}'".format(var, id(var), val.tobytes(), var.field))

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
