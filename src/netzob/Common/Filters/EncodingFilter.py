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
import uuid
from netzob.Common.Filters.RenderingFilter import RenderingFilter
#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| EncodingFilter :
#|     Class definition of a filter for encoding purposes (format, unit, ...)
#+---------------------------------------------------------------------------+
class EncodingFilter(RenderingFilter):

    TYPE = "EncodingFilter"

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, type, name):
        RenderingFilter.__init__(self, EncodingFilter.TYPE)
        self.type = type
        self.name = name

    #+-----------------------------------------------------------------------+
    #| apply
    #|     Abstract method to apply the filter on a provided message
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def apply(self, message):
        self.log.error("The filter class (" + self.getType() + ") doesn't define 'isValid' !")
        raise NotImplementedError("The filter class (" + self.getType() + ") doesn't define 'isValid' !")

    #+-----------------------------------------------------------------------+
    #| getConversionAddressingTable
    #|     Retrieve a table which describes the conversion addressing
    #+-----------------------------------------------------------------------+
    def getConversionAddressingTable(self, message):
        return None

    #+-----------------------------------------------------------------------+
    #| Getter & Setters
    #+-----------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getName(self):
        return self.name

    def setType(self, type):
        self.type = type

    def setName(self, name):
        self.name = name
