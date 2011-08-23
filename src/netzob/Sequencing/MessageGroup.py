#!/usr/bin/ python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

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
        for message in self.messages:
            message.setGroup(self)
        self.score = 0
        self.alignment = ""
        self.columns = [] # each column element contains a dict : {'name', 'regex', 'selectedType', 'tabulation', 'description', 'color'}

    def __repr__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"

    def __str__(self, *args, **kwargs):
        return self.name+"("+str(round(self.score,2))+")"

    def clear(self):
        self.columns = []
        self.alignment = ""
        del self.messages[:]

    #+---------------------------------------------- 
    #| buildRegexAndAlignment : compute regex and 
    #| self.alignment from the binary strings computed 
    #| in the C Needleman library
    #+----------------------------------------------
    def buildRegexAndAlignment(self):
        self.log.debug("Build the regex and alignement of the group " + str(self.getID()))
        # Use the default protocol type for representation
        configParser = ConfigurationParser.ConfigurationParser()
        valID = configParser.getInt("clustering", "protocol_type")
        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"

        self.columns = []
        if len(self.getMessages()) == 1:
            self.columns.append({'name' : "Name",
                                  'regex' : self.getMessages()[0].getStringData(),
                                 'selectedType' : aType,
                                 'tabulation' : 0,
                                 'description' : "",
                                 'color' : ""
                                 })
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
        # Initialized the self.columns structure based on alignement
        self.buildRegexFromAlignment(align)
    
    def buildRegexFromAlignment(self, align):
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

        # Use the default protocol type for representation
        configParser = ConfigurationParser.ConfigurationParser()
        valID = configParser.getInt("clustering", "protocol_type")
        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"

        for regexElt in regex:
            self.columns.append({'name' : "Name",
                                 'regex' : regexElt,
                                 'selectedType' : aType,
                                 'tabulation' : 0,
                                 'description' : "",
                                 'color' : ""
                                 })
   
    #+---------------------------------------------- 
    #| removeMessage : remove any ref to the given
    #| message and recompute regex and score
    #+----------------------------------------------
    def removeMessage(self, message):
        self.messages.remove(message)
        
    #+---------------------------------------------- 
    #| addMessage : add a message in the list
    #| @param message : the message to add
    #+----------------------------------------------
    def addMessage(self, message):
        message.setGroup(self)
        self.messages.append( message )
        
    def addMessages(self, messages):
        for message in messages:
            message.setGroup(self)
            self.messages.append( message )
    
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
        # Use the default protocol type for representation
        configParser = ConfigurationParser.ConfigurationParser()
        valID = configParser.getInt("clustering", "protocol_type")
        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"

        res = False
        i = 1
        while i < len(self.columns) - 1:
            if self.isRegexStatic( self.columns[i]['regex'] ):
                if len(self.columns[i]['regex']) == 2: # Means a potential negligeable element
                    if self.isRegexOnlyDynamic( self.columns[i-1]['regex'] ):
                        if self.isRegexOnlyDynamic( self.columns[i+1]['regex'] ):
                            res = True
                            col1 = self.columns.pop(i - 1) # we retrieve the precedent regex
                            col2 = self.columns.pop(i - 1) # we retrieve the current regex
                            col3 = self.columns.pop(i - 1) # we retrieve the next regex
                            lenColResult = int(col1['regex'][4:-2]) + 2 + int(col3['regex'][4:-2]) # We compute the len of the aggregated regex
                            self.columns.insert(i - 1, {'name' : "Name",
                                                        'regex' : "(.{," + str(lenColResult) + "})",
                                                        'selectedType' : aType,
                                                        'tabulation' : 0,
                                                        'description' : "",
                                                        'color' : ""
                                                        })
            i += 1

        if res:
            self.slickRegex() # Try to loop until no more merges are done
            self.log.debug("The regex has been slicked")

        # TODO: relaunch the matrix step of getting the maxIJ to merge column/row
        # TODO: memorize old regex/align
        # TODO: adapt align

    #+---------------------------------------------- 
    #| findSizeFields:
    #|  try to find the size fields of each regex
    #+----------------------------------------------    
    def findSizeFields(self, store):
        if len(self.columns) == 0:
            return
        typer = TypeIdentifier.TypeIdentifier()
        iCol = 0
        # We cover each field for a potential size field
        for col in self.getColumns():
            if self.isRegexStatic(col['regex']): # Means the element is static, and we exclude it for performance issue
                iCol += 1
                continue
            cellsSize = self.getCellsByCol(iCol)
            j = 0
            # We cover each field and aggregate them for a potential payload
            while j < len(self.getColumns()):
                # Initialize the aggregate of messages from colJ to colK
                aggregateCellsData = []
                for l in range(len(cellsSize)):
                    aggregateCellsData.append( "" )

                # Fill the aggregate of messages and try to compare its length with the current expected length
                k = j
                while k < len(self.getColumns()):
                    if k != j:
                        for l in range(len(cellsSize)):
                            aggregateCellsData[l] += self.getCellsByCol(k)[l]

                    # We try to aggregate the successive right sub-parts of j if it's a static column (TODO: handle dynamic column / TODO: handle left subparts of the K column)
                    if self.isRegexStatic( self.getColumns()[j]['regex'] ):
                        lenJ = len(self.getColumns()[j]['regex'])
                        stop = 0
                    else:
                        lenJ = 2
                        stop = 0
                    for m in range(lenJ, stop, -2):
                        for n in [4, 0, 1]: # loop over different possible encoding of size field
                            res = True
                            for l in range(len(cellsSize)):
                                if self.isRegexStatic( self.getColumns()[j]['regex'] ):
                                    targetData = self.getColumns()[j]['regex'][lenJ - m:] + aggregateCellsData[l]
                                else:
                                    targetData = self.getCellsByCol(j)[l] + aggregateCellsData[l]

                                # Handle big and little endian for size field of 1, 2 and 4 octets length
                                rawMsgSize = typer.toBinary(cellsSize[l][:n*2])
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
                                if self.isRegexStatic( self.getColumns()[j]['regex'] ): # Means the regex j element is static and a sub-part is concerned
                                    store.append([self.id, iCol, n*2, j, lenJ-m, k, -1, "Group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")"])
                                    self.log.info("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")")
                                else:
                                    store.append([self.id, iCol, n*2, j, -1, k, -1, "Group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")"])
                                    self.log.info("In group " + self.name + " : found potential size field (col " + str(iCol) + "[:" + str(n*2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")")
                                break
                    k += 1
                j += 1
            iCol += 1

    #+---------------------------------------------- 
    #| dataCarving:
    #|  try to find the size fields of each regex
    #+----------------------------------------------    
    def dataCarving(self, store):
        self.log.info("Not yet implemented, stay tuned")
        if len(self.columns) == 0:
            return

    #+---------------------------------------------- 
    #| concatColumns:
    #|  Concatenate two columns starting from iCol
    #+----------------------------------------------
    def concatColumns(self, iCol):
        col1 = self.getColumns().pop(iCol)
        col2 = self.getColumns().pop(iCol)

        # Build the merged regex
        newRegex = ""
        if col1['regex'] == "":
            newRegex = col2['regex']
        if col2['regex'] == "":
            newRegex = col1['regex']

        if col1['regex'][0] == "(" and col2['regex'][0] != "(": # Dyn + Static fields
            newRegex = col1['regex'][:-1] + col2['regex'] + ")"

        if col1['regex'][0] != "(" and col2['regex'][0] == "(": # Static + Dyn fields
            newRegex = "(" + col1['regex'] + col2['regex'][1:]

        if col1['regex'][0] == "(" and col2['regex'][0] == "(": # Dyn + Dyn fields
            newRegex = col1['regex'][:-1] + col2['regex'][1:]

        if col1['regex'][0] != "(" and col2['regex'][0] != "(": # Static + Static fields (should not happen...)
            newRegex = col1['regex'] + col2['regex']

        # Use the default protocol type for representation
        configParser = ConfigurationParser.ConfigurationParser()
        valID = configParser.getInt("clustering", "protocol_type")
        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"

        self.getColumns().insert(iCol, {'name' : "Name",
                                        'regex' : newRegex,
                                        'selectedType' : aType,
                                        'tabulation' : 0,
                                        'description' : "",
                                        'color' : ""
                                        })

    #+---------------------------------------------- 
    #| splitColumn:
    #|  Split a column in two columns
    #|  return False if the split does not occure, else True
    #+----------------------------------------------
    def splitColumn(self, iCol, split_position):
        if not (split_position > 0):
            return False
        # Find the static/dynamic cols
        cells = self.getCellsByCol(iCol)
        ref1 = cells[0][:split_position]
        ref2 = cells[0][split_position:]
        isStatic1 = True
        isStatic2 = True
        lenDyn1 = len(cells[0][:split_position])
        lenDyn2 = len(cells[0][split_position:])
        for m in cells[1:]:
            if m[:split_position] != ref1:
                isStatic1 = False
                if len(m[:split_position]) > lenDyn1:
                    lenDyn1 = len(m[:split_position])
            if m[split_position:] != ref2:
                isStatic2 = False
                if len(m[split_position:]) > lenDyn2:
                    lenDyn2 = len(m[split_position:])

        # Build the new sub-regex
        if isStatic1:
            regex1 = ref1
        else:
            regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = ref2
        else:
            regex2 = "(.{," + str(lenDyn2) + "})"

        if regex1 == "":
            return False
        if regex2 == "":
            return False

        aType = self.getSelectedTypeByCol(iCol)
        aTab = self.getTabulationByCol(iCol)

        # Build the new regex and apply it
        self.getColumns().pop(iCol)
        self.getColumns().insert(iCol, {'name' : "Name",
                                        'regex' : regex1,
                                        'selectedType' : aType,
                                        'tabulation' : aTab,
                                        'description' : "",
                                        'color' : ""
                                        })
        self.getColumns().insert(iCol + 1, {'name' : "Name",
                                            'regex' : regex2,
                                            'selectedType' : aType,
                                            'tabulation' : aTab,
                                            'description' : "",
                                            'color' : ""
                                            })
        return True

    #+---------------------------------------------- 
    #| Type handling
    #+----------------------------------------------
    def setTypeForCols(self, aType):
        for col in self.getColumns():
            col['selectedType'] = aType

    def setTypeForCol(self, iCol, aType):
        if iCol>=0 and iCol<len(self.columns) :
            self.columns[iCol]['selectedType'] = aType
        else :
            self.log.warning("The type for the column "+str(iCol)+" is not defined ! ")

    def getSelectedTypeByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            return self.columns[iCol]['selectedType']
        else :
            self.log.warning("The type for the column "+str(iCol)+" is not defined ! ")
            return "binary"

    def getPossibleTypesByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            cells = self.getCellsByCol(iCol)
            typeIdentifier = TypeIdentifier.TypeIdentifier()        
            return typeIdentifier.getTypes( cells )
        else :
            self.log.warning("The possible types for the column "+str(iCol)+" are not defined ! ")
            return ["binary"]

    def getStyledPossibleTypesByCol(self, iCol):
        tmpTypes = self.getPossibleTypesByCol(iCol)
        for i in range(len(tmpTypes)):
            if tmpTypes[i] == self.getSelectedTypeByCol(iCol):
                tmpTypes[i] = "<span foreground=\"red\">" + self.getSelectedTypeByCol(iCol) + "</span>"
        return ", ".join(tmpTypes)

    def getRepresentation(self, raw, iCol) :
        type = self.getSelectedTypeByCol(iCol)
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

    #+---------------------------------------------- 
    #| Regex handling
    #+----------------------------------------------
    def refineRegexes(self):
        for iCol in range(len(self.getColumns())):
            tmpRegex = self.getRegexByCol(iCol)
            if self.isRegexStatic( tmpRegex ):
                continue
            elif self.isRegexOnlyDynamic( tmpRegex ):
                cells = self.getCellsByCol(iCol)
                min = 999999
                max = 0
                for cell in cells:
                    if len(cell) > max:
                        max = len(cell)
                    if len(cell) < min:
                        min = len(cell)
                self.setRegexByCol(iCol, "(.{"+str(min)+","+str(max)+"})")
            else:
                # TODO: handle complex regex
                continue

    def isRegexStatic(self, regex):
        if regex.find("{") == -1:
            return True
        else:
            return False

    def isRegexOnlyDynamic(self, regex):
        if re.match("\(\.\{,\d+\}\)", regex) != None:
            return True
        else:
            return False

    #+---------------------------------------------- 
    #| XML store/load handling
    #+----------------------------------------------    
    def storeInXmlConfig(self):
        # TODO: also store the following information : tabulation and selectedType
        log = logging.getLogger('netzob.Sequencing.MessageGroup.py')
        
        members = ""
        for message in self.getMessages() :
            members += str(message.getID())+";"
        
        xml  = "<group id=\""+str(self.getID())+"\" name=\""+self.getName()+"\" score=\""+str(self.getScore())+"\" members=\""+members+"\" alignment=\""+self.getAlignment()+"\">\n"
        
        xml += "\t<regex>\n"
        for col in self.getColumns():
            xml += "\t\t<re>"+col['regex']+"</re>\n"
        xml += "\t</regex>\n"
        
        
        xml += "\t<cols>\n"
        for col in self.getColumns() :
            xml += "\t\t<col>"+col['name']+"</col>\n"
        xml += "\t</cols>\n"
        xml += "</group>\n"
        return xml        
    
    @staticmethod
    def loadFromXmlConfig(xml, messages):
        # TODO: also load the following information : tabulation and selectedType
        self.columns = []
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
        for xmlRe in xmlRes :
            for node in xmlRe.childNodes:
                re = node.data.split()
            self.columns.append( {'regex' : "".join(re)} )
        
        xmlCols = xml.getElementsByTagName("col")
        iCol = 0
        for xmlCol in xmlCols :
            for node in xmlCol.childNodes:
                colName = node.data.split()
            self.columns[iCol]['name'] = "".join(colName)
            iCol += 1

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
#         group.setRegex(group.extractRegexFromAlignment(group.getAlignment()))
#        group.setColumnNames(colNames)
#        group.setRegex(regex)
        group.setScore(xml.attributes["score"].value)
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
    def getMessageByID(self, messageID):
        for message in self.getMessages():
            if str(message.getID()) == str(messageID):
                return message
        return None
    def getColumns(self):
        return self.columns
    def getCellsByCol(self, iCol):
        res = []
        for message in self.getMessages():
            messageTable = message.applyRegex()
            res.append( messageTable[iCol] )
        return res
    def getTabulationByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            return self.columns[iCol]['tabulation']
    def getRegexByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            return self.columns[iCol]['regex']
    def getDescriptionByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            return self.columns[iCol]['description']
    def getColorByCol(self, iCol):
        if iCol>=0 and iCol<len(self.columns) :
            return self.columns[iCol]['color']

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    def setMessages(self, messages): 
        self.messages = messages
    def setAlignment(self, alignment):
        self.alignment = alignment
    def setScore(self, score):
        self.score = score
    def setColumnNameByCol(self, iCol, name):
        if len(self.columns) > iCol:
            self.columns[iCol]['name'] = name
    def setColumns(self, columns):
        self.columns = columns
    def setTabulationByCol(self, iCol, n):
        if iCol>=0 and iCol<len(self.columns) :
            self.columns[iCol]['tabulation'] = int(n)
    def setDescriptionByCol(self, iCol, descr):
        if iCol>=0 and iCol<len(self.columns) :
            self.columns[iCol]['description'] = descr
    def setRegexByCol(self, iCol, regex):
        if iCol>=0 and iCol<len(self.columns) :
            self.columns[iCol]['regex'] = regex
    def setColorByCol(self, iCol, color):
        if iCol>=0 and iCol<len(self.columns) :
            self.columns[iCol]['color'] = color
