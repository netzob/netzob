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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Parser.VariableParserPath import VariableParserPath
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class VariableParser(object):
    """This class can be use to parse some data against the specification of a domain

    """

    def __init__(self, variable, memory):
        self.variable = variable
        self.memory = memory
        self.__clearResults()

    def parse(self, content):
        """Parses the specified content against the variable"""
        self._logger.debug("Parse '{0}' with variable '{1}' specifications".format(content, self.variable))

        self.__clearResults()

        # we create the initial parser path
        variableParserPath = self._createVariableParserPath(None, content)

        self.variableParserPaths = self.variable.parse(variableParserPath)
        self._logger.debug("Parsing variable '{0}' generated '{1}' valid paths".format(self.variable, len(self.variableParserPaths)))
        
        return self.isOk()

    def isOk(self):
        """Returns True if at least one valid VariableParserResult is available"""
        return len(self.variableParserPaths)>0
    
    def __clearResults(self):
        """Prepare for a new parsing by cleaning any previously results"""
        self.variableParserResults = []
        self.variableParserPaths = []        

    def _createVariableParserPath(self, consumedContent, remainingContent, originalVariableParserPath=None):
        self._logger.debug("rContent = {0}".format(remainingContent))
        copy_consumedContent = None
        copy_remainingContent = None

        if consumedContent is not None:
            copy_consumedContent = consumedContent.copy()

        if remainingContent is not None:
            copy_remainingContent = remainingContent.copy()
        
        varPath = VariableParserPath(self, copy_consumedContent, copy_remainingContent, originalVariableParserPath)
        return varPath

    def createVariableParser(self, content):
        variableParser = VariableParser(content)
        self.variableParserChildren.append(variableParser)
        return variableParser        

    @property
    def variable(self):
        """The variable that will be use to parse some content

        :type: :class:`netzob.Common.Models.Vocabulary.Domaoin.Variables.AbstractVariable.AbstractVariable`
        """
        return self.__variable

    @variable.setter
    @typeCheck(AbstractVariable)
    def variable(self, variable):
        if variable is None:
            raise ValueError("Variable cannot be None")

        self.__variable = variable

    @property
    def memory(self):
        """The memory that will be use to parse some content

        :type: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.Memory.Memory`
        """
        return self.__memory

    @memory.setter
    @typeCheck(Memory)
    def memory(self, memory):
        if memory is None:
            raise ValueError("Memory cannot be None")

        self.__memory = memory        
        
    @property
    def variableParserResults(self):
        """The list of parsing results obtained after last call to parse() method

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Domain.Parser.FieldParserResult.FieldParserResult`
        """
        return self.__variableParserResults

    @variableParserResults.setter
    def variableParserResults(self, results):
        if results is None:
            raise ValueError("FieldParserResults cannot be None, it should be an empty list if really you want to clear the results")

        self.__variableParserResults = results

    @property
    def variableParserChildren(self):
        """The list of variable parser that were created while executing the parse() method

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Domain.Parser.VariableParser.VariableParser`
        """
        return self.__variableParserChildren

    @variableParserChildren.setter
    def variableParserChildren(self, results):
        if results is None:
            raise ValueError("VariableParserChildren cannot be None, it should be an empty list if really you want to clear the results")

        self.__variableParserChildren = results

