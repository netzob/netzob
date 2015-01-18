#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid

#+---------------------------------------------------------------------------+
#| related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Specializer.VariableSpecializerResult import VariableSpecializerResult
from netzob.Common.Models.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw

@NetzobLogger
class VariableSpecializerPath(GenericPath):
    """This class denotes one specializing result of a variable
    
    """
    
    def __init__(self, originalVariableSpecializerPath=None, dataAssignedToField = None, memory=None):
        super(VariableSpecializerPath, self).__init__(memory)                

        if memory is not None:
            self.memory = memory
        else:
            if originalVariableSpecializerPath is not None:
                self.memory = self.originalVariableSpecializerPath.memory.duplicate()
            else:            
                self.memory = Memory()
        self.callBacksOnVariableSpecialization = dict()
        
        self.originalVariableSpecializerPath = originalVariableSpecializerPath
        self.variableSpecializerResults = []
        if originalVariableSpecializerPath is not None:
            self.variableSpecializerResults.extend(originalVariableSpecializerPath.variableSpecializerResults)

        if originalVariableSpecializerPath is not None:
            self.callBacksOnVariableSpecialization = originalVariableSpecializerPath.callBacksOnVariableSpecialization

        self._logger.warn("Creation of a var path with memory: {0}".format(self.memory))
            
    def createVariableSpecializerResult(self, variable, specializerResult, generatedContent):

        # first we check if a result was already known for this variable
        equivalentVariableSpecializerResult = None
        for variableSpecializerResult in self.variableSpecializerResults:
            if variableSpecializerResult.variable == variable:
                equivalentVariableSpecializerResult = variableSpecializerResult

        if equivalentVariableSpecializerResult is not None:
            equivalentVariableSpecializerResult.specializerResult = specializerResult
            equivalentVariableSpecializerResult.generatedContent = generatedContent
            self._logger.debug("A VariableSpecializerResult already exists, we update its results, it becomes: {0}".format(generatedContent))
        else:        
            variableSpecializerResult = VariableSpecializerResult(variable, specializerResult, generatedContent)
            if specializerResult:
                self._logger.debug("New specializer result attached to path {0}: {1}".format(self, variableSpecializerResult))
            else:
                self._logger.debug("creation of an invalid specializer result.")


            self._logger.info("Registering result for variable {0} in path {1}".format(variable.id, self.name))
            self.variableSpecializerResults.append(variableSpecializerResult)
            self._logger.debug("After registering new VariablePathResult, Path is {0}".format(self))

            self._triggerCallBacks(variable)

    def _triggerCallBacks(self, variable):
        """This method must be called everytime a variable has been specialized in order to execute potential callbacks"""
        self._logger.debug("Triggering potential callbacks attached to variable {0} specialization process.".format(variable))
        if variable in self.callBacksOnVariableSpecialization.keys():
            callbacks = self.callBacksOnVariableSpecialization[variable]
            for callback in callbacks:
                callback(self, False)
            del self.callBacksOnVariableSpecialization[variable]

    def assignDataToField(self, data, field):
        if data is None:
            raise Exception("Data cannot be None")
        if field is None:
            raise Exception("Field cannot be None")
        self.__dataAssignedToField[field.id] = data

    def isDataAvailableForField(self, field):
        if field is None:
            raise Exception("Field cannot be None")
        if field.id in self.__dataAssignedToField:
            return True
        return self.memory.hasValue(field.domain)                

    def isValueForVariableAvailable(self, variable):
        self._logger.debug("IsValueForAvailable: {0}".format(variable.id))
        return self.memory.hasValue(variable)

    def getValueForVariable(self, variable):
        self._logger.debug("GetValueForVariable: {0}".format(variable.id))
        return self.memory.getValue(variable)

    def addCallbackOnVariableSpecialization(self, variable, callBackFunction):
        """Register a callback function that must be called when the specified field is specialized"""
        self._logger.debug("Adding a callback function on variable {0}".format(variable))
        if variable in self.callBacksOnVariableSpecialization.keys():
            self.callBacksOnVariableSpecialization[variable].append(callBackFunction)
        else:
            self.callBacksOnVariableSpecialization[variable] = [callBackFunction]

    def __str__(self):        
        return "Path {0} (generatedContent={1})".format(self.name, self.generatedContent)

    @property
    def generatedContent(self):
        result = None
        for variableSpecializerResult in self.variableSpecializerResults:
            if result is None:
                result = variableSpecializerResult.generatedContent.copy()
            else:
                result += variableSpecializerResult.generatedContent

        return result

    @generatedContent.setter
    def generatedContent(self, generatedContent):
        raise Exception("Cannot modify the generated content")

