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
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Specializer.VariableSpecializerResult import VariableSpecializerResult


@NetzobLogger
class VariableSpecializerPath(object):
    """This class denotes one specializing result of a variable
    
    """
    
    def __init__(self, variableSpecializer, generatedContent, originalVariableSpecializerPath=None):
        self.name = str(uuid.uuid4())
        self._logger.debug("Generated Content = {0}".format(generatedContent))
        self.generatedContent = generatedContent
        self.variableSpecializer = variableSpecializer
        self.memory = self.variableSpecializer.memory.duplicate()
        
        self.originalVariableSpecializerPath = originalVariableSpecializerPath
        self.variableSpecializerResults = []
        if originalVariableSpecializerPath is not None:
            self.variableSpecializerResults.extend(originalVariableSpecializerPath.variableSpecializerResults)

            
    def createVariableSpecializerResult(self, variable, specializerResult, generatedContent):
        variableSpecializerResult = VariableSpecializerResult(variable, specializerResult, generatedContent)
        if specializerResult:
            self._logger.debug("New specializer result attached to path {0}: {1}".format(self, variableSpecializerResult))
    
            if self.generatedContent is None:
                self.generatedContent = variableSpecializerResult.generatedContent
            else:
                self.generatedContent.extend(variableSpecializerResult.generatedContent)
        else:
            self._logger.debug("creation of an invalid specializer result.")
        
        self.variableSpecializerResults.append(variableSpecializerResult)
        self._logger.debug("After registering new VariablePathResult, Path is {0}".format(self))        

    def __str__(self):
        return "Path {0} (generatedContent={1})".format(self.name, self.generatedContent)

    @property
    def generatedContent(self):
        return self.__generatedContent

    @generatedContent.setter
    def generatedContent(self, generatedContent):
        self.__generatedContent = generatedContent

    @property
    def memory(self):
        return self.__memory

    @memory.setter
    def memory(self, memory):
        if memory is None:
            raise Exception("Memory cannot be None")
        self.__memory = memory        
