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
from netzob.Common.MMSTD.Dictionary.Values.AbstractValue import AbstractValue


#+---------------------------------------------------------------------------+
#| VarValue:
#|     Represents a var value
#+---------------------------------------------------------------------------+
class VarValue(AbstractValue):

    def __init__(self, variable, resetCondition):
        AbstractValue.__init__(self, "VarValue")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.VarValue.py')
        self.log.debug("VarValue : " + str(variable))
        self.variable = variable
        self.resetCondition = resetCondition

    #+---------------------------------------------------------------------------+
    #| restore:
    #|     Simple !! :) Call this method if you want to forget the last learned value
    #+---------------------------------------------------------------------------+
    def restore(self):
        self.variable.restore()

    def compare(self, val, indice, negative, dictionary):
        # first we retrieve the value stored in the variable
        self.log.debug("compare and so retrieve value of " + str(self.variable))

        (binvalue, strvalue) = self.variable.getValue(negative, dictionary)

        if binvalue is None or self.resetCondition == "force":
            # We execute the learning process
            self.log.debug("Variable " + self.variable.getName() + " will be learnt from input. (" + str(indice) + ")")

            isForced = False
            if self.resetCondition == "force":
                isForced = True

            new_indice = self.variable.learn(val, indice, isForced, dictionary)

            return new_indice
        else:
            self.log.debug("Compare " + val[indice:] + " with " + strvalue + "[" + ''.join(binvalue) + "]")
            if val[indice:].startswith(''.join(binvalue)):
                self.log.debug("Compare successful")
                return indice + len(binvalue)
            else:
                self.log.debug("Compare fail")
        return -1

    def send(self, negative, dictionary):
        (val, strval) = self.variable.getValue(negative, dictionary)
        if val is None or self.resetCondition == "force":
            self.variable.generateValue(negative, dictionary)
            (val, strval) = self.variable.getValue(negative, dictionary)

        return (val, strval)

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
