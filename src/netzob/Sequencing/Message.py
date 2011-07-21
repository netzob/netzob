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

        
        
    
    #+---------------------------------------------- 
    #|`getPangoData : compute a colored representation    
    #|  following the given regex
    #| @param regex : the regex which colors the text
    #| @return string(data)
    #+----------------------------------------------
    def getPangoData(self, regex):
        # Compute the score of the regex
        needle = NeedlemanWunsch.NeedlemanWunsch()
        score = needle.computeScore(regex)

        # if score > 75 : apply regex
        if (score < 75) :
            return self.getStringData()
        
        data = self.getStringData()
        compiledRegex = re.compile(regex)
        m = compiledRegex.match(data)
    
        if (m == None) :
            self.log.warning("The regex of the group doesn't match one of its message")
            return self.getStringData()
        
        
        result = ""
        current = 0
        
        nbGroup = len(m.groups())
        
        for i_group in range(1, nbGroup+1) :
            start = m.start(i_group)
            end = m.end(i_group)
            
            result += '<span >' + data[current:start] + '</span>'
            result += '<span foreground="blue" font_family="monospace" >' + data[start:end] + '</span>'
            
            current = end
        
        return result
    
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
