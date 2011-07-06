#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import threading

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import NeedlemanWunsch

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
       self.id = uuid.uuid4() 
       self.name = name
       self.messages = messages
       self.score = 0
       self.regex = ""

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
        #print "[Debug] Compute the score of group {0}".format(self.id)
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
        for msg in _messages :
            found = False
            for message in self.messages :
                if message.getID() == msg.getID() :
                    found = True;
            if found == False :
                 self.messages.append(message)
        # Compute the regex
        self.computeRegex()
        # Compute the score
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
    def getScore(self):
        return self.score


    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setName(self, name):
        self.name = name
    def setMessages(self, messages): 
        self.messages = messages
    
    #+---------------------------------------------- 
    #| Inner thread for huge calcul
    #+----------------------------------------------
    class InnerMessageGroup(threading.Thread):
        def __init__(self, mg):
            threading.Thread.__init__(self)
            self.mg = mg

        def run(self):
            ## Run huge calcul
            #print "[Debug] Compute the regex of group {0}".format(self.mg.id)
            alignator = NeedlemanWunsch.NeedlemanWunsch()
            sequences = []
            for message in self.mg.messages :
                sequences.append(message.getStringData())
        
            self.mg.regex = alignator.getRegex(sequences) 
            #print "[Debug] regex = {0}".format(self.mg.regex)
        
