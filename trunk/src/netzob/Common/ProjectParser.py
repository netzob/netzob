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
import time
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

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
            filePath = self.projectPath + "/" + file
            if file == '.svn' or file == "config.xml":
                self.log.warning("[INFO] Do not parse file {0}".format(filePath))
            else :
                files.append(file)

        # Parse each file
        for file in files :
            filePath = self.projectPath + "/" + file
            
            # TODO: in futur
            # Retrieves the extension of the files in directory
#            fileExtension = os.path.splitext(filePath)[1]
#            if (fileExtension != ".xml") :
#                self.log.warning("Do not parse file {0} since it's not an xml file (extension {1})".format(filePath, fileExtension))
               
            # Append retrieved message to the final list
            tmpMessages = self.parseFile(filePath)
            # Save the extracted messages in a dedicated group
            group = Group(file, tmpMessages)            
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
        tree = ElementTree.ElementTree()
        tree.parse(filePath)
        xmlMessages = tree.findall("message")
        for xmlMessage in xmlMessages:
            message = AbstractMessageFactory.loadFromXML(xmlMessage)
            messages.append(message)     
        
        self.log.info("Found : {0} messages ".format(len(messages)))
        return messages
        
