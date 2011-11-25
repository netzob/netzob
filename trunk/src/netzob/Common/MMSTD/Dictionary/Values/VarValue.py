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
from .AbstractValue import AbstractValue


#+---------------------------------------------------------------------------+
#| VarValue :
#|     Represents a var value
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
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
    #| restore :
    #|     Simple !! :) Call this method if you want to forget the last learned value
    #+---------------------------------------------------------------------------+
    def restore(self):
        self.variable.restore()
    
    def compare(self, val, indice, negative, dictionary):        
        # first we retrieve the value stored in the variable
        self.log.debug("compare and so retrieve value of " + str(self.variable))
        
        (binvalue, strvalue) = self.variable.getValue(negative, dictionary)
        
        if binvalue == None or self.resetCondition == "force":
            # We execute the learning process
            self.log.debug("Variable " + self.variable.getName() + " will be learnt from input. (" + str(indice) + ")")  
            
            isForced = False
            if self.resetCondition == "force": 
                isForced = True
                          
            new_indice = self.variable.learn(val, indice, isForced, dictionary)
            
            return new_indice
        else :
            self.log.debug("Compare " + val[indice:] + " with " + strvalue + "[" + ''.join(binvalue) + "]")
            if val[indice:].startswith(''.join(binvalue)) :
                self.log.debug("Compare successful")                
                return indice + len(binvalue)
            else :
                self.log.debug("Compare fail")
        return -1
    
    def send(self, negative, dictionary):        
        (val, strval) = self.variable.getValue(negative, dictionary)
        if val == None or self.resetCondition == "force":
            self.variable.generateValue(negative, dictionary)
            (val, strval) = self.variable.getValue(negative, dictionary)
            
        return (val, strval)
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
  
    
    
