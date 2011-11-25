# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging.config

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..Variable import Variable

#+---------------------------------------------------------------------------+
#| AggregrateVariable :
#|     Definition of an aggregation of variables defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AggregateVariable(Variable):
    
    def __init__(self, id, name, vars):
        Variable.__init__(self, id, name, "AGGREGATE")
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
