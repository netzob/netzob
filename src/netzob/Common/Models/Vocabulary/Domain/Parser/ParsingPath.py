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
from bitarray import bitarray

from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Domain.GenericPath import GenericPath

@NetzobLogger
class ParsingPath(GenericPath):

    def __init__(self, dataToParse, memory, dataAssignedToField=None, dataAssignedToVariable=None, fieldsCallbacks = None, ok = None, parsedData=None):
        super(ParsingPath, self).__init__(memory, dataAssignedToField=dataAssignedToField, dataAssignedToVariable=dataAssignedToVariable, fieldsCallbacks=fieldsCallbacks)        
        self.originalDataToParse = dataToParse.copy()
        if ok is None:
            self.__ok = True
        else:
            self.__ok = ok

    def __str__(self):
        return "ParsingPath ({}, ok={})".format(id(self), self.__ok)

    def validForMessage(self, fields, bitArrayMessage):
        """Checks if the parsing path can represent the provided bitArrayMessage
        under the provided fields."""
        
        parsedMessage = None
        for field in fields:
            if not self.isDataAvailableForField(field):
                return False
            
            if parsedMessage is None:
                parsedMessage = self.getDataAssignedToField(field).copy()
            else:
                parsedMessage += self.getDataAssignedToField(field).copy()

        return parsedMessage == bitArrayMessage

    def duplicate(self):
        dField = {}
        for key, value in self._dataAssignedToField.iteritems():
            dField[key] = value.copy()

        dVariable = {}
        for key, value in self._dataAssignedToVariable.iteritems():
            dVariable[key] = value.copy()

        fCall = [x for x in self._fieldsCallbacks]

        result = ParsingPath(self.originalDataToParse, memory=self.memory.duplicate(), dataAssignedToField = dField, dataAssignedToVariable=dVariable, fieldsCallbacks=fCall, ok=self.ok())
        
        return result
        
        

    def ok(self):
        return self.__ok
        
