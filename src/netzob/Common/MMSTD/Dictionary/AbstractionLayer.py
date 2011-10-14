#!/usr/bin/python
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
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractionLayer :
#|     Definition of an abstractionLayer
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractionLayer():
    
    def __init__(self, input, output, dictionary):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.AbstractionLayer.py')
        self.input = input
        self.output = output
        self.dictionary = dictionary
        
    
    def receiveSymbol(self):
        # First we read from the input the message
        receivedData = self.rfile.readline().strip()
        
        
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    
    
    
