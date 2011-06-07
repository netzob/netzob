#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import xml.dom.minidom

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import Message

#+---------------------------------------------- 
#| TraceParser :
#|     parse the content of a trace file and retrives all the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TraceParser(object):
    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the file to parse 
    #+----------------------------------------------   
    def __init__(self, path):
       self.path = path
       self.messages = []
       
    #+---------------------------------------------- 
    #| Parse :  
    #+----------------------------------------------   
    def parse(self):
        print "[INFO] Extract traces from file {0}".format(self.path)
        
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
        
        print "Found : {0} messages ".format(len(self.messages))    
        return self.messages  
        
