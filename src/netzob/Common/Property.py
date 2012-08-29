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
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Property:
#|     Definition of an object (project, symbol, message, etc.) property
#+---------------------------------------------------------------------------+
class Property(object):
    def __init__(self, name, format, currentValue):
        self.name = name
        self.format = format
        self.currentValue = currentValue
        self.possibleValues = []
        self.isEditable = False
        self.hasEntry = False
        self.log = logging.getLogger(__name__)

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getName(self):
        return self.name

    def getFormat(self):
        return self.format

    def getCurrentValue(self):
        return self.currentValue

    def getPossibleValues(self):
        return self.possibleValues

    def isEditable(self):
        return self.isEditable

    def hasEntry(self):
        return self.hasEntry

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setName(self, name):
        self.name = name

    def setFormat(self, format):
        self.format = format

    def setCurrentValue(self, currentValue):
        self.currentValue = currentValue

    def setPossibleValues(self, possibleValues):
        self.possibleValues = possibleValues

    def setIsEditable(self, isEditable):
        self.isEditable = isEditable

    def setHasEntry(self, hasEntry):
        self.hasEntry = hasEntry
