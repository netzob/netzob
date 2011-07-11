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
        if (self.group == None or len(self.group.getMessages())<1) or len(self.group.getRegex()) == 0 :
            self.error()
            return
        
        # configuration of the representation format
        # default = binary
        for i in range(0, len(self.group.getRegex())) :
            self.selectedType.append("binary")
        
        # Create a TreeStore with N cols, with N := len(self.group.getRegex())
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for i in range( len(self.group.getRegex()) ):
            treeStoreTypes.append(str)           
        self.treestore = gtk.TreeStore(*treeStoreTypes)

        compiledRegex = re.compile("".join( self.group.getRegex() ))

        self.msgByCol = {}

        # Apply the content matrix to the treestore
        for i in range(0, len(self.group.getMessages())) :
            message = self.group.getMessages()[i]

            # for each message we create a line and computes its cols
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)

            # We apply the regex to the message
            data = message.getStringData()                    
            m = compiledRegex.match(data)

            # If the regex doesn't match the message, we activate the error mode
            if (m == None) :
                self.log.warning("The regex of the group doesn't match the message : " + data)
                self.error()
                return 
            
            iCol = 0
            dynamicCol = 1
            for regexElt in self.group.getRegex():
                # (init) Aggregate the cells content to a structure dedicacted to identify the column type
                if not iCol in self.msgByCol:
                    self.msgByCol[iCol] = []

                # Append styled data to the treestore
                if regexElt.find("(") != -1: # Means this column is not static
                    start = m.start(dynamicCol)
                    end = m.end(dynamicCol)
                    line.append('<span foreground="blue" font_family="monospace">' + self.getRepresentation( data[start:end], iCol ) + '</span>')
                    self.msgByCol[iCol].append( data[start:end] )
                    dynamicCol += 1
                else:
                    line.append('<span font_family="monospace">' + self.getRepresentation( regexElt, iCol ) + '</span>')
                    self.msgByCol[iCol].append( regexElt )

                iCol = iCol + 1
            self.treestore.append(None, line)
        
        # Creates the header (a line with the type displayed)
        header_line = []
        header_line.append("HEADER TYPE")
        header_line.append("#DEDEDE")
        header_line.append(pango.WEIGHT_BOLD)
        header_line.append(True)        

        # Get the possible types of each column
        for iCol in range( len(self.group.getRegex()) ):
            header_line.append(", ".join(self.getAllDiscoveredTypes(iCol)))
        self.treestore.prepend(None, header_line)

        # Creates the header line for the regex
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)

        # Get the Sub-Regex of each column
        for iCol in range( len(self.group.getRegex()) ):
            # Split the regex (this is scrapy...)
            tmpRegex = self.group.getRegex()[iCol]
            if len(tmpRegex) > 0 and tmpRegex[0] == "(": # Means a complex regex (static + dyn)
                tmpRegex = tmpRegex[1:-1] # We exclude the parenthesis

            splittedRegex = re.findall('(,?[0-9a-f]+)', self.group.getRegex()[iCol])

            resRegex = ""
            for elt in splittedRegex:
                if elt[0] == ",":
                    resRegex += ".{" + elt + "}"
                else:
                    resRegex += self.getRepresentation( elt, iCol )
            regex_row.append( resRegex )
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

        for i in range(4, 4 + len(self.group.getRegex()) ) :
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

    def getAllDiscoveredTypes(self, iCol):
        typeIdentifier = TypeIdentifier.TypeIdentifier()        
        return typeIdentifier.getTypes(self.msgByCol[iCol])
    
    def setTypeForCol(self, iCol, aType):
        self.selectedType[iCol] = aType
        
    def updateDefault(self):
        self.default(self.group)
    
    
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll_lib

    def getGroup(self):
        return self.group
