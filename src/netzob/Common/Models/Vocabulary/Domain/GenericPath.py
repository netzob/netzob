# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
# +---------------------------------------------------------------------------+
# | related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw

@NetzobLogger
class GenericPath(object):
    """This class is the parent class of both abstraction paths and
    specialization paths"""

    def __init__(self, memory=None, dataAssignedToField=None, dataAssignedToVariable=None, fieldsCallbacks=None):
        self.name = str(uuid.uuid4())
        self.memory = memory
    
        if fieldsCallbacks is not None:
            self._fieldsCallbacks = fieldsCallbacks
        else:
            self._fieldsCallbacks = []
        
        if dataAssignedToField is None:
            self._dataAssignedToField = {}
        else:
            self._dataAssignedToField = dataAssignedToField

        if dataAssignedToVariable is None:
            self._dataAssignedToVariable = {}
        else:
            self._dataAssignedToVariable = dataAssignedToVariable

    def addResult(self, variable, result):
        self.assignDataToVariable(result, variable)

    def addResultToField(self, field, result):
        self.assignDataToField(result, field)

        if not self._triggerFieldCallbacks(field):
            raise Exception("Impossible to assign this result to the field (CB has failed)")

    def getDataAssignedToField(self, field):
        if field is None:
            raise Exception("Field cannot be None")

        if field.id in self._dataAssignedToField:
            return self._dataAssignedToField[field.id]
        elif self.memory.hasValue(field.domain):
            return self.memory.getValue(field.domain)

        raise Exception("No data is assigned to field '{0}'".format(field.id))

    def assignDataToField(self, data, field):
        if data is None:
            raise Exception("Data cannot be None")
        if field is None:
            raise Exception("Field cannot be None")

        self._dataAssignedToField[field.id] = data

    def isDataAvailableForField(self, field):
        if field is None:
            raise Exception("Field cannot be None")
        if field.id in self._dataAssignedToField:
            return True
        return self.memory.hasValue(field.domain)

    def removeAssignedDataToField(self, field):
        if field is None:
            raise Exception("Field cannot be None")
        del self._dataAssignedToField[field.id]

    @typeCheck(AbstractVariable)
    def getDataAssignedToVariable(self, variable):
        if variable is None:
            raise Exception("Variable cannot be None")
        if variable.id not in self._dataAssignedToVariable:
            # dirty hack
            # self.assignDataToVariable(variable.currentValue, variable)
            raise Exception("No data is assigned to variable '{0}'".format(variable.name))

        return self._dataAssignedToVariable[variable.id]

    @typeCheck(AbstractVariable)
    def isDataAvailableForVariable(self, variable):
        if variable is None:
            raise Exception("Variable cannot be None")
        return variable.id in self._dataAssignedToVariable

    @typeCheck(bitarray, AbstractVariable)
    def assignDataToVariable(self, data, variable):
        if data is None:
            raise Exception("Data cannot be None")
        if variable is None:
            raise Exception("Variable cannot be None")

        self._dataAssignedToVariable[variable.id] = data

    @typeCheck(AbstractVariable)
    def removeAssignedDataToVariable(self, variable):
        if variable is None:
            raise Exception("Variable cannot be None")

        del self._dataAssignedToVariable[variable.id]

    def registerFieldCallBack(self, fields, variable, parsingCB=True):
        if fields is None:
            raise Exception("Fields cannot be None")
        if variable is None:
            raise Exception("Variable cannot be None")

        if len(fields) == 0:
            raise Exception("At least one field must be defined in the callback")

        self._fieldsCallbacks.append((fields, variable, parsingCB))

    def _triggerFieldCallbacks(self, field):

        moreCallBackFound = True
        while moreCallBackFound:
            moreCallBackFound = False
            callBackToExecute = None
            
            for (fields, variable, parsingCB) in self._fieldsCallbacks:
                fieldsHaveValue = True
                for f in fields:
                    if not self.isDataAvailableForField(f):
                        fieldsHaveValue = False
                if fieldsHaveValue:
                    self._logger.debug("Found a callback that must be able to trigger (all its fields are set)")
                    callBackToExecute = (fields, variable, parsingCB)
                    break
                
            if callBackToExecute is not None:
                moreCallBackFound = True
                (fields, variable, parsingCB) = callBackToExecute
                if parsingCB:
                    resultingPaths = variable.parse(self, acceptCallBack=False)
                else:
                    resultingPaths = variable.specialize(self, acceptCallBack=False)
                if len(resultingPaths) == 0:
                    return False
                self._fieldsCallbacks.remove(callBackToExecute)
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
