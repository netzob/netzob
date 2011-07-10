#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
import re
import pango
import gobject
import gtk
from numpy.core.numeric import zeros

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ...Common import ConfigurationParser
from ...Common import TypeIdentifier
from ..Message import Message
from ..NeedlemanWunsch import NeedlemanWunsch

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TreeMessageGenerator :
#|     update and generates the treeview and its 
#|     treestore dedicated to the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeMessageGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param vbox : where the treeview will be hold
    #+---------------------------------------------- 
    def __init__(self, vbox):
        self.vbox = vbox
        self.content = None
        self.selectedType = []
        self.msgByCol = {}
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TreeStores.TreeMessageGenerator.py')
        
   
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------     
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(str, str, str)     
        # creation of the treeview   
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        self.cell = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn('Messages')
        self.column.pack_start(self.cell, True)
        self.column.set_attributes(self.cell, text=0)
        self.column.set_attributes(self.cell, markup=0)
        self.treeview.append_column(self.column)
        
        self.treeview.show()
        
        self.scroll_lib = gtk.ScrolledWindow()
        self.scroll_lib.set_size_request(1000, 500)
        self.scroll_lib.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll_lib.add(self.treeview)
        self.scroll_lib.show()
        
    #+---------------------------------------------- 
    #| error :
    #|         Update the treestore in error mode
    #+---------------------------------------------- 
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")      
        self.treestore.clear()
        
    
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self, group):
        self.group = group
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the group "+self.group.getName())        
        self.treestore.clear()
        
        # Verifies we have everything needed for the creation of the treeview
        if (self.group == None or len(self.group.getMessages())<1) or len(self.group.getRegex())==0 :
            self.error()
            return
        
        # Computes the content matrix
        (self.content, numberOfGroups) = self.computeContent()
        
        # configuration of the representation format
        # default = binary
        for i in range(0, 2*numberOfGroups+1) :
            self.selectedType.append("binary")
        
        # Create a TreeStore with N cols, with := (maxNumberOfGroup * 2 + 1)
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for i in range(2*numberOfGroups+1):
            treeStoreTypes.append(str)
            
        self.treestore = gtk.TreeStore(*treeStoreTypes)
        
        # Create the content of the treestore
        for i in range(0, len(self.group.getMessages())) :
            message = self.group.getMessages()[i]
            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            
            c=0
            data = message.getStringData()
            current = 0
            while c<numberOfGroups*2 :
                start = self.content[i][c]
                rawContent1 = data[current:start]                
                if not c in self.msgByCol:
                    self.msgByCol[c] = []
                self.msgByCol[c].append(rawContent1)               
                content1 = self.getRepresentation(rawContent1, c)
                c = c+1
                
                
                end = self.content[i][c]
                rawContent2 = data[start:end]
                if not c in self.msgByCol:
                    self.msgByCol[c] = []
                self.msgByCol[c].append(rawContent2)
                content2 = self.getRepresentation(rawContent2, c)
                c = c+1
                              
                                    
                line.append('<span font_family="monospace">' + content1 + '</span>')
                line.append('<span foreground="blue" font_family="monospace">' + content2 + '</span>')                
                current = end
                
                
            if not c in self.msgByCol:
                self.msgByCol[c] = []
            self.msgByCol[c].append( data[current:] )
            
            print self.msgByCol
            
            
            line.append('<span font_family="monospace">' + self.getRepresentation(data[current:],c) + '</span>')     
            self.treestore.append(None, line)
        
        
        # Creates the header (a line with the type displayed)
        header_line = []
        header_line.append("HEADER TYPE")
        header_line.append("#DEDEDE")
        header_line.append(pango.WEIGHT_BOLD)
        header_line.append(True)        
        for i in range( numberOfGroups*2 +1):
            header_line.append(", ".join(self.getAllDiscoveredTypes(i)))
            
        self.treestore.prepend(None, header_line)
        
        
        # Creates the header line for the regex
        splittedRegex = re.findall("(\(\.\{\d*,\d*\}\))", self.group.getRegex())

        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)

        for i in range(len(splittedRegex)):
            regex_row.append("")
            # Get the Regex of the current column
            regex_row.append(splittedRegex[i][1:-1])
            
        for i in range((numberOfGroups * 2 + 1 + 4) - len(regex_row)):
            regex_row.append("")
            
        self.treestore.prepend(None, regex_row)
        
        
        
                 
        # Updates the treeview with the newly created treestore
        self.treeview.set_model(self.treestore)
        self.treeview.set_reorderable(True)

        # Remove all the columns of the current treeview
        for col in self.treeview.get_columns() :
            self.treeview.remove_column(col)
            
        # Define cellRenderer objects
        self.textCellRenderer = gtk.CellRendererText()
        self.textCellRenderer.set_property('background-set' , True)

        for i in range(4, 4 + (2*numberOfGroups +1)) :
            # Column Messages
            self.lvcolumnDetail2 = gtk.TreeViewColumn('Col'+str(i-4))
            self.lvcolumnDetail2.pack_start(self.textCellRenderer, True)
            self.lvcolumnDetail2.set_attributes(self.textCellRenderer, markup=i, background=1, weight=2, editable=3)
            self.treeview.append_column(self.lvcolumnDetail2)
            
        
            

    def getRepresentation(self, raw, colId) :
        type = self.getSelectedType(colId)
        return self.encode(raw, type)
    
    def getSelectedType(self, colId):
        if colId>=0 and colId<len(self.selectedType) :
            return self.selectedType[colId]
        else :
            self.log.warning("The type for the column "+str(colId)+" is not defined ! ")
            return "binary"
    
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
     
    
    def computeContent(self):
        
        # Compile the regex (in order to prepare to the identification of groups in the messages)
        compiledRegex = re.compile(self.group.getRegex())
        
        # the maximum number of groups per message (eq. the nb of displayed cols)
        numberOfGroup = -1
        
        # create a table which contains all the cols and lines of the treestore
        maxNumberOfCols = 40
        content = zeros([len(self.group.getMessages()), maxNumberOfCols*2], int)
        i_message = 0        
        # Apply the regex to each message in order to comptagramute the groups
        # Full fill the content array
        for message in self.group.getMessages() :
            
            # Apply the group regex's to the current message
            data = message.getStringData()                    
            m = compiledRegex.match(data)
            
            # If the regex doesn't match one of the message, we activate the error mode
            if (m == None) :
                self.log.warning("The regex of the group doesn't match one of its message ! ("+data+")")
                self.error()
                return 
            
            # compute the number of group in this message in order to compute the maximum
            if numberOfGroup < len(m.groups()) :
                numberOfGroup = len(m.groups())
                
            # retrieves all the groups of the regex
            start = 0
            end = 0
            k = 0
            
            for i_group in range(1, len(m.groups())+1) :
                start = m.start(i_group)
                end = m.end(i_group)
                content[i_message][k]=start
                k = k+1
                content[i_message][k]=end
                k = k+1
            
            i_message = i_message + 1
            
        return (content, numberOfGroup)
        
    
    def getAllDiscoveredTypes(self, iCol):
        typeIdentifier = TypeIdentifier.TypeIdentifier()        
        return typeIdentifier.getTypes(self.msgByCol[iCol])
    
    def setTypeForCol(self, iCol, type):
        self.selectedType[iCol]=type
        
    def updateDefault(self):
        self.default(self.group)
    
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll_lib
    
