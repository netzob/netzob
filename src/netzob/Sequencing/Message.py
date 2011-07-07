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
        self.id = uuid.uuid4() 
        self.protocol = ""
        self.ipSource = ""
        self.ipTarget = ""
        self.l4SourcePort = -1
        self.l4TargetPort = -1
        self.timestamp = -1
        self.data = ""
        
    
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
        result = data
        compiledRegex = re.compile(regex)
        m = compiledRegex.match(data)
    
        if (m == None) :
            logger.error("The regex of the group doesn't match one of its message")
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
#        i_regex = 0
#        for i_data in range(0, len(data)) :
#            
        
        
    
    #+---------------------------------------------- 
    #|`getStringData : compute a string representation
    #| of the data 
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        return "".join(self.data) 
    
    
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
       
    
       
