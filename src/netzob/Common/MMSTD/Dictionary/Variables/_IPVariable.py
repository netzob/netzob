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
from netzob.Common.MMSTD.Dictionary._Variable import Variable


#+---------------------------------------------------------------------------+
#| IPVariable:
#|     Definition of a n IP variable defined in a dictionary
#+---------------------------------------------------------------------------+
class IPVariable(Variable):

    def __init__(self, id, name, defaultVar):
        Variable.__init__(self, id, name, "IP")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.IPVariable.py')
        if defaultVar == "" or defaultVar is None:
            self.binVal = None
            self.strVal = None
        else:
            self.strVal = defaultVar
            self.binVal = self.string2bin(self.strVal)

    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)

    def string2bin(self, aStr):
        chars = []
        for c in aStr:
            v = str(hex(ord(c))).replace("0x", "")
            if len(str(v)) != 2:
                v = "0" + str(v)
            chars.append(v)

    def generateValue(self, negative, dictionary):
        # NOT YET GENERATED
        self.strVal = "192.168.0.10"
        self.binVal = self.string2bin(self.strVal)

    def learn(self, val, indice, isForced, dictionary):
        self.log.debug("Received : " + str(val))

        if self.strVal is None or isForced:
            tmp = val[indice:]

            res = ""
            i = 0
            finish = False
            while not finish:
                v = int(tmp[i: i + 2], 16)
                if v > 0x21 and v <= 0x7e:
                    res += chr(v)
                    i = i + 2
                else:
                    finish = True

            if i > 0:
                self.strVal = res
                self.log.debug("value = " + str(self.strVal) + ", isForced = " + str(isForced))
                self.binVal = self.string2bin(self.strVal)

                return indice + i

        return -1
