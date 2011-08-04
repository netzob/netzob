#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import uuid
import threading
import logging
import re
import struct

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
        self.columnNames = []
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
            self.columnNames = ["Name"]
            return

        # Serialize the messages before sending them to the C library
        typer = TypeIdentifier.TypeIdentifier()
        serialMessages = ""
        format = ""
        maxLeftReducedStringData = 0
        maxRightReducedStringData = 0
        maxReducedSize = 0
        for m in self.getMessages():
            format += str(len(m.getReducedStringData())/2) + "M"
            serialMessages += typer.toBinary( m.getReducedStringData() )
            if m.getLeftReductionFactor()>maxLeftReducedStringData :
                maxLeftReducedStringData = m.getLeftReductionFactor()
            if m.getRightReductionFactor()>maxRightReducedStringData :
                maxRightReducedStringData = m.getRightReductionFactor()
            if m.getReducedSize() > maxReducedSize :
                maxReducedSize = m.getReducedSize()

        # Align sequences in C library
        configParser = ConfigurationParser.ConfigurationParser()
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        (score, aRegex, aMask) = libNeedleman.alignSequences(doInternalSlick, len(self.getMessages()), format, serialMessages)
        
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
        
        if maxLeftReducedStringData > 0 :
            self.log.warning("add on the left part adding a bit of --")
            for i in range(0, maxReducedSize):
                align = "--"+align
        if maxRightReducedStringData > 0 :
            self.log.warning("add on the right part adding a bit of --")
            for i in range(0, maxReducedSize):
                align = align+"--"
            
            
        # Updates the alignment by adding -- on its end
#        if maxReducedStringData > 1 :
#            for i in range(0, (maxReducedStringData*len(align) - len(align))) :
#                align+="--"
            
        
        self.setAlignment( align )
        # Compute and store the regex based on alignment
        self.setRegex(self.extractRegexFromAlignment(align))


        # Fill columnNames with a default name
        self.columnNames = []
        for i in range(len(self.getRegex())):
            self.columnNames.append("Name")
    
    def extractRegexFromAlignment(self, align):
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
        return regex
    
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
        
    def addMessages(self, _messages) :
        for m in _messages:
            self.messages.append(m)
    
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
    #| findSizeFields:
    #|  try to find the size fields of each regex
    #+----------------------------------------------    
    def findSizeFields(self):
        resTable = []
        if len(self.msgByCol) == 0:
            return resTable

        typer = TypeIdentifier.TypeIdentifier()

        # First step: try to find a size field for a uniq data column
        iCol = 0
        for regexElt in self.getRegex():
            if re.match("[0-9a-fA-F]{1,}", regexElt) != None: # Means the element is static
                iCol += 1
                continue
            msgsSize = self.getMessagesFromCol(iCol)
            j = 0
            while j < len(self.getRegex()):
                if not (re.match("\(\.\{,\d+\}\)", self.getRegex()[j]) != None): # Means the element is not purely dynamic
                    j += 1
                    continue
                if j != iCol:
                    msgsData = self.getMessagesFromCol(j)
                    res = True
                    for k in range(len(msgsSize)):
                        # Handle big and little endian for size field of 1, 2 and 4 octets length
                        rawMsgSize = typer.toBinary(msgsSize[k][:8])
                        if len(rawMsgSize) == 1:
                            expectedSizeType = "B"
                        elif len(rawMsgSize) == 2:
                            expectedSizeType = "H"
                        elif len(rawMsgSize) == 4:
                            expectedSizeType = "I"
                        else: # Do not consider size field with len > 4
                            res = False
                            break
                        (expectedSizeLE,) = struct.unpack("<" + expectedSizeType, rawMsgSize)
                        (expectedSizeBE,) = struct.unpack(">" + expectedSizeType, rawMsgSize)
                        if (expectedSizeLE != len(msgsData[k]) / 2) and (expectedSizeBE != len(msgsData[k]) / 2):
                            res = False
                            break
                    if res:
                        resTable.append("In group " + self.name + " : found potential size field (col " + str(iCol) + ") for a data field (col " + str(j) + ")")
                        self.log.info("In group " + self.name + " : found potential size field (col " + str(iCol) + ") for a data field (col " + str(j) + ")")
                j += 1
            iCol += 1

        # Second step: try to find a size field for an aggregate of data columns
        iCol = 0
        for regexElt in self.getRegex():
            if re.match("[0-9a-fA-F]{2,}", regexElt) != None: # Means the element is static
                iCol += 1
                continue
            msgsSize = self.getMessagesFromCol(iCol)
            j = 0
            while j < len(self.getRegex()) - 1:
                # Initialize the aggregate of messages from colJ to colK
                aggregateMsgsData = []
                for l in range(len(msgsSize)):
                    aggregateMsgsData.append( "" )

                # Fill the aggregate of messages and try to compare its length with the current expected length
                k = j + 1
                while k < len(self.getRegex()):
                    for l in range(len(msgsSize)):
                        aggregateMsgsData[l] += self.getMessagesFromCol(k)[l]

                    # We try to aggregate the successive sub-parts of j if it's a static column
                    if self.getRegex()[j].find("{") == -1: # Means the regex j element is static
                        lenJ = len(self.getRegex()[j])
                        stop = 0
                    else:
                        lenJ = 2
                        stop = 0
                    for m in range(lenJ, stop, -2):
                        for n in [1, 2, 4]: # loop over different possible encoding of size field
                            res = True
                            for l in range(len(msgsSize)):
                                if self.getRegex()[j].find("{") == -1: # Means the precedent regex element is static
                                    targetData = self.getRegex()[j][lenJ - m:] + aggregateMsgsData[l]
                                else:
                                    targetData = self.getMessagesFromCol(j)[l] + aggregateMsgsData[l]

                                # Handle big and little endian for size field of 1, 2 and 4 octets length
                                rawMsgSize = typer.toBinary(msgsSize[l][:n*2])
                                if len(rawMsgSize) == 1:
                                    expectedSizeType = "B"
                                elif len(rawMsgSize) == 2:
                                    expectedSizeType = "H"
                                elif len(rawMsgSize) == 4:
                                    expectedSizeType = "I"
                                else: # Do not consider size field with len > 4
                                    res = False
                                    break
                                (expectedSizeLE,) = struct.unpack("<" + expectedSizeType, rawMsgSize)
                                (expectedSizeBE,) = struct.unpack(">" + expectedSizeType, rawMsgSize)
                                if (expectedSizeLE != len(targetData) / 2) and (expectedSizeBE != len(targetData) / 2):
                                    res = False
                                    break
                            if res:
                                if self.getRegex()[j].find("{") == -1: # Means the regex j element is static and a sub-part is concerned
                                    resTable.append("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")")
                                    self.log.info("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")")
                                else:
                                    resTable.append("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")")
                                    self.log.info("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")")
                    k += 1
                j += 1
            iCol += 1

        return resTable

    #+---------------------------------------------- 
    #| Type handling
    #+----------------------------------------------
    def setTypeForCols(self, aType):
        for iCol in range(len(self.getRegex())):
            self.selectedType[iCol] = aType

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
        if iCol < len(self.msgByCol):
            return self.msgByCol[iCol]
        else:
            return None

    def getRepresentation(self, raw, colId) :
        type = self.getSelectedType(colId)
        return self.encode(raw, type)
    
    def encode(self, raw, type):
        typer = TypeIdentifier.TypeIdentifier()
        if type == "ascii" :
            return typer.toASCII(raw)
        elif type == "alphanum" :
            return typer.toAlphanum(raw)
        elif type == "num" :
            return typer.toNum(raw)
        elif type == "alpha" :
            return typer.toAlpha(raw)
        elif type == "base64dec" :
            return typer.toBase64Decoded(raw)
        elif type == "base64enc" :
            return typer.toBase64Encoded(raw)
        else :
            return raw
    
    def storeInXmlConfig(self):
        log = logging.getLogger('netzob.Sequencing.MessageGroup.py')
        
        members = ""
        for message in self.getMessages() :
            members += str(message.getID())+";"
        
        xml  = "<group id=\""+str(self.getID())+"\" name=\""+self.getName()+"\" score=\""+str(self.getScore())+"\" members=\""+members+"\" alignment=\""+self.getAlignment()+"\">\n"
        
        xml += "\t<regex>\n"
        for re in self.getRegex() :
            xml += "\t\t<re>"+re+"</re>\n"
        xml += "\t</regex>\n"
        
        
        xml += "\t<cols>\n"
        for colName in self.getColumnNames() :
            xml += "\t\t<col>"+colName+"</col>\n"
        xml += "\t</cols>\n"
        xml += "</group>\n"
        return xml
        
    
    @staticmethod
    def loadFromXmlConfig(xml, messages):        
        log = logging.getLogger('netzob.Sequencing.MessageGroup.py')
        
        
        
        if not xml.hasAttribute("id") :
            log.warn("Impossible to load group from xml config file (no \"id\" attribute)")
            return None
        if not xml.hasAttribute("name") :
            log.warn("Impossible to load group from xml config file (no \"name\" attribute)")
            return None
        if not xml.hasAttribute("alignment") :
            log.warn("Impossible to load group from xml config file (no \"alignment\" attribute)")
            return None
        if not xml.hasAttribute("score") :
            log.warn("Impossible to load group from xml config file (no \"score\" attribute)")
            return None
        if not xml.hasAttribute("members") :
            log.warn("Impossible to load group from xml config file (no \"members\" attribute)")
            return None
        
        xmlRes = xml.getElementsByTagName("re")
        regex = []
        for xmlRe in xmlRes :
            for node in xmlRe.childNodes:
                re = node.data.split()
            regex.append("".join(re))
        
        xmlCols = xml.getElementsByTagName("col")
        colNames = []
        for xmlCol in xmlCols :
            for node in xmlCol.childNodes:
                colName = node.data.split()
            
            colNames.append("".join(colName))
            
            
        
        group = MessageGroup(xml.attributes["name"].value, [])    
        
        idMessages = xml.attributes["members"].value.split(";")
        for idMessage in idMessages :
            if len(idMessage) > 0 :
                found = False
                
                for message in messages :
                    if str(message.getID()) == idMessage :
                        group.addMessage(message)
                        found = True
                
                if found == False :
                    log.warn("Impossible to load the group since a message is not found.")
                    return None
                
        
        group.setID(xml.attributes["id"].value)
        
        group.setAlignment(xml.attributes["alignment"].value)
        group.setRegex(group.extractRegexFromAlignment(group.getAlignment()))
        group.setScore(xml.attributes["score"].value)
        group.setColumnNames(colNames)
        group.setRegex(regex)
        
        
        return group
    
    
    
    
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
    def getMessageByID(self, messageID):
        for message in self.getMessages():
            if str(message.getID()) == str(messageID):
                return message
        return None
    def getColumnNames(self):
        return self.columnNames

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setID(self, id):
        self.id = id
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
    def setColumnNames(self, columnNames):
        self.columnNames = columnNames
    def setColumnName(self, iCol, value):
        if len(self.columnNames) > iCol:
            self.columnNames[iCol] = value

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
