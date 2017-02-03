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
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath

@NetzobLogger
class VariableParser(object):
    """This class can be use to parse some data against the specification of a domain

    """

    def __init__(self, variable):
        self.variable = variable

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parses the specified content (in the parsingPath) against the variable"""
        if parsingPath is None:
            raise Exception("Parsing path cannot be None")
        if self.variable is None:
            raise Exception("Variable cannot be None")
        
        
        dataToParse = parsingPath.getDataAssignedToVariable(self.variable)
        self._logger.debug("Parse '{0}' with variable '{1}' specifications".format(dataToParse, self.variable))

        return self.variable.parse(parsingPath, carnivorous=carnivorous)

    @property
    def variable(self):
        """The variable that will be use to parse some content

        :type: :class:`netzob.Model.Vocabulary.Domaoin.Variables.AbstractVariable.AbstractVariable`
        """
        return self.__variable

    @variable.setter
    @typeCheck(AbstractVariable)
    def variable(self, variable):
        if variable is None:
            raise ValueError("Variable cannot be None")

        self.__variable = variable

