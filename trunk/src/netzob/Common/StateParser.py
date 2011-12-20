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
#| Global Imports
#+----------------------------------------------
import logging
from lxml.etree import ElementTree

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Common.GroupFactory import GroupFactory

#+---------------------------------------------- 
#| ConfigParser :
#|     XML parser for saved modelization operations
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class StateParser(object):
    
    #+---------------------------------------------- 
    #| Constructor : 
    #+----------------------------------------------   
    def __init__(self, configFile):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.StateParser.py')
        self.configFile = configFile
        self.groups = []
        
    #+---------------------------------------------- 
    #| saveInConfiguration :
    #|    Dump in self.configFile the current configuration
    #|    of the analysis
    #| @param groups: list of the groups to save 
    #+----------------------------------------------    
    def saveInConfiguration(self, groups):
        self.log.info("Save configuration in file {0}".format(self.configFile))
        messages = []
        
        xml = "<netzob>\n"
        xml += "\t<groups>\n"
        for group in groups :
            xml += GroupFactory.saveInXML(group) + "\n"
            for message in group.getMessages() :
                messages.append(message)
        xml += "\t</groups>\n"
        xml += "\t<datas>\n";
        
        for message in messages :
            xml += "\t\t" + AbstractMessageFactory.saveInXML(message) + "\n"
        xml += "\t</datas>\n"
        xml += "</netzob>"
        
        self.log.debug("The generated configuration file is : " + xml)
        
        file = open(self.configFile, 'w')
        file.write(xml)
        file.close()
       
        self.log.debug("Configuration successfully saved.")
        
    #+---------------------------------------------- 
    #| loadConfiguration :
    #|    Load self.configFile and parse its content
    #|    in order to retrieve the group definitions
    #| @return the extracted groups 
    #+----------------------------------------------
    def loadConfiguration(self):
        self.log.info("Extract configuration from file {0}".format(self.configFile))
        
        messages = []
        
        # Parse the config file associated
        configTree = ElementTree()
        configTree.parse(self.configFile)  
        # Retrieves the root of the config file
        rootConfigTree = configTree.getroot()
        for xmlData in rootConfigTree.findall("datas/message") :
            message = AbstractMessageFactory.loadFromXML(xmlData)
            if message != None :
                messages.append(message)
        
        # parse all the declared groups
        for xmlGroup in rootConfigTree.findall("groups/group") :
            group = GroupFactory.loadFromXML(xmlGroup, messages)
            if group != None :
                self.groups.append(group)

        self.log.debug("Found in config file : {0} messages ".format(len(messages)))
        self.log.debug("Found in config file : {0} groups ".format(len(self.groups)))
        return self.groups
        
    #+---------------------------------------------- 
    #| GETTERS & SETTERS
    #+----------------------------------------------    
    def getGroups(self):
        return self.groups
