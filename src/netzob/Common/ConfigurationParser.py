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
import os.path
import logging

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
import ConfigParser
from ResourcesConfiguration import ResourcesConfiguration

#+---------------------------------------------- 
#| ConfigurationParser :
#|     extracts from the configuration file the 
#|     requested value
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ConfigurationParser(object):
    
    # The configuration file path
    # configurationFilePath = NetzobResources.DATA_DIR
    
    #+---------------------------------------------- 
    #| Constructor :
    #+---------------------------------------------- 
    def __init__(self):
        self.configurationFilePath = os.path.join(ResourcesConfiguration.getWorkspace(), "global.conf")
        # If the config file exists we parse it
        # if not we create an in-memory default one
        if self.configurationFilePath != "" or not os.path.isfile(self.configurationFilePath) :
            # create default in memory file
            self.config = ConfigurationParser.createDefault()
            self.config.write(open(self.configurationFilePath, "w"))
        else :
            # Configure the configuration parser
            self.config = ConfigParser.ConfigParser()
            # Parse the configuration file
            self.config.read(self.configurationFilePath)
    
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
        if self.configurationFilePath != "" and os.path.isfile(self.configurationFilePath) :
            self.config.write(open(self.configurationFilePath, "w"))
    
    
    @staticmethod
    def createDefault():
        defaultConfig = ConfigParser.RawConfigParser()
        defaultConfig.add_section('clustering')
        defaultConfig.add_section('traces')
        defaultConfig.add_section('automata')
        defaultConfig.add_section('logging')
        defaultConfig.add_section('import')        
        
        defaultConfig.set('clustering', 'equivalence_threshold', '60')
        defaultConfig.set('clustering', 'orphan_reduction', '0')
        defaultConfig.set('clustering', 'nbiteration', '100')
        defaultConfig.set('clustering', 'do_internal_slick', '0')
        defaultConfig.set('clustering', 'protocol_type', '1')
        
        #defaultConfig.set('traces', 'path', 'resources/traces')
        defaultTraceDirectory = os.path.join(ResourcesConfiguration.getWorkspace(), "traces")
        defaultConfig.set('traces', 'path', defaultTraceDirectory)
        
        #defaultConfig.set('automata', 'path', 'resources/automaton')
        defaultAutomatonDirectory = os.path.join(ResourcesConfiguration.getWorkspace(), "automaton")
        defaultConfig.set('automata', 'path', defaultAutomatonDirectory)
        
        defaultConfig.set('logging', 'path', '')
        
        #defaultConfig.set('import', 'repository_prototypes', 'resources/prototypes/repository.xml')
        defaultConfig.set('import', 'repository_prototypes', '')
        
        return defaultConfig
