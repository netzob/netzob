#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import re
import logging
import xml.dom.minidom


#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
import Message
import MessageGroup

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| ConfigParser :
#|     XML parser for saved sequencing operations
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ConfigParser(object):
    
    #+---------------------------------------------- 
    #| Constructor : 
    #+----------------------------------------------   
    def __init__(self, configFile):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.ConfigParser.py')
        self.configFile = configFile
        self.groups = []
        
        
    def saveInConfiguration(self, groups):
        self.log.info("Save configuration in file {0}".format(self.configFile))
        messages = []
        
        xml = "<netzob>\n"
        xml += "\t<groups>\n"
        for group in groups :
            xml += group.storeInXmlConfig()+"\n"
            for message in group.getMessages() :
                messages.append(message)
        xml += "\t</groups>\n"
        xml += "\t<datas>\n";
        
        for message in messages :
            xml += "\t\t"+message.storeInXmlConfig()
        xml += "\t</datas>\n"
        xml += "</netzob>"
        
        file = open(self.configFile, 'w')
        file.write(xml)
        file.close()
        
        
        print xml
        
    
    def loadConfiguration(self):
        self.log.info("Extract configuration from file {0}".format(self.configFile))
        
        messages = []
        
        
        dom = xml.dom.minidom.parse(self.configFile)
        # parse all the declared messages
        xmlDatas = dom.getElementsByTagName("data")
        for data in xmlDatas :
            message = Message.Message.loadFromXmlConfig(data)
            if message != None :
                messages.append(message)
        
        # parse all the declared groups
        xmlGroups = dom.getElementsByTagName("group")
        for xmlGroup in xmlGroups :
            group = MessageGroup.MessageGroup.loadFromXmlConfig(xmlGroup, messages)
            if group != None :
                self.groups.append(group)
            
            
        
        self.log.info("Found : {0} messages ".format(len(messages)))
        self.log.info("Found : {0} groups ".format(len(self.groups)))
        return self.groups
        
        
    def getGroups(self):
        return self.groups
   
   