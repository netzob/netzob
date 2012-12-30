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
import random
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary._Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| DynLenStringVariable:
#|     Definition of a dynamic sized string variable defined in a dictionary
#+---------------------------------------------------------------------------+
class DynLenStringVariable(Variable):

    def __init__(self, id, name, idVar):
        Variable.__init__(self, id, name, "DynLenString")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.WordVariable.py')
        self.idVar = idVar
        self.binVal = None
        self.strVal = None

    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)

    def generateValue(self, negative, dictionary):

        variable = dictionary.getVariableByID(self.idVar)
        (binValue, strValue) = variable.getValue(negative, dictionary)

        self.log.debug("GENERATE VALUE of size : " + str(binValue))
        nb_letter = TypeConvertor.bin2int(binValue)
        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
        self.binVal = TypeConvertor.string2bin(self.strVal, 'big')
        self.log.debug("Generated value = " + self.strVal)
        self.log.debug("Generated value = " + str(self.binVal))

    def learn(self, val, indice, isForced, dictionary):
        self.log.debug("LEARN")
        variable = dictionary.getVariableByID(self.idVar)
        (binValue, strValue) = variable.getValue(False, dictionary)
        nb_letter = TypeConvertor.bin2int(binValue) * 8
        self.log.debug("nb_letter = " + str(nb_letter))
        tmp = val[indice:]
        self.log.debug("tmp size : " + str(len(tmp)))
        if (len(tmp) >= nb_letter):
            self.binVal = tmp[:nb_letter]
            self.strVal = TypeConvertor.bin2string(self.binVal)
            self.log.debug("Value learnt : " + self.strVal)
            return indice + nb_letter

        return -1
