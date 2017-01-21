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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable

@NetzobLogger
class VariableParserResult():
    """This class denotes one parsing result of a variable against a specified content
    
    """

    def __init__(self, variable, result, consumedData, remainedData):
        self.variable = variable
        self.result = result
        self.consumedData = consumedData
        self.remainedData = remainedData

    def isOk(self):
        """Returns True if this results is True"""
        return self.result

    def __str__(self):
        return "VarParserResult (result={0}, consumedData={1}, remainingData={2})".format(self.result, self.consumedData, self.remainedData)
    
    @property
    def result(self):
        return self.__result

    @result.setter
    @typeCheck(bool)
    def result(self, result):
        if result is None:
            raise Exception("Result cannot be None")
        self.__result = result
            
        
    @property
    def variable(self):
        """The variable that will be use to parse some content

        :type: :class:`netzob.Model.Vocabulary.Domain.Variables.AbstractVariable`
        """
        return self.__variable

    @variable.setter
    @typeCheck(AbstractVariable)
    def variable(self, variable):
        if variable is None:
            raise ValueError("Variable cannot be None")

        self.__variable = variable

    @property
    def consumedData(self):
        """The consumedData obtained after parsing

        :type: raw
        """
        return self.__consumedData

    @consumedData.setter
    def consumedData(self, consumedData):
        self.__consumedData = consumedData

    @property
    def remainedData(self):
        """The remainedData obtained after parsing

        :type: raw
        """
        return self.__remainedData

    @remainedData.setter
    def remainedData(self, remainedData):
        self.__remainedData = remainedData


    

