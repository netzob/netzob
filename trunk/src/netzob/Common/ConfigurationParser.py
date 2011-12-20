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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import os.path
import logging
import ConfigParser

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration

#+---------------------------------------------- 
#| ConfigurationParser :
#|     extracts from the configuration file the 
#|     requested value
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ConfigurationParser(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #+---------------------------------------------- 
    def __init__(self):
        self.configurationFilePath = os.path.join(ResourcesConfiguration.getWorkspaceFile(), ResourcesConfiguration.CONFFILE)
        
        # If the config file exists we parse it
        # if not we create an in-memory default one
        if self.configurationFilePath == None or not os.path.isfile(self.configurationFilePath) :
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
        if self.config.has_section(section) :
            return self.config.getint(section, name)
        else :
            return None
        
    
    def getFloat(self, section, name):
        return self.config.getfloat(section, name)

    #+---------------------------------------------- 
    #| SETTERS
    #+----------------------------------------------     
    def set(self, section, name, value):
        
        if not self.config.has_section(section) :
            self.config.add_section(section)
        
        self.config.set(section, name, value)
        if self.configurationFilePath != "" and os.path.isfile(self.configurationFilePath) :
            self.config.write(open(self.configurationFilePath, "w"))
    
    
    @staticmethod
    def createDefault():
        logging.info("Create a default configuration file")
        defaultConfig = ConfigParser.RawConfigParser()
        defaultConfig.add_section('clustering')
        defaultConfig.add_section('projects')
        defaultConfig.add_section('automata')
        defaultConfig.add_section('logging')
        defaultConfig.add_section('import')        
        
        defaultConfig.set('clustering', 'equivalence_threshold', '60')
        defaultConfig.set('clustering', 'orphan_reduction', '0')
        defaultConfig.set('clustering', 'nbiteration', '100')
        defaultConfig.set('clustering', 'do_internal_slick', '0')
        defaultConfig.set('clustering', 'protocol_type', '1')
        
        defaultTraceDirectory = os.path.join(ResourcesConfiguration.getWorkspaceFile(), "projects")
        defaultConfig.set('projects', 'path', defaultTraceDirectory)
        
        defaultAutomatonDirectory = os.path.join(ResourcesConfiguration.getWorkspaceFile(), "automaton")
        defaultConfig.set('automata', 'path', defaultAutomatonDirectory)
        
        defaultConfig.set('logging', 'path', '')
        
        #defaultConfig.set('import', 'repository_prototypes', 'resources/prototypes/repository.xml')
        defaultConfig.set('import', 'repository_prototypes', '')
        
        return defaultConfig
