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
class VariableSpecializerResult():
    """This class denotes one specializer result of a variable
    
    """

    def __init__(self, variable, result, generatedContent):
        self.variable = variable
        self.result = result
        self.generatedContent = generatedContent

    def isOk(self):
        """Returns True if this results is True"""
        return self.result

    def __str__(self):
        return "VarSpecializerResult (result={0}, generatedContent={1})".format(self.result, self.generatedContent)
    
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
    def generatedContent(self):
        """The generatedContent obtained after parsing

        :type: raw
        """
        return self.__generatedContent

    @generatedContent.setter
    def generatedContent(self, generatedContent):
        self.__generatedContent = generatedContent


    

