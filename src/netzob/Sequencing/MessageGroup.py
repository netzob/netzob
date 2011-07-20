#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import threading
import logging
import re

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import NeedlemanWunsch
from ..Common import ConfigurationParser, TypeIdentifier

#+---------------------------------------------- 
#| C Imports
#+----------------------------------------------
import libNeedleman

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
        self.regex = []
        self.alignment = ""
        self.selectedType = []
        self.msgByCol = {}

    def __repr__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"

    def __str__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"

    #+---------------------------------------------- 
    #| buildRegexAndAlignment : compute self.regex and 
    #| self.alignment from the binary strings computed 
    #| in the C Needleman library
    #+----------------------------------------------
    def buildRegexAndAlignment(self):
        if len(self.getMessages()) == 1:
            self.regex = [self.getMessages()[0].getStringData()]
            self.align = self.getMessages()[0].getStringData()
            return

        # Serialize the messages before sending them to the C library
        typer = TypeIdentifier.TypeIdentifier()
        serialMessages = ""
        format = ""
        for m in self.getMessages():
            format += str(len(m.getStringData())/2) + "M"
            serialMessages += typer.toBinary( m.getStringData() )

        # Align sequences in C library
        (score, aRegex, aMask) = libNeedleman.alignSequences(len(self.getMessages()), format, serialMessages)
        self.setScore( score )

        # Build alignment C library result
        align = ""
        i = 0
        for c in aMask:
            if c != '\x02':
                if c == '\x01':
                    align += "--"
                else:
                    align += aRegex[i:i+1].encode("hex")
            i += 1
        self.setAlignment( align )

        # Build regex from alignment
        i = 0
        start = 0
        regex = []
        found = False
        for i in range(len(align)) :
            if (align[i] == "-"):                
                if (found == False) :
                    start = i
                    found = True
            else :
                if (found == True) :
                    found = False
                    nbTiret = i - start                                   
                    regex.append( "(.{," + str(nbTiret) + "})")
                    regex.append( align[i] )
                else :
                    if len(regex) == 0:
                        regex.append( align[i] )
                    else:
                        regex[-1] += align[i]
        if (found == True) :
            nbTiret = i - start
            regex.append( "(.{," + str(nbTiret) + "})" )
        self.setRegex( regex )
    
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
    #| getXMLDefinition : 
    #|  returns the XML description of the group
    #| @return a string containing the xml def.
    #+----------------------------------------------
    def getXMLDefinition(self):
        result = "<dictionnary>\n"
        
        result += self.alignment
        
        result += "\n</dictionnary>\n"
        
        return result

    #+---------------------------------------------- 
    #| slickRegex:
    #|  try to make smooth the regex, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegex(self):
        newRegex = self.getRegex()
        res = False
        i = 1
        while i < len(newRegex) - 1:
            if newRegex[i].find("{") == -1: # Means the current element is static
                if len(newRegex[i]) == 2: # Means a potential negligeable element
                    if re.match("\(\.\{,\d+\}\)", newRegex[i-1]) != None: # Means the precedent element is purely dynamic (not complex)
                        if re.match("\(\.\{,\d+\}\)", newRegex[i+1]) != None: # Means the next element is purely dynamic (not complex)
                            res = True
                            elt1 = newRegex.pop(i - 1) # we retrieve the precedent regex
                            elt2 = newRegex.pop(i - 1) # we retrieve the current regex
                            elt3 = newRegex.pop(i - 1) # we retrieve the next regex
                            lenEltResult = int(elt1[4:-2]) + 2 + int(elt3[4:-2]) # We compute the len of the aggregated regex
                            newRegex.insert(i - 1, "(.{," + str(lenEltResult) + "})")
            i += 1

        if res:
            self.setRegex( newRegex )
            self.slickRegex() # Try to loop until no more merges are done
            self.log.debug("The regex has been slicked")

        # TODO: relaunch the matrix step of getting the maxIJ to merge column/row
        # TODO: memorize old regex/align
        # TODO: adapt align

    #+---------------------------------------------- 
    #| Type handling
    #+----------------------------------------------
    def setTypeForCol(self, iCol, aType):
        self.selectedType[iCol] = aType

    def getSelectedType(self, colId):
        if colId>=0 and colId<len(self.selectedType) :
            return self.selectedType[colId]
        else :
            self.log.warning("The type for the column "+str(colId)+" is not defined ! ")
            return "binary"

    def getAllDiscoveredTypes(self, iCol):
        typeIdentifier = TypeIdentifier.TypeIdentifier()        
        return typeIdentifier.getTypes(self.msgByCol[iCol])

    def getMessagesFromCol(self, iCol):
        return self.msgByCol[iCol]

    def getRepresentation(self, raw, colId) :
        type = self.getSelectedType(colId)
        return self.encode(raw, type)
    
    def encode(self, raw, type):
        if type == "ascii" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toASCII(raw)
        elif type == "alphanum" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toAlphanum(raw)
        elif type == "num" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toNum(raw)
        elif type == "alpha" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toAlpha(raw)
        elif type == "base64dec" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toBase64Decoded(raw)
        elif type == "base64enc" :
            typer = TypeIdentifier.TypeIdentifier()
            return typer.toBase64Encoded(raw)
        else :
            return raw
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def getMessages(self):
        return self.messages   
    def getAlignment(self):
        return self.alignment
    def getScore(self):
        return self.score
    def getRegex(self):
        return self.regex

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
