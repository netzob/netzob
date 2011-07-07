#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import threading
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
#| MessageGroup :
#|     definition of a group of messages
#| all the messages in the same group must be 
#| considered as equivalent
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class MessageGroup(object):
    
    #+----------------------------------------------
    #| Fields in a group message definition :
    #|     - unique ID
    #|     - name
    #|     - messages
    #+----------------------------------------------
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param name : name of the group
    #| @param messages : list of messages 
    #+----------------------------------------------   
    def __init__(self, name, messages):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.MessageGroup.py')
        self.id = uuid.uuid4() 
        self.name = name
        self.messages = messages
        self.score = 0
        self.regex = ""
        self.alignment = ""

    def __repr__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"

    def __str__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"
    
    #+---------------------------------------------- 
    #| computeScore : given the messages, 
    #| this function computes the score of equivalence
    #| of the group
    #+----------------------------------------------
    def computeScore(self):
        self.log.debug("Compute the score of group {0}".format(self.id))
        alignator = NeedlemanWunsch.NeedlemanWunsch()
        self.score = alignator.computeScore(self.regex)
   
    #+---------------------------------------------- 
    #| computeRegex : given the messages, 
    #| this function computes the regex of the group
    #+----------------------------------------------
    def computeRegex(self):
        innerThread = self.InnerMessageGroup(self) # parameter := the MessageGroup class object
        innerThread.start()
        innerThread.join()
        
    #+---------------------------------------------- 
    #| computeRegex2 : given the messages, 
    #| this function computes the new regex of the group
    #+----------------------------------------------    
    def computeRegex2(self, new_msgs):
        innerThread = self.InnerMessageGroup2(self, new_msgs)
        innerThread.start()
        innerThread.join()
    
    #+---------------------------------------------- 
    #| removeMessage : remove any ref to the given
    #| message and recompute regex and score
    #+----------------------------------------------
    def removeMessage(self, message):
        self.messages.remove(message)
        self.computeRegex()
        self.computeScore()
    
        
    #+---------------------------------------------- 
    #| addMessage : add a message in the list
    #| @param message : the message to add
    #+----------------------------------------------
    def addMessage(self, message):
        self.messages.append(message)
        # Compute the regex
        self.computeRegex()
        # Compute the score
        self.computeScore()
        
    def addMessages(self, _messages) :
        msgs = []
        for msg in _messages :
            found = False
            for message in self.messages :
                if message.getID() == msg.getID():
                    found = True;
            if found == False :
                msgs.append(msg)
        if (self.alignment == "") :
            for m in msgs :
                self.messages.append(m)
            self.computeRegex()
            self.computeScore()
        else :
            self.computeRegex2(msgs)
            self.computeScore()
            
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def getMessages(self):
        return self.messages   
    def getRegex(self):
        return self.regex
    def getAlignment(self):
        return self.alignment
    def getScore(self):
        return self.score


    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setName(self, name):
        self.name = name
    def setMessages(self, messages): 
        self.messages = messages
    def setRegex(self, regex):
        self.regex = regex
    def setAlignment(self, alignment):
        self.alignment = alignment
    def setScore(self, score):
        self.score = score
    #+---------------------------------------------- 
    #| Inner thread for regex computation
    #+----------------------------------------------
    class InnerMessageGroup(threading.Thread):
        #+---------------------------------------------- 
        #| Constructor :
        #| @param group : the manipulated group
        #+----------------------------------------------  
        def __init__(self, group):
            threading.Thread.__init__(self)
            self.group = group

        def run(self):
            alignator = NeedlemanWunsch.NeedlemanWunsch()
            sequences = []
            for message in self.group.getMessages() :
                sequences.append(message.getStringData())
            if (len(sequences) >=2) :
                (regex, alignment) = alignator.getRegex(sequences) 
                self.group.regex = regex
                self.group.alignment = alignment
            else :
                self.group.regex = ""
                self.group.alignment = ""
     
    class InnerMessageGroup2(threading.Thread):
        #+---------------------------------------------- 
        #| Constructor :
        #| @param group : the manipulated group
        #+----------------------------------------------  
        def __init__(self, group, new_msgs):
            threading.Thread.__init__(self)
            self.group = group
            self.new_msgs = new_msgs

        def run(self):
            alignator = NeedlemanWunsch.NeedlemanWunsch()
            sequences = []
            sequences.append(str(self.group.getAlignment()))
            for message in self.new_msgs :
                sequences.append(message.getStringData())
            
            
            if (len(sequences) >=2) :
                (regex, alignment) = alignator.getRegex(sequences) 
                self.group.regex = regex
                self.group.alignment = alignment
            else :
                self.group.regex = ""
                self.group.alignment = ""
