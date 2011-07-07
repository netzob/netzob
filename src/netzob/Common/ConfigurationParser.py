#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
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
        return self.config.get(section, name)
    
        