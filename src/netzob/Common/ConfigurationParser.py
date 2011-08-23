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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
import ConfigParser

#+---------------------------------------------- 
#| ConfigurationParser :
#|     extracts from the configuration file the 
#|     requested value
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ConfigurationParser(object):
    
    #A really useful function.

    # The configuration file path
    configurationFilePath = "resources/global.conf"
    
    #+---------------------------------------------- 
    #| Constructor :
    #+---------------------------------------------- 
    def __init__(self):
        # Configure the configuration parser
        self.config = ConfigParser.ConfigParser()
        # Parse the configuration file
        self.config.read(ConfigurationParser.configurationFilePath)
    
    #+---------------------------------------------- 
    #| get :
    #|     computes the requested value from the 
    #|    requested section
    #| @param section : the section in config file
    #| @param value: the value in the section
    #| @return the requested value
    #+---------------------------------------------- 
    def get(self, section, name):
        if self.config.has_section(section) :
            return self.config.get(section, name)
        else :
            return None
    
    def getInt(self, section, name):
        return self.config.getint(section, name)
    
    def getFloat(self, section, name):
        return self.config.getfloat(section, name)

    #+---------------------------------------------- 
    #| SETTERS
    #+----------------------------------------------     

    def set(self, section, name, value):
        self.config.set(section, name, value)
        self.config.write(open(ConfigurationParser.configurationFilePath, "w"))
