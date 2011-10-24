#!/usr/bin/ python
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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
from pylab import figure, show

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| Searcher :
#|     Provides multiple algorithms for a searching after a pattern in a 
#|     set of computed messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Searcher(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param messages the list of messages it will search in
    #+----------------------------------------------   
    def __init__(self, messages):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Searcher.py')
        self.messages = messages
    
    #+---------------------------------------------- 
    #| searchBinary :
    #|   search for a value provided in Binary
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchBinary(self, value):
        return None
    
    #+---------------------------------------------- 
    #| searchOctal :
    #|   search for a value provided in octal
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchOctal(self, value):
        return None
    
    #+---------------------------------------------- 
    #| searchHexadecimal :
    #|   search for a value provided in hex
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchHexadecimal(self, value):
        return None
    
    #+---------------------------------------------- 
    #| searchASCII :
    #|   search for a value provided in ASCII
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchASCII(self, value):
        return None
    
    #+---------------------------------------------- 
    #| searchIP :
    #|   search for a value provided in IP
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchIP(self, value):
        return None
        


