#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import re
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import NeedlemanWunsch
from ..Common import ConfigurationParser

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| Message :
#|     definition of a message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Message(object):
    
    #+----------------------------------------------
    #| Fields in message definition :
    #|     - unique ID
    #|     - protocol
    #|     - IP source
    #|     - IP target
    #|     - L4 source port
    #|     - L4 target port
    #|     - timestamp
    #|     - data
    #+----------------------------------------------
    
    #+---------------------------------------------- 
    #| Constructor : 
    #+----------------------------------------------   
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.Message.py')
        self.id = uuid.uuid4() 
        self.protocol = ""
        self.ipSource = ""
        self.ipTarget = ""
        self.l4SourcePort = -1
        self.l4TargetPort = -1
        self.timestamp = -1
        self.data = ""
        self.rightReductionFactor = 0
        self.leftReductionFactor = 0
        self.group = None
    
    #+---------------------------------------------- 
    #|`getStringData : compute a string representation
    #| of the data 
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        return "".join(self.data)
    
    def getReducedSize(self):
        start = 0
        end = len(self.getStringData())
        
        if self.getLeftReductionFactor()>0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end-start)%2 == 1 :
                start=start-1
        if self.getRightReductionFactor()>0 :
            end   = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end-start)%2 == 1 :
                end=end+1 
        
        if (end-start)%2 == 1 :
            end=end+1 
            
        return len(self.getStringData()) - (end-start)
    
    def getReducedStringData(self):        
        start = 0
        end = len(self.getStringData())        
        if self.getLeftReductionFactor()>0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end-start)%2 == 1 :
                start=start-1 
        if self.getRightReductionFactor()>0 :
            end   = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end-start)%2 == 1 :
                end=end+1
        return "".join(self.getStringData()[start:end]) 
    
    def storeInXmlConfig(self):
        log = logging.getLogger('netzob.Sequencing.Message.py')
        xml  = "<data id=\""+str(self.getID())+"\" timestamp=\""+self.getTimestamp()+"\" " 
        xml += "rightReductionFactor=\""+str(self.getRightReductionFactor())+"\" leftReductionFactor=\""+str(self.getLeftReductionFactor())+"\">"
        xml += self.getStringData()
        xml += "</data>\n" 
        return xml
    
    @staticmethod
    def loadFromXmlConfig(xml):        
        log = logging.getLogger('netzob.Sequencing.Message.py')
        message = Message()
        
        if not xml.hasAttribute("id") :
            log.warn("Impossible to load message from xml config file (no \"id\" attribute)")
            return None
        if not xml.hasAttribute("timestamp") :
            log.warn("Impossible to load message from xml config file (no \"timestamp\" attribute)")
            return None
        if not xml.hasAttribute("rightReductionFactor") :
            log.warn("Impossible to load message from xml config file (no \"rightReductionFactor\" attribute)")
            return None
        if not xml.hasAttribute("leftReductionFactor") :
            log.warn("Impossible to load message from xml config file (no \"leftReductionFactor\" attribute)")
            return None
        
        message.setID(xml.attributes["id"].value)
        message.setTimestamp(xml.attributes["timestamp"].value)
        message.setRightReductionFactor(int(xml.attributes["rightReductionFactor"].value))
        message.setLeftReductionFactor(int(xml.attributes["leftReductionFactor"].value))
        
        for node in xml.childNodes:
            message.setData(node.data.split())
        
        return message

    #+---------------------------------------------- 
    #| applyRegex: apply the current regex on the message
    #|  and return a table
    #+----------------------------------------------
    def applyRegex(self, styled=False, encoded=False):
        regex = []
        for col in self.group.getColumns():
            regex.append( col['regex'] )
        compiledRegex = re.compile("".join( regex ))
        data = self.getStringData()
        m = compiledRegex.match(data)
        if m == None:
            self.log.warning("The regex of the group doesn't match one of its message")
            return [ self.getStringData() ]
        res = []
        iCol = 0
        dynamicCol = 1
        for col in self.group.getColumns():
            if col['regex'].find("(") != -1: # Means this column is not static
                start = m.start(dynamicCol)
                end = m.end(dynamicCol)
                if self.group.getColorByCol(iCol) == "":
                    color = 'blue'
                else:
                    color = self.group.getColorByCol(iCol)
                if styled:
                    if encoded:
                        res.append( '<span foreground="'+color+'" font_family="monospace">' + self.group.getRepresentation( data[start:end], iCol ) + '</span>' )
                    else:
                        res.append( '<span foreground="'+color+'" font_family="monospace">' + data[start:end] + '</span>' )
                else:
                    if encoded:
                        res.append( self.group.getRepresentation( data[start:end], iCol ) )
                    else:
                        res.append( data[start:end] )
                dynamicCol += 1
            else:
                if styled:
                    if encoded:
                        res.append( '<span>' + self.group.getRepresentation( col['regex'], iCol ) + '</span>')
                    else:
                        res.append( '<span>' + col['regex'] + '</span>')
                else:
                    if encoded:
                        res.append( self.group.getRepresentation( col['regex'], iCol ) )
                    else:
                        res.append( col['regex'] )
            iCol = iCol + 1
        return res

    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getID(self):
        return self.id
    def getProtocol(self):
        return self.protocol
    def getIPSource(self):
        return self.ipSource
    def getIPTarget(self):
        return self.ipTarget
    def getL4SourcePort(self):
        return self.l4SourcePort
    def getL4TargetPort(self):
        return self.l4TargetPort
    def getTimestamp(self):
        return self.timestamp
    def getData(self):
        return self.data   
    def getRightReductionFactor(self):
        return self.rightReductionFactor
    def getLeftReductionFactor(self):
        return self.leftReductionFactor
    def getGroup(self):
        return self.group
       
    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setProtocol(self, protocol):
        self.protocol = protocol
    def setIPSource(self, ipSource):
        self.ipSource = ipSource
    def setIPTarget(self, ipTarget):
        self.ipTarget = ipTarget
    def setL4SourcePort(self, l4sourcePort):
        self.l4SourcePort = l4sourcePort
    def setL4TargetPort(self, l4targetPort):
        self.l4TargetPort = l4targetPort
    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
    def setData(self, data):
        self.data = data   
    def setRightReductionFactor(self, factor):
        self.rightReductionFactor = factor
        self.leftReductionFactor = 0
    def setLeftReductionFactor(self, factor):
        self.leftReductionFactor = factor
        self.rightReductionFactor = 0
    def setID(self, id):
        self.id = id
    def setGroup(self, group):
        self.group = group
