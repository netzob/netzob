# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| Token:
#|     Definition of a token
#+---------------------------------------------------------------------------+

class Token():
    def __init__(self, format, length, type, value):
        self.format = format
        self.setType(type)
        self.length = int(length)
        self.value = value

    def __str__(self):
        return str(self.format) + "_" + str(self.length) + "_" + str(self.type) + "_" + TypeConvertor.pythonRawToNetzobRaw(str(self.value))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            sameFormat = (self.format == other.getFormat())
            sameType = (self.type == other.getType())
            isSub = True
            if not sameType or (sameType and self.type == "variable"):
                if self.length <= other.getLength():
                    isSub = (other.getValue().find(self.value) > -1)
                else:
                    isSub = (self.value.find(other.getValue()) > -1)
            return (sameFormat)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

#+---------------------------------------------------------------------------+
#| Getters
#+---------------------------------------------------------------------------+
    def getFormat(self):
        return self.format

    def getLength(self):
        return self.length

    def getType(self):
        return self.type

    def getValue(self):
        return self.value

#+---------------------------------------------------------------------------+
#| Setters
#+---------------------------------------------------------------------------+
    def setType(self, type):
        if type in ["variable", "constant"]:
            self.type = type
