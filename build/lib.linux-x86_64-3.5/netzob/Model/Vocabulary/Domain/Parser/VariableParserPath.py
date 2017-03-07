#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Parser.VariableParserResult import VariableParserResult


@NetzobLogger
class VariableParserPath(object):
    """This class denotes one parsing result of a variable against a specified content
    
    """
    
    def __init__(self, variableParser, consumedData, remainingData, originalVariableParserPath=None):
        self.name = str(uuid.uuid4())
        self.consumedData = consumedData
        self.remainingData = remainingData
        self.variableParser = variableParser
        self.memory = self.variableParser.memory.duplicate()
        
        self.originalVariableParserPath = originalVariableParserPath
        self.variableParserResults = []
        if originalVariableParserPath is not None:
            self.variableParserResults.extend(originalVariableParserPath.variableParserResults)

    def getValueToParse(self, variable):
        """Returns the value that is assigned to the specified variable"""
        

        
            
            
    def createVariableParserResult(self, variable, parserResult, consumedData, remainedData):
        variableParserResult = VariableParserResult(variable, parserResult, consumedData, remainedData)
        if parserResult:
            self._logger.debug("New parser result attached to path {0}: {1}".format(self, variableParserResult))
            self.remainingData = variableParserResult.remainedData
    
            if self.consumedData is None:
                self._logger.debug("consumed is none...")
                self.consumedData = variableParserResult.consumedData
            else:
                self.consumedData.extend(variableParserResult.consumedData)
        else:
            self._logger.debug("creation of an invalid parser result.")
        
        self.variableParserResults.append(variableParserResult)
        self._logger.debug("After registering new VariablePathResult, Path is {0}".format(self))        

    def __str__(self):
        return "Path {0} (consumedData={1}, remainingData={2}".format(self.name, self.consumedData, self.remainingData)

    @property
    def consumedData(self):
        return self.__consumedData

    @consumedData.setter
    def consumedData(self, consumedData):
        self.__consumedData = consumedData

    @property
    def memory(self):
        return self.__memory

    @memory.setter
    def memory(self, memory):
        if memory is None:
            raise Exception("Memory cannot be None")
        self.__memory = memory        
