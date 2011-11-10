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
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

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
        self.variable = variable
        self.resetCondition = resetCondition
    
    def compare(self, val, indice, negative, dictionary):        
        # first we retrieve the value stored in the variable
        (binvalue, strvalue) = self.variable.getValue(negative, dictionary)
        
        if binvalue == None or self.resetCondition == "force":
            # We execute the learning process
            self.log.info("Variable " + self.variable.getName() + " will be learnt from input.")  
            
            isForced = False
            if self.resetCondition == "force": 
                isForced = True
                          
            new_indice = self.variable.learn(val, indice, isForced, dictionary)
            
            return new_indice
        else :
            self.log.info("Compare " + val[indice:] + " with " + strvalue)
            if val[indice:].startswith(strvalue) :
                self.log.info("Compare successful")                
                return indice + len(strvalue)
            else :
                self.log.info("Compare fail")
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
  
    
    
