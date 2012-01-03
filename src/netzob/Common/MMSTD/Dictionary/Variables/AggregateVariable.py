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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable

#+---------------------------------------------------------------------------+
#| AggregrateVariable :
#|     Definition of an aggregation of variables defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AggregateVariable(Variable):
    
    def __init__(self, id, name, vars):
        Variable.__init__(self, "Aggregate", id, name, True, None)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.vars = vars
    
    
    def getValue(self, negative, dictionary):
        binResult = []
        strResult = []        
        for idVar in self.vars :
            var = dictionary.getVariableByID(int(idVar))
            (binVal, strVal) = var.getValue(negative, dictionary)
            if binVal == None :
                return (None, None)
            else :
                binResult.append(binVal)
                strResult.append(strVal)
        return ("".join(binResult), "".join(strResult))       
    
    def generateValue(self, negative, dictionary):
        for idVar in self.vars :
            var = dictionary.getVariableByID(int(idVar))
            var.generateValue(negative, dictionary)
            
    def learn(self, val, indice, isForced, dictionary):
        new_indice = indice
        for idVar in self.vars :
            var = dictionary.getVariableByID(int(idVar))
            tmp_indice = var.learn(val, new_indice, isForced, dictionary)
            if tmp_indice != -1 :
                new_indice = tmp_indice
        return new_indice
