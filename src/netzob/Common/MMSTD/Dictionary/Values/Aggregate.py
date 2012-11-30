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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Values.AbstractValue import AbstractValue


#+---------------------------------------------------------------------------+
#| Aggregate:
#|     Definition of an aggregation
#+---------------------------------------------------------------------------+
class Aggregate(AbstractValue):

    def __init__(self):
        AbstractValue.__init__(self, "Aggregate")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.Aggregate.py')

        self.values = []

    def registerValue(self, value):
        self.values.append(value)

    def send(self, negative, dictionary):
        binResult = bitarray(endian='big')
        strResult = []
        for value in self.values:
            (binVal, strVal) = value.send(negative, dictionary)
            self.log.debug("Aggregate : " + str(binVal) + " [" + str(strVal) + "]")
            binResult.extend(binVal)
            strResult.append(strVal)

        return (binResult, "".join(strResult))

    def compare(self, val, indice, negative, dictionary):
        result = indice
        self.log.debug("Will compare with:")
        for value in self.values:
            self.log.debug(str(value.getType()))

        for value in self.values:
            self.log.debug("Indice = {0}: {1}".format(str(result), value.getType()))
            result = value.compare(val, result, negative, dictionary)
            if result == -1 or result is None:
                self.log.debug("Compare fail")
                return -1
            else:
                self.log.debug("Compare successfull")

        return result

    def restore(self):
        for value in self.values:
            value.restore()

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setType(self, type):
        self.type = type
