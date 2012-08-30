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
import hashlib

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| MD5Variable:
#|     Definition of an md5 variable defined in a dictionary
#+---------------------------------------------------------------------------+
class MD5Variable(Variable):

    def __init__(self, id, name, init, id_var):
        Variable.__init__(self, id, name, "MD5")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.init = init
        self.id_var = id_var
        self.binVal = None
        self.strVal = None

    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)

    def generateValue(self, negative, dictionary):
        # Retrieve the value of the data to hash
        var = dictionary.getVariableByID(self.id_var)
        (binToHash, strToHash) = var.getValue(negative, dictionary)

        toHash = TypeConvertor.bin2string(binToHash)
        self.log.debug("Will hash the followings : " + toHash)

        md5core = hashlib.md5(self.init)
        md5core.update(toHash)

        md5Hex = md5core.digest()
        self.binVal = TypeConvertor.hex2bin(md5Hex)
        self.strVal = TypeConvertor.bin2strhex(self.binVal)
        self.log.debug("Generated MD5 = " + self.strVal)

    def learn(self, val, indice, isForced, dictionary):

        if self.strVal is None or isForced:
            tmp = val[indice:]
            self.log.debug("Taille MD5 " + str(len(tmp)))
            # MD5 size = 16 bytes = 16*8 = 128
            if (len(tmp) >= 128):
                binVal = tmp[0:128]
                # We verify its realy the MD5
                var = dictionary.getVariableByID(self.id_var)
                (binToHash, strToHash) = var.getValue(False, dictionary)

                toHash = TypeConvertor.bin2string(binToHash)
                self.log.debug("Will hash the followings : " + toHash)

                md5core = hashlib.md5(self.init)
                md5core.update(toHash)

                md5Hex = md5core.digest()

                self.log.debug("We should received an MD5 = " + str(TypeConvertor.hex2bin(md5Hex)))
                self.log.debug("We have received " + str(binVal))

                if (TypeConvertor.hex2bin(md5Hex) == binVal):
                    self.binVal = TypeConvertor.hex2bin(md5Hex)
                    self.strVal = TypeConvertor.bin2strhex(self.binVal)
                    self.log.debug("Perfect, there are equals we return  " + str(len(binVal)))
                    return indice + len(binVal)
                else:
                    return -1

            else:
                return -1

        self.log.debug("value = " + str(self.strVal) + ", isForced = " + str(isForced))
        return -1
