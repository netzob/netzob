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
import logging
import re
import struct
import gtk
import glib

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
#| Group :
#|     definition of a group of messages
#| all the messages in the same group must be 
#| considered as equivalent
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Group(object):
    
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
        self.log = logging.getLogger('netzob.Modelization.Group.py')
        self.id = uuid.uuid4() 
        self.name = name
        self.messages = messages
        for message in self.messages:
            message.setGroup(self)
        self.score = 0
        self.alignment = ""
        self.columns = [] # each column element contains a dict : {'name', 'regex', 'selectedType', 'tabulation', 'description', 'color'}

        ## TODO: put this things in a dedicated class
        self.carvers = {
            'url' : re.compile("((http:\/\/|https:\/\/)?(www\.)?(([a-zA-Z0-9\-]){2,}\.){1,4}([a-zA-Z]){2,6}(\/([a-zA-Z\-_\/\.0-9#:?+%=&;,])*)?)"),
            'email' : re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"),
            'ip' : re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
            }

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
                if len(self.columns[i]['regex']) == 2: # Means a potential negligeable element that can be merged with its neighbours
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
    #|  try to find semantic elements in each field
    #+----------------------------------------------    
    def dataCarving(self):
        if len(self.columns) == 0:
            return None

        vbox = gtk.VBox(False, spacing=5)
        vbox.show()
        hbox = gtk.HPaned()
        hbox.show()
        # Treeview containing potential data carving results ## ListStore format :
        # int: iCol
        # str: data type (url, ip, email, etc.)
        store = gtk.ListStore(int, str)
        treeviewRes = gtk.TreeView(store)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Column')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewRes.append_column(column)
        column = gtk.TreeViewColumn('Data type found')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewRes.append_column(column)
        treeviewRes.set_size_request(200, 300)
        treeviewRes.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeviewRes)
        hbox.add(scroll)

        ## Algo : for each column, and then for each cell, try to carve data
        typer = TypeIdentifier.TypeIdentifier()
        iCol = 0
        for col in self.getColumns():
            for (carver, regex) in self.carvers.items():
                matchElts = 0
                for cell in self.getCellsByCol(iCol):
                    for match in regex.finditer(typer.toASCII(cell)):
                        matchElts += 1
                if matchElts > 0:
                    store.append([iCol, carver])
            iCol += 1

        # Preview of matching fields in a treeview ## ListStore format :
        # str: data
        treeview = gtk.TreeView(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, markup=0)
        treeview.append_column(column)
        treeview.set_size_request(700, 300)
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        hbox.add(scroll)
        vbox.pack_start(hbox, True, True, 0)

        # Apply button
        but = gtk.Button(label="Apply data type on column")
        but.show()
        self.butDataCarvingHandle = None
        treeviewRes.connect("cursor-changed", self.dataCarvingResultSelected_cb, treeview, but)
        vbox.pack_start(but, False, False, 0)

        return vbox
        # TODO : use hachoir to retrieve subfiles
        #    lines = os.popen("/usr/bin/hachoir-subfile " + target).readline()

    #+---------------------------------------------- 
    #| dataCarvingResultSelected_cb:
    #|  Callback when clicking on a data carving result.
    #|  It shows a preview of the carved data
    #+----------------------------------------------
    def dataCarvingResultSelected_cb(self, treeview, treeviewTarget, but):
        typer = TypeIdentifier.TypeIdentifier()
        treeviewTarget.get_model().clear()
        (model, it) = treeview.get_selection().get_selected()
        if(it):
            if(model.iter_is_valid(it)):
                iCol = model.get_value(it, 0)
                dataType = model.get_value(it, 1)
                treeviewTarget.get_column(0).set_title("Column " + str(iCol))
                if self.butDataCarvingHandle != None:
                    but.disconnect(self.butDataCarvingHandle)
                self.butDataCarvingHandle = but.connect("clicked", self.applyDataType_cb, iCol, dataType)
                for cell in self.getCellsByCol(iCol):
                    cell = glib.markup_escape_text( typer.toASCII(cell) )
                    segments = []
                    for match in self.carvers[dataType].finditer(cell):
                        if match == None:
                            treeviewTarget.get_model().append([ cell ])
                        segments.append( (match.start(0), match.end(0)) )

                    segments.reverse() # We start from the end to avoid shifting
                    for (start, end) in segments:
                        cell = cell[:end] + "</span>" + cell[end:]
                        cell = cell[:start] + '<span foreground="red" font_family="monospace">' + cell[start:]
                    treeviewTarget.get_model().append([ cell ])

    #+---------------------------------------------- 
    #| applyDataType_cb:
    #|  Called when user wants to apply a data type to a field
    #+----------------------------------------------
    def applyDataType_cb(self, button, iCol, dataType):
        self.setDescriptionByCol(iCol, dataType)

    #+---------------------------------------------- 
    #| search:
    #|  search a specific data in messages
    #+----------------------------------------------    
    def search(self, data):
        if len(self.columns) == 0:
            return None

        # Retrieve the raw data ('abcdef0123') from data
        rawData = data.encode("hex")
        hbox = gtk.HPaned()
        hbox.show()
        # Treeview containing potential data carving results ## ListStore format :
        # int: iCol
        # str: encoding
        store = gtk.ListStore(int, str)
        treeviewRes = gtk.TreeView(store)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Column')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewRes.append_column(column)
        column = gtk.TreeViewColumn('Encoding')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewRes.append_column(column)
        treeviewRes.set_size_request(200, 300)
        treeviewRes.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeviewRes)
        hbox.add(scroll)

        ## Algo (first step) : for each column, and then for each cell, try to find data
        iCol = 0
        for col in self.getColumns():
            matchASCII = 0
            matchBinary = 0
            for cell in self.getCellsByCol(iCol):
                matchASCII += cell.count(rawData)
                matchBinary += cell.count(data)
            if matchASCII > 0:
                store.append([iCol, "ASCII"])
            if matchBinary > 0:
                store.append([iCol, "binary"])
            iCol += 1

        ## TODO: Algo (second step) : for each message, try to find data

        # Preview of matching fields in a treeview ## ListStore format :
        # str: data
        treeview = gtk.TreeView(gtk.ListStore(str))
        treeviewRes.connect("cursor-changed", self.searchResultSelected_cb, treeview, data)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, markup=0)
        treeview.append_column(column)
        treeview.set_size_request(700, 300)
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        hbox.add(scroll)
        return hbox

    #+---------------------------------------------- 
    #| searchResultSelected_cb:
    #|  Callback when clicking on a search result.
    #|  It shows a preview of the finding
    #+----------------------------------------------
    def searchResultSelected_cb(self, treeview, treeviewTarget, data):
        typer = TypeIdentifier.TypeIdentifier()
        treeviewTarget.get_model().clear()
        (model, it) = treeview.get_selection().get_selected()
        if(it):
            if(model.iter_is_valid(it)):
                iCol = model.get_value(it, 0)
                encoding = model.get_value(it, 1)
                treeviewTarget.get_column(0).set_title("Column " + str(iCol))
                for cell in self.getCellsByCol(iCol):
                    if encoding == "ASCII":
                        cell = typer.toASCII(cell)
                        arrayCell = cell.split(data)
                    elif encoding == "binary":
                        arrayCell = cell.split(data)
                    arrayCell = [ glib.markup_escape_text(a) for a in arrayCell ]
                    if len(arrayCell) > 1:
                        styledCell = str("<span foreground=\"red\" font_family=\"monospace\">" + data + "</span>").join(arrayCell)
                    else:
                        styledCell = cell
                    treeviewTarget.get_model().append([ styledCell ])

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
        aType = self.getSelectedTypeByCol(iCol)
        return self.encode(raw, aType)
    
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
                if min == max:
                    self.setRegexByCol(iCol, "(.{"+str(min)+"})")
                else:
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
        if re.match("\(\.\{\d?,\d+\}\)", regex) != None:
            return True
        else:
            return False

    #+---------------------------------------------- 
    #| XML store/load handling
    #+----------------------------------------------    
    def storeInXmlConfig(self):
        log = logging.getLogger('netzob.Modelization.Group.py')

        members = ""
        for message in self.getMessages() :
            members += str(message.getID())+";"
        
        xml  = "<group id=\""+str(self.getID())+"\" name=\""+self.getName()+"\" score=\""+str(self.getScore())+"\" members=\""+members+"\" alignment=\""+self.getAlignment()+"\">\n"

        xml += "\t<colsName>\n"
        for col in self.getColumns() :
            xml += "\t\t<name>"+col['name']+"</name>\n"
        xml += "\t</colsName>\n"
        
        xml += "\t<colsRegex>\n"
        for col in self.getColumns():
            xml += "\t\t<regex>"+col['regex']+"</regex>\n"
        xml += "\t</colsRegex>\n"
                
        xml += "\t<colsSelectedType>\n"
        for col in self.getColumns() :
            xml += "\t\t<selectedType>"+col['selectedType']+"</selectedType>\n"
        xml += "\t</colsSelectedType>\n"

        xml += "\t<colsTabulation>\n"
        for col in self.getColumns():
            xml += "\t\t<tabulation>"+str(col['tabulation'])+"</tabulation>\n"
        xml += "\t</colsTabulation>\n"

        xml += "\t<colsDescription>\n"
        for col in self.getColumns():
            xml += "\t\t<description>"+col['description']+"</description>\n"
        xml += "\t</colsDescription>\n"

        xml += "\t<colsColor>\n"
        for col in self.getColumns():
            xml += "\t\t<color>"+col['color']+"</color>\n"
        xml += "\t</colsColor>\n"

        xml += "</group>\n"
        return xml
    
    @staticmethod
    def loadFromXmlConfig(xml, messages):
        columns = []
        log = logging.getLogger('netzob.Modelization.Group.py')
        
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
        
        xmlCols = xml.getElementsByTagName("regex")
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns.append( {'regex' : "".join(data)} )
        
        xmlCols = xml.getElementsByTagName("name")
        iCol = 0
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns[iCol]['name'] = "".join(data)
            iCol += 1

        xmlCols = xml.getElementsByTagName("selectedType")
        iCol = 0
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns[iCol]['selectedType'] = "".join(data)
            iCol += 1

        xmlCols = xml.getElementsByTagName("tabulation")
        iCol = 0
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns[iCol]['tabulation'] = int("".join(data))
            iCol += 1

        xmlCols = xml.getElementsByTagName("description")
        iCol = 0
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns[iCol]['description'] = "".join(data)
            iCol += 1

        xmlCols = xml.getElementsByTagName("color")
        iCol = 0
        for xmlCol in xmlCols :
            data = ""
            for node in xmlCol.childNodes:
                data = node.data.split()
            columns[iCol]['color'] = "".join(data)
            iCol += 1

        group = Group(xml.attributes["name"].value, [])    
        
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
        group.setColumns(columns)
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
