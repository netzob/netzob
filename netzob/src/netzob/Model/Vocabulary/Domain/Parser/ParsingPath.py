#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray

from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


class ParsingException(Exception):
    pass


@NetzobLogger
class ParsingPath(GenericPath):
    def __init__(self,
                 dataToParse,
                 memory,
                 dataAssignedToVariable=None,
                 variablesCallbacks=None,
                 ok=None,
                 parsedData=None):
        super(ParsingPath, self).__init__(
            memory,
            dataAssignedToVariable=dataAssignedToVariable,
            variablesCallbacks=variablesCallbacks)
        self.originalDataToParse = dataToParse.copy()
        if ok is None:
            self.__ok = True
        else:
            self.__ok = ok

    def __str__(self):
        return "ParsingPath ({}, ok={})".format(id(self), self.__ok)

    def copy(self):
        dVariable = {}
        for key, value in list(self._dataAssignedToVariable.items()):
            dVariable[key] = value.copy()

        fCall = [x for x in self._variablesCallbacks]

        result = ParsingPath(
            self.originalDataToParse,
            memory=self.memory,
            dataAssignedToVariable=dVariable,
            variablesCallbacks=fCall,
            ok=self.ok)

        return result

    @property
    def ok(self):
        return self.__ok

    @ok.setter  # type: ignore
    def ok(self, ok):
        self.__ok = ok
