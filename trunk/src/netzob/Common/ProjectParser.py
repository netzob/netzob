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
import time
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Group import Group
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Common.ConfigurationParser import ConfigurationParser

#+---------------------------------------------- 
#| ProjectParser :
#|     Parse the content of project files and retrieve all the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ProjectParser(object):
    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the file to parse 
    #+----------------------------------------------   
    def __init__(self, netzob):
        self.netzob = netzob
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        self.projectPath = projectsDirectoryPath + os.sep + self.netzob.currentProject
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.ProjectParser.py')
       
    #+---------------------------------------------- 
    #| Parse :
    #|     @update the groups paramter with the computed groups of messages
    #+----------------------------------------------   
    def parse(self):
        self.log.info("[INFO] Extract project from directory {0}".format(self.projectPath))
        t1 = time.time()
        groups = []

        # Retrieves all the files to parse
        files = []
        for file in os.listdir(self.projectPath):
            filePath = self.projectPath + os.sep + file
            if file == '.svn' or file == "config.xml":
                self.log.warning("[INFO] Do not parse file {0}".format(filePath))
            else :
                files.append(file)

        # Parse each file
        for file in files :
            filePath = self.projectPath + os.sep + file
            
            # TODO: in futur
            # Retrieves the extension of the files in directory
#            fileExtension = os.path.splitext(filePath)[1]
#            if (fileExtension != ".xml") :
#                self.log.warning("Do not parse file {0} since it's not an xml file (extension {1})".format(filePath, fileExtension))
               
            # Append retrieved message to the final list
            (messages, properties) = self.parseFile(filePath)
            # Save the extracted messages in a dedicated group
            group = Group(file, messages, properties)
            groups.append(group)
        return groups

    #+---------------------------------------------- 
    #| ParseFile :  
    #|  Parse the content of a project files and retrieve all the messages
    #|  @return A list of messages
    #+----------------------------------------------   
    def parseFile(self, filePath):
        self.log.info("Extract trace from file {0}".format(filePath))
        messages = []
        properties = {}
        tree = ElementTree()
        tree.parse(filePath)
        
        # Retrieve each message from the XML
        xmlMessages = tree.findall("messages/message")
        for xmlMessage in xmlMessages:
            message = AbstractMessageFactory.loadFromXML(xmlMessage)
            messages.append(message)

        # Retrieve each envData properties from the XML
        xmlEnvDatas = tree.findall("properties/envData")
        for xmlEnvData in xmlEnvDatas:
            name = xmlEnvData.get('name', "-1")
            value = xmlEnvData.get('value', "-1")
            properties[name] = value.split(";")

        self.log.info("Found : {0} messages ".format(len(messages)))
        return (messages, properties)
        
