#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import xml.dom.minidom
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import Message
from ..Common import ConfigurationParser


#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TraceParser :
#|     parse the content of a trace file and retrives all the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TraceParser(object):
    #+---------------------------------------------- 
    #| Constructor :NeedemanWunsch
    #| @param path: path of the file to parse 
    #+----------------------------------------------   
    def __init__(self, path):
        self.path = path
        self.messages = []
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TraceParser.py')
       
    #+---------------------------------------------- 
    #| Parse :  
    #+----------------------------------------------   
    def parse(self):
        self.log.info("Extract traces from file {0}".format(self.path))
        
        dom = xml.dom.minidom.parse(self.path)
        xmlMessages = dom.getElementsByTagName("data")
        for xmlMessage in xmlMessages:
            
            # create a new message for each entry
            message = Message.Message()
            message.setProtocol(xmlMessage.attributes["proto"].value)
            message.setIPSource(xmlMessage.attributes["sourceIp"].value)
            message.setIPTarget(xmlMessage.attributes["targetIp"].value)
            message.setL4SourcePort(xmlMessage.attributes["sourcePort"].value)
            message.setL4TargetPort(xmlMessage.attributes["targetPort"].value)
            message.setTimestamp(xmlMessage.attributes["timestamp"].value)
            for node in xmlMessage.childNodes:
                message.setData(node.data.split())
            self.messages.append(message)     
        
        self.log.info("Found : {0} messages ".format(len(self.messages)))
        return self.messages  
        
